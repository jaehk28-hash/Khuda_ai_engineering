from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GuessRequest(BaseModel):
    guess_word: str

    @field_validator("guess_word")
    @classmethod
    def normalize_guess_word(cls, value: str) -> str:
        return value.strip().upper()


class GuessResponse(BaseModel):
    attempt_number: int
    guess_word: str
    feedback: list[str]
    is_correct: bool
    attempts_remaining: int


class AttemptResponse(BaseModel):
    attempt_number: int
    guess_word: str
    feedback: list[str]
    created_at: datetime


class TodayAttemptsResponse(BaseModel):
    date: date
    attempts: list[AttemptResponse]


class AnswerResponse(BaseModel):
    date: date
    answer_word: str
