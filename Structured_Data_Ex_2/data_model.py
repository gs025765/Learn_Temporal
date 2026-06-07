from dataclasses import dataclass

@dataclass
class ImageInput:
    file_path:str
    page_number:str

@dataclass
class ImageOutput:
    page_number: str
    text: str
    confidence: str
    status: str
    error_msg: str=" "