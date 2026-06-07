import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activity import run_ocr_activity
    from data_model import ImageInput, OCRResult, MultiPageInput, MultiPageResult


# ------------Child Workflow -------------
# Handles exactly ONE Page
# Has its own event history,Its own retries


@workflow.defn
class PageWorkflow:

    @workflow.run
    async def run (self, input:ImageInput)->OCRResult:
        print(f"[ChildWorkflow] Starting page {input.page_number}")
        
        result = await workflow.execute_activity(
            run_ocr_activity,
            input,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                maximum_attempts=3,
            )
        )
        print(f"[ChildWorkflow] Page {input.page_number} completed")

        return result

#-------Parent Workflow-----
# Spawns one workflow per page
# Waits for all children to complete then assembles final result

@workflow.defn
class OCRWorkflow:
    @workflow.run
    async def run(self, input: MultiPageInput)-> MultiPageResult:
        print(f"[ParentWorkflow] Starting Job: {input.job_id}")
        print(f"[ParentWorkflow] Spawing {len(input.file_paths)} child workflows")

        # Spawn one child workflow per page
        # Each child gets a unique id - job_id + page number

        child_tasks = [
            workflow.execute_child_workflow(
                PageWorkflow.run,
                ImageInput(file_path=path,page_number=i+1),
                id=f"{input.job_id}_page_{i+1}",
            )
            for i,path in enumerate(input.file_paths)
        ]
        # Wait for the childrens
        print(f"[ParentWorkflow] waiting for all the children....")
        results = await asyncio.gather(*child_tasks,return_exceptions=True)

        # Assemble Results
        page_results=[]

        for i,result in enumerate(results):
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

        successful = sum(1 for r in page_results if r.status == "success")
        failed = sum(1 for r in page_results if r.status == "failed")
        print(f"[ParentWorkflow] All done — {successful} succeeded, {failed} failed")

        return MultiPageResult(
            job_id=input.job_id,
            pages=page_results,
            total_pages=len(page_results),
            successful_pages=successful,
            failed_pages=failed,
        )