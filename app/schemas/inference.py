# app/schemas/inference.py
from pydantic import BaseModel

class InferenceRequest(BaseModel):
    model_name: str ="sentiment"
    input_text: str

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "sentiment",
                "input_text": "The movie was fantastic!"
            }
        }

class InferenceResponse(BaseModel):
    label: str
    score: float
