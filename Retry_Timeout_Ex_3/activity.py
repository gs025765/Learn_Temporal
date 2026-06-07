import random
from temporalio import activity
from temporalio.exceptions import ApplicationError
from data_model import ImageInput, OCRResults

attempt_counter = {"count":0}

@activity.defn
async def run_ocr_activity(input:ImageInput)->OCRResults:
    attempt_counter["count"]+=1
    current_attempt = attempt_counter["count"]
    activity.logger.info(
        f"Attempt #{current_attempt} for file: {input.file_path}"
    )
    print(f"[Activity] Attempt #{current_attempt} - file: {input.file_path}")

    #Simulate Triton being flaky for first 3 attempts
    if current_attempt <=3:
        print(f"[Activity] Triton server unavailable -attempt {current_attempt} failed")
        raise ApplicationError(
            f"Triton unavailable on attempt {current_attempt}",
            non_retryable=False # False means temporal will retry this
        )
    # 4th attempt
    try:
        with open(input.file_path,"r") as f:
            content =f.read().strip()
        
        confidence = 0.95 if len(content)>0 else 0.0
        print(f"[Activity] Success on attempt {current_attempt} : {content}")
        return OCRResults(
            page_number=input.page_number,
            text = content,
            confidence=confidence,
            status="sucess",)
    except FileNotFoundError:
        raise ApplicationError(
            f"File not found: {input.file_path}",
            non_retryable=True # True means Temporal will not retry
        )        