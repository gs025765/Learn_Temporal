from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activity import ocr_output
    from data_model import ImageInput, ImageOutput


@workflow.defn
class OCRWorkflow:
    @workflow.run
    async def run(self, input: ImageInput)->ImageOutput:
        print(f"[Workflow] Starting OCR job for : {input.file_path}")
        result = await workflow.execute_activity(
            ocr_output,
            input,
            start_to_close_timeout=timedelta(seconds=30),
        )
        print(f"[Workflow] OCR complete - status: {result.status}")
        return result