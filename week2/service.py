import json
import random
from collections import Counter
from datetime import date as date_type

from sqlalchemy.orm import Session

from week2 import repository, security
from week2.exceptions import (
    DailyAttemptLimitExceededError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    InvalidGuessLengthError,
    UserNotFoundError,
)
from week2.models import Puzzle, User

ANSWER_WORDS = ["APPLE", "GRAPE", "STONE", "BRAVE", "CHESS", "LIGHT", "MONEY", "PLANT"]
WORD_LENGTH = 5
MAX_ATTEMPTS_PER_DAY = 6


def register_user(db: Session, username: str, password: str) -> User:
    if repository.get_user_by_username(db, username) is not None:
        raise DuplicateUsernameError(f"이미 존재하는 아이디입니다: {username}")
    password_hash = security.hash_password(password)
    return repository.create_user(db, username, password_hash)


def authenticate_user(db: Session, username: str, password: str) -> str:
    user = repository.get_user_by_username(db, username)
    if user is None or not security.verify_password(password, user.password_hash):
        raise InvalidCredentialsError("아이디 또는 비밀번호가 올바르지 않습니다.")
    return security.create_access_token(user.id, user.username)


def get_current_user(db: Session, token: str) -> User:
    payload = security.decode_access_token(token)
    user = repository.get_user_by_id(db, payload["user_id"])
    if user is None:
        raise UserNotFoundError("토큰에 해당하는 사용자를 찾을 수 없습니다.")
    return user


def get_or_create_today_puzzle(db: Session) -> Puzzle:
    today = date_type.today()
    puzzle = repository.get_puzzle_by_date(db, today)
    if puzzle is None:
        answer_word = random.choice(ANSWER_WORDS)
        puzzle = repository.create_puzzle(db, answer_word, today)
    return puzzle


def evaluate_guess(guess_word: str, answer_word: str) -> list[str]:
    # 같은 글자가 정답에 여러 번 나올 때 실제 등장 횟수만큼만 present로 표시해야 하므로,
    # 정답 글자별 잔여 개수(remaining count)를 Counter로 추적하며 correct -> present 순서로 두 번 순회한다.
    feedback = ["absent"] * len(guess_word)
    remaining_letter_counts = Counter(answer_word)

    for position, guess_char in enumerate(guess_word):
        if guess_char == answer_word[position]:
            feedback[position] = "correct"
            remaining_letter_counts[guess_char] -= 1

    for position, guess_char in enumerate(guess_word):
        if feedback[position] == "correct":
            continue
        if remaining_letter_counts[guess_char] > 0:
            feedback[position] = "present"
            remaining_letter_counts[guess_char] -= 1

    return feedback


def submit_guess(db: Session, user: User, guess_word: str) -> dict:
    if len(guess_word) != WORD_LENGTH:
        raise InvalidGuessLengthError(WORD_LENGTH)

    puzzle = get_or_create_today_puzzle(db)

    # 몇 번째 시도인지를 서버 변수로 들고 있지 않고, 매 요청마다 오늘자 시도 기록을 DB에서
    # 다시 조회해서 attempt_number와 남은 횟수를 계산한다 (무상태성 요구사항).
    previous_attempts = repository.list_attempts(db, user.id, puzzle.id)
    if len(previous_attempts) >= MAX_ATTEMPTS_PER_DAY:
        raise DailyAttemptLimitExceededError("오늘의 시도 횟수를 모두 소진했습니다.")

    feedback = evaluate_guess(guess_word, puzzle.answer_word)
    attempt_number = len(previous_attempts) + 1

    repository.create_attempt(
        db,
        user_id=user.id,
        puzzle_id=puzzle.id,
        guess_word=guess_word,
        feedback=json.dumps(feedback),
        attempt_number=attempt_number,
    )

    return {
        "attempt_number": attempt_number,
        "guess_word": guess_word,
        "feedback": feedback,
        "is_correct": guess_word == puzzle.answer_word,
        "attempts_remaining": MAX_ATTEMPTS_PER_DAY - attempt_number,
    }


def get_today_attempts(db: Session, user: User) -> dict:
    puzzle = get_or_create_today_puzzle(db)
    attempts = repository.list_attempts(db, user.id, puzzle.id)
    return {
        "date": puzzle.date,
        "attempts": [
            {
                "attempt_number": attempt.attempt_number,
                "guess_word": attempt.guess_word,
                "feedback": json.loads(attempt.feedback),
                "created_at": attempt.created_at,
            }
            for attempt in attempts
        ],
    }


def get_today_answer(db: Session) -> dict:
    puzzle = get_or_create_today_puzzle(db)
    return {"date": puzzle.date, "answer_word": puzzle.answer_word}