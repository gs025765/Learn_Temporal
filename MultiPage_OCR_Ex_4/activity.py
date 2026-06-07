from temporalio import activity
from temporalio.exceptions import ApplicationError
from data_model import ImageInput, OCRResult


@activity.defn
async def run_ocr(input:ImageInput)->OCRResult:
    print(f"[Activity] Processing page number {input.page_number}: {input.file_path}")

    try:
        with open(input.file_path,"r") as f:
            content = f.read().strip()

        confidence = 0.95 if len(content) >0 else 0.0
        print(f"[Activity] page {input.page_number} done")

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