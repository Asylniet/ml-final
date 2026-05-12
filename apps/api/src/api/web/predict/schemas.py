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
<<<<<<< HEAD
    feature_values: dict[str, float]
    secondary_structure: "SecondaryStructureSchema | None" = None


class FeatureImportanceItem(BaseModel):
    name: str
    importance: float


class ModelStatsSchema(BaseModel):
    accuracy: float
    f1: float
    precision: float
    recall: float
    cv_score: float
    n_samples: int
    n_positive: int
    n_negative: int
    n_features: int
    model_type: str


class SecondaryStructureSchema(BaseModel):
    dot_bracket: str
    mfe: float
    svg: str
=======
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
