from datetime import date as date_type

from sqlalchemy.orm import Session

from week2 import models


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, username: str, password_hash: str) -> models.User:
    user = models.User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_puzzle_by_date(db: Session, target_date: date_type) -> models.Puzzle | None:
    return db.query(models.Puzzle).filter(models.Puzzle.date == target_date).first()


def create_puzzle(db: Session, answer_word: str, target_date: date_type) -> models.Puzzle:
    puzzle = models.Puzzle(answer_word=answer_word, date=target_date)
    db.add(puzzle)
    db.commit()
    db.refresh(puzzle)
    return puzzle


def list_attempts(db: Session, user_id: int, puzzle_id: int) -> list[models.Attempt]:
    return (
        db.query(models.Attempt)
        .filter(models.Attempt.user_id == user_id, models.Attempt.puzzle_id == puzzle_id)
        .order_by(models.Attempt.attempt_number)
        .all()
    )


def create_attempt(
    db: Session,
    user_id: int,
    puzzle_id: int,
    guess_word: str,
    feedback: str,
    attempt_number: int,
) -> models.Attempt:
    attempt = models.Attempt(
        user_id=user_id,
        puzzle_id=puzzle_id,
        guess_word=guess_word,
        feedback=feedback,
        attempt_number=attempt_number,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt
