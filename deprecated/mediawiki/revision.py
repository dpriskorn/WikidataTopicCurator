from pydantic import BaseModel, Field


class Revision(BaseModel):
    """Represents a single MediaWiki revision with only an ID and a comment."""

    id: int = Field(..., description="Unique ID of the revision")
    comment: str = Field("", description="Edit summary comment")
