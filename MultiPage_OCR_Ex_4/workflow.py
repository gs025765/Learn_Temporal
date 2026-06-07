import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activity import run_ocr
    from data_model import ImageInput, OCRResult, MultiPageInput,MultiPageResult

@workflow.defn
class OCRWorkflow:

    @workflow.run
    async def run(self, input:MultiPageInput) ->MultiPageResult:
        print(f"[Workflow] Starting job: {input.job_id}")
        print(f"[Workflow] Pages to process: {len(input.file_path)}")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )
        tasks = [
            workflow.execute_activity(
                run_ocr,
                ImageInput(file_path=path,page_number=i+1),
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )
            for i, path in enumerate(input.file_path)
        ]
        #Fire all pages Simultaneously
        print(f"[Workflow] Firing {len(tasks)} pages in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        #Collect results - handle any page that failed
        page_results = []
        for i, result in enumerate(results):
            if isinstance(result,Exception):
                page_results.append(OCRResult(
                    page_number=i+1,
                    text="",
                    confidence=0.0,
                    status="failed",
                    error_message=str(result)
                ))
            else:
                page_results.append(result)
            
        successful = sum(1 for r in page_results if r.status =="success")
        failed = sum(1 for r in page_results if r.status=="failed")
        
        print(f"[Workflow] Complete - {successful} succeeded, {failed} failed")

        return MultiPageResult(
            job_id = input.job_id,
            pages = page_results,
            total_pages = len(page_results),
            successful_pages=successful,
            failed_pages=failed,
        )