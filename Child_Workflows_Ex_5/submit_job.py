import asyncio
from temporalio.client import Client
from data_model import MultiPageInput
from workflow import OCRWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    handle = await client.start_workflow(
        OCRWorkflow,
        MultiPageInput(
            file_paths=["../MultiPage_OCR_Ex_4/Data/page_1.txt", "../MultiPage_OCR_Ex_4/Data/page_2.txt", "../MultiPage_OCR_Ex_4/Data/page_3.txt"],
            job_id="invoice-batch-ex6"
        ),
        id="ocr-workflow-ex6",
        task_queue="ocr-task-queue",
    )

    print(f"[Client] Job submitted: {handle.id}")
    result = await handle.result()

    print(f"\n[Result] Job: {result.job_id}")
    print(f"  Total pages : {result.total_pages}")
    print(f"  Successful  : {result.successful_pages}")
    print(f"  Failed      : {result.failed_pages}")
    print(f"\n  Page details:")
    for page in result.pages:
        print(f"    Page {page.page_number} [{page.status}] → {page.text}")


if __name__ == "__main__":
    asyncio.run(main())