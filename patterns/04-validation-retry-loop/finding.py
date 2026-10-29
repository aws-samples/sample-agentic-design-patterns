from pydantic import BaseModel, model_validator
from typing import Literal

class Finding(BaseModel):
    claim: str
    evidence: str
    source_url: str | None = None
    source_name: str
    publication_date: str | None = None
    confidence: Literal["high", "medium", "low", "uncertain"]
    source_type: Literal["academic", "news", "documentation", "blog", "other"]
    source_type_detail: str | None = None

    @model_validator(mode="after")
    def check_source_type_detail(self) -> "Finding":
        if self.source_type == "other" and not self.source_type_detail:
            raise ValueError(
                "source_type_detail is required when source_type is 'other'"
            )
        return self
