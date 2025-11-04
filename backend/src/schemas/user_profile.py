from pydantic import BaseModel, Field


class PortfolioItem(BaseModel):
    """Represents a single project in the user's portfolio."""

    name: str
    client_industry: str
    description: str = Field(
        ..., max_length=200, description="A brief description of the project."
    )
    key_outcomes: str = Field(
        ..., description="The key results and outcomes of the project."
    )


class UserProfile(BaseModel):
    """Represents the user's professional profile."""

    company_name: str
    company_description: str = Field(
        ..., max_length=500, description="What the user's company does."
    )
    industries_served: list[str]
    portfolio: list[PortfolioItem] = Field(..., max_items=10)
