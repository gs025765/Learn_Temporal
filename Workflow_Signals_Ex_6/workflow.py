import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activity import run_ocr_activity
    from data_model import ImageInput, OCRResult, MultiPageInput, MultiPageResult, JobStatus


@workflow.defn
class OCRWorkflow:
    _cancelled:bool = False
    _completed_pages:int=0
    _total_pages: int=0
    _job_id: str=""

    # ------SIGNAL HANDLER-------------
    # This method is called when someone sends a cancel job signal
    # It just flip the flag -- the workflow check flag b/w pages

    @workflow.signal
    async def cancel_job(self) -> None:
        print(f"[Workflow] Cancel signal recieved -- will stop after current page")
        self._cancelled =True

    # -------Query Handler -------------
    # This method is used when someone queries get_status
    # Must be synchronous -- cannot use await inside a query

    @workflow.query
    def get_status(self)->JobStatus:
        status ="cancelled" if self._cancelled else(
            "complete" if self._completed_pages == self._total_pages
            else "running"
        )
        return JobStatus(
            job_id=self._job_id,
            total_pages=self._total_pages,
            completed_pages=self._completed_pages,
            cancelled=self._cancelled,
            current_status=status
        )

    # -------Main Workflow--------------------------
    @workflow.run
    async def run(self, input: MultiPageInput) -> MultiPageResult:
        self._job_id = input.job_id
        self._total_pages = len(input.file_paths)

        print(f"[Workflow] Starting job: {input.job_id}")
        print(f"[Workflow] Total pages: {self._total_pages}")

        page_results = []

        # Process pages ONE BY ONE — so we can check cancel flag between each
        for i, file_path in enumerate(input.file_paths):

            # Check cancel flag before starting each page
            if self._cancelled:
                print(f"[Workflow] Cancelled — stopping at page {i + 1}")
                break

            print(f"[Workflow] Starting page {i + 1} of {self._total_pages}")

            result = await workflow.execute_activity(
                run_ocr_activity,
                ImageInput(file_path=file_path, page_number=i + 1),
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_attempts=3,
                )
            )

            page_results.append(result)
            self._completed_pages += 1
            print(f"[Workflow] Page {i + 1} complete — {self._completed_pages}/{self._total_pages} done")

        successful = sum(1 for r in page_results if r.status == "success")
        failed = sum(1 for r in page_results if r.status == "failed")

        final_status = "cancelled" if self._cancelled else "complete"
        print(f"[Workflow] Job {final_status} — {successful} pages processed")

        return MultiPageResult(
            job_id=input.job_id,
            pages=page_results,
            total_pages=self._total_pages,
            successful_pages=successful,
            failed_pages=failed,
        )



