import asyncio
from temporalio.client import Client
from data_model import MultiPageInput
from workflow import OCRWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    handle = await client.start_workflow(
        OCRWorkflow,
        MultiPageInput(
            file_paths=[
                "./Data/page_1.txt", "./Data/page_2.txt", "./Data/page_3.txt",
                "./Data/page_4.txt", "./Data/page_5.txt"
            ],
            job_id="invoice-ex7"
        ),
        id="ocr-workflow-ex7",
        task_queue="ocr-task-queue",
    )

    print(f"[Client] Job submitted: {handle.id}")
    print(f"[Client] Waiting for result — send signals from another tab...")

    result = await handle.result()

    print(f"\n[Final Result]")
    print(f"  Job ID      : {result.job_id}")
    print(f"  Total pages : {result.total_pages}")
    print(f"  Successful  : {result.successful_pages}")
    print(f"  Pages done  :")
    for page in result.pages:
        print(f"    Page {page.page_number} [{page.status}] → {page.text}")


if __name__ == "__main__":
    asyncio.run(main())