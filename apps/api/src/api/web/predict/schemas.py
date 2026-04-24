from pydantic import BaseModel, field_validator


class SequenceInputSchema(BaseModel):
    sequence: str

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v: str) -> str:
        clean = v.upper().replace("T", "U").strip()
        invalid = set(clean) - set("AUGC")
        if invalid:
            raise ValueError(f"Invalid nucleotides: {invalid}")
        if len(clean) < 10:
            raise ValueError("Sequence must be at least 10 nucleotides long")
        return clean


class PredictionResponseSchema(BaseModel):
    prediction: str
    is_mirna: bool
    confidence: float
    gc_content: float
    length: int
    sequence: str
