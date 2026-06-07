from dataclasses import dataclass, field
from typing import List


@dataclass
class ImageInput:
    file_path: str
    page_number: int


@dataclass
class OCRResult:
    page_number: int
    text: str
    confidence: float
    status: str
    error_message: str = ""


@dataclass
class MultiPageInput:
    file_paths: List[str]
    job_id: str


@dataclass
class MultiPageResult:
    job_id: str
    pages: List[OCRResult]
    total_pages: int
    successful_pages: int
    failed_pages: int


# NEW — returned when someone queries job status
@dataclass
class JobStatus:
    job_id: str
    total_pages: int
    completed_pages: int
    cancelled: bool
    current_status: str   # "running", "cancelled", "complete"