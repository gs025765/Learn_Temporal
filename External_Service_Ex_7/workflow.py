import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activity import run_ocr_activity
    from data_model import ImageInput, OCRResult, MultiPageInput, MultiPageResult, JobStatus


@workflow.defn
class OCRWorkflow:

    _cancelled: bool = False
    _completed_pages: int = 0
    _total_pages: int = 0
    _job_id: str = ""

    @workflow.signal
    async def cancel_job(self) -> None:
        print(f"[Workflow] Cancel signal received")
        self._cancelled = True

    @workflow.query
    def get_status(self) -> JobStatus:
        status = "cancelled" if self._cancelled else (
            "complete" if self._completed_pages == self._total_pages and self._total_pages > 0
            else "running"
        )
        return JobStatus(
            job_id=self._job_id,
            total_pages=self._total_pages,
            completed_pages=self._completed_pages,
            cancelled=self._cancelled,
            current_status=status
        )

    @workflow.run
    async def run(self, input: MultiPageInput) -> MultiPageResult:
        self._job_id = input.job_id
        self._total_pages = len(input.file_paths)

        print(f"[Workflow] Starting job: {input.job_id}")
        page_results = []

        for i, file_path in enumerate(input.file_paths):

            if self._cancelled:
                print(f"[Workflow] Cancelled at page {i + 1}")
                break

            result = await workflow.execute_activity(
                run_ocr_activity,
                ImageInput(file_path=file_path, page_number=i + 1),
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2.0,
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=5,   # 5 attempts — Triton may 503 a few times
                )
            )

            page_results.append(result)
            self._completed_pages += 1

        successful = sum(1 for r in page_results if r.status == "success")
        failed = sum(1 for r in page_results if r.status == "failed")

        return MultiPageResult(
            job_id=input.job_id,
            pages=page_results,
            total_pages=self._total_pages,
            successful_pages=successful,
            failed_pages=failed,
        )