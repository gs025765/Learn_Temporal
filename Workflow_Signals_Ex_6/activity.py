import asyncio
from temporalio import activity
from temporalio.exceptions import ApplicationError
from data_model import ImageInput, OCRResult


@activity.defn
async def run_ocr_activity(input: ImageInput) -> OCRResult:
    print(f"[Activity] Processing page {input.page_number}: {input.file_path}")

    # Simulate Triton inference taking 2 seconds per page
    # This gives us time to send signals while job is running
    await asyncio.sleep(2)

    try:
        with open(input.file_path, "r") as f:
            content = f.read().strip()

        confidence = 0.95 if len(content) > 0 else 0.0
        print(f"[Activity] Page {input.page_number} done ✓")

        return OCRResult(
            page_number=input.page_number,
            text=content,
            confidence=confidence,
            status="success"
        )

    except FileNotFoundError:
        raise ApplicationError(
            f"File not found: {input.file_path}",
            non_retryable=True
        )