from temporalio import activity
from data_model import ImageInput, ImageOutput


@activity.defn
async def ocr_output(input:ImageInput)->ImageOutput:
    activity.logger.info(f"Processing file : {input.file_path}, page_number : {input.page_number}")
    try:
        with open(input.file_path,"r") as f:
            content = f.read().strip()
        
        confidence = str(0.95 if len(content)>0 else 0.0)

        print(f"Activity file processed successfully: {content}")

        return ImageOutput(
            page_number=input.page_number,
            text=content,
            confidence=confidence,
            status="success"
        )
    except FileNotFoundError:
        print(f"[Activity] File not found: {input.file_path}")
        return ImageOutput(
            page_number=input.page_number,
            text="",
            confidence=0.0,
            status="failed",
            error_message=f"File not found: {input.file_path}"
        )