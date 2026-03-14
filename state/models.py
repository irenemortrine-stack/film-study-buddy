from typing import Optional
from pydantic import BaseModel, Field


class Clarification(BaseModel):
    question: str
    answer: str


class TheoryCard(BaseModel):
    name: str
    key_figures: str
    core_idea: str
    mermaid: str
    visual_html: str
    source_links: list[str] = Field(default_factory=list)


class Session(BaseModel):
    state: str = "IDLE"
    film_title: Optional[str] = None
    original_review: str = ""
    keywords: list[str] = Field(default_factory=list)
    clarifications: list[Clarification] = Field(default_factory=list)
    clarification_round: int = 0
    theory_cards: list[TheoryCard] = Field(default_factory=list)
    selected_theory: Optional[TheoryCard] = None
    essay_questions: list[str] = Field(default_factory=list)
    essay_answers: list[str] = Field(default_factory=list)
    current_question_index: int = 0
    processed_message_ids: list[str] = Field(default_factory=list)
