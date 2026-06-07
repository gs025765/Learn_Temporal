import httpx
from temporalio import activity
from temporalio.exceptions import ApplicationError
from data_model import ImageInput, OCRResult


@activity.defn
async def run_ocr_activity(input: ImageInput) -> OCRResult:
    activity.logger.info(f"Sending page {input.page_number} to Triton")
    print(f"[Activity] Calling Triton for page {input.page_number}: {input.file_path}")

    triton_url = "http://localhost:8080/v2/models/paddleocr/infer"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                triton_url,
                json={
                    "file_path": input.file_path,
                    "page_number": input.page_number,
                }
            )

        # ── Handle Triton response codes ──────────────────

        # 503 — server overloaded — retryable
        if response.status_code == 503:
            print(f"[Activity] Triton overloaded (503) — Temporal will retry")
            raise ApplicationError(
                "Triton server overloaded",
                non_retryable=False      # retry this
            )

        # 404 — file not found on Triton side — not retryable
        if response.status_code == 404:
            print(f"[Activity] File not found on Triton (404) — no retry")
            raise ApplicationError(
                f"File not found: {input.file_path}",
                non_retryable=True       # never retry this
            )

        # 500 — server error — retryable
        if response.status_code == 500:
            print(f"[Activity] Triton internal error (500) — Temporal will retry")
            raise ApplicationError(
                "Triton internal server error",
                non_retryable=False      # retry this
            )

        # 200 — success — parse response
        if response.status_code == 200:
            data = response.json()

            print(f"[Activity] Triton responded — page {data['page_number']} done ✓")
            print(f"[Activity] Inference time: {data['inference_time_ms']}ms")

            return OCRResult(
                page_number=data["page_number"],
                text=data["text"],
                confidence=data["confidence"],
                status="success"
            )

        # Unexpected status code
        raise ApplicationError(
            f"Unexpected Triton response: {response.status_code}",
            non_retryable=False
        )

    except httpx.ConnectError:
        # Triton server is completely down — retryable
        print(f"[Activity] Cannot connect to Triton — is it running?")
        raise ApplicationError(
            "Cannot connect to Triton server",
            non_retryable=False          # retry — server might come back up
        )

    except httpx.TimeoutException:
        # Triton took too long — retryable
        print(f"[Activity] Triton request timed out")
        raise ApplicationError(
            "Triton request timed out",
            non_retryable=False          # retry
        )