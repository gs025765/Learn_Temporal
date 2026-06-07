import asyncio
from temporalio.client import Client
from data_model import JobStatus


async def main():
    client = await Client.connect("localhost:7233")

    # Get handle to the already-running workflow by its id
    handle = client.get_workflow_handle("ocr-workflow-ex7")

    # Send a query — get current status back immediately
    status = await handle.query("get_status",result_type=JobStatus)

    print(f"\n[Query Result]")
    print(f"  Job ID          : {status.job_id}")
    print(f"  Status          : {status.current_status}")
    # print(f"  Pages completed : {status.completed_pages}/{status.total_pages}")
    print(f"  Cancelled       : {status.cancelled}")


if __name__ == "__main__":
    asyncio.run(main())