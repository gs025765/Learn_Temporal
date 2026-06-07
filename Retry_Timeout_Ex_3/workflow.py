from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activity import run_ocr_activity
    from data_model import ImageInput, OCRResults

@workflow.defn
class OCRWorkflow:

    @workflow.run
    async def run(self,input: ImageInput)->OCRResults:
        print(f"[Workflow] starting OCR job: {input.file_path}")
        result = await workflow.execute_activity(
            run_ocr_activity,
            input,
            # How long 1st attempt can take
            start_to_close_timeout=timedelta(seconds=30),
            # How long all attempts combined can take 
            schedule_to_close_timeout=timedelta(minutes=5),

            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),#Wait 1 second before 1st retry
                backoff_coefficient=2.0, #Double wait each Retry 1s,2s,4s
                maximum_interval=timedelta(seconds=30), # Never wait more then 30 Seconds
                maximum_attempts=5, # Give up after 5 total attempts
            )

        )
        print(f"[Workflow] Done -- Status : {result.status}, attempts used: up to 5")
        return result
