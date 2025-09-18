from pydantic import BaseModel
from typing import List, Union

class PromptRequest(BaseModel):
    prompt: str
    data: Union[List[List[Union[str, float]]], None] = None  # Optional Excel range

class PromptResponse(BaseModel):
    result: List[List[Union[str, float]]]  # 2D list suitable for Excel return
