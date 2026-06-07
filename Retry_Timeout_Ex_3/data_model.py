from dataclasses import dataclass 

@dataclass
class ImageInput:
    file_path:str
    page_number:int

@dataclass
class OCRResults:
    page_number:int
    text:str
    confidence:float
    status:str
    error_msg:str= " "