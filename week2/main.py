from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import Counter
import random

app = FastAPI()

ANSWER_WORDS = ["APPLE", "GRAPE", "STONE", "BRAVE", "CHESS"]
WORD_LENGTH = 5
MAX_ATTEMPTS = 6

TODAY_ANSWER = random.choice(ANSWER_WORDS)


class GuessRequest(BaseModel):
    guess: str
    previous_attempts: list[str] = []


def evaluate_guess(guess: str, answer: str) -> list[str]:
    result = ["absent"] * len(guess)
    answer_letter_count = Counter(answer)

    for i, guess_char in enumerate(guess):
        if guess_char == answer[i]:
            result[i] = "correct"
            answer_letter_count[guess_char] -= 1

    for i, guess_char in enumerate(guess):
        if result[i] == "correct":
            continue
        if answer_letter_count[guess_char] > 0:
            result[i] = "present"
            answer_letter_count[guess_char] -= 1

    return result


@app.get("/")
def root():
    return {"message": "Wordle API"}


@app.post("/guess")
def make_guess(request: GuessRequest):
    if len(request.previous_attempts) >= MAX_ATTEMPTS:
        raise HTTPException(status_code=400, detail="시도 횟수를 모두 소진했습니다.")

    if len(request.guess) != WORD_LENGTH:
        raise HTTPException(status_code=400, detail=f"단어는 {WORD_LENGTH}글자여야 합니다.")

    feedback = evaluate_guess(request.guess.upper(), TODAY_ANSWER)
    attempt_number = len(request.previous_attempts) + 1

    return {
        "guess": request.guess,
        "attempt_number": attempt_number,
        "feedback": feedback,
        "is_correct": request.guess.upper() == TODAY_ANSWER,
        "attempts_remaining": MAX_ATTEMPTS - attempt_number,
    }


@app.get("/answer")
def check_answer():
    return {"answer": TODAY_ANSWER}