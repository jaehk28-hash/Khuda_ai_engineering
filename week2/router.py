from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from week2 import schemas, service
from week2.database import get_db
from week2.exceptions import (
    DailyAttemptLimitExceededError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    InvalidGuessLengthError,
    InvalidTokenError,
    UserNotFoundError,
)
from week2.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

auth_router = APIRouter(prefix="/users", tags=["users"])
game_router = APIRouter(prefix="/game", tags=["game"])


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        return service.get_current_user(db, token)
    except (InvalidTokenError, UserNotFoundError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error


@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return service.register_user(db, user_create.username, user_create.password)
    except DuplicateUsernameError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@auth_router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        access_token = service.authenticate_user(db, form_data.username, form_data.password)
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    return schemas.Token(access_token=access_token)


@game_router.post("/guess", response_model=schemas.GuessResponse)
def submit_guess(
    guess_request: schemas.GuessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return service.submit_guess(db, current_user, guess_request.guess_word)
    except InvalidGuessLengthError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except DailyAttemptLimitExceededError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@game_router.get("/attempts/today", response_model=schemas.TodayAttemptsResponse)
def read_today_attempts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_today_attempts(db, current_user)


@game_router.get("/puzzle/today/answer", response_model=schemas.AnswerResponse)
def read_today_answer(db: Session = Depends(get_db)):
    return service.get_today_answer(db)
