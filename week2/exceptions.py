class ServiceError(Exception):
    pass


class DuplicateUsernameError(ServiceError):
    pass


class InvalidCredentialsError(ServiceError):
    pass


class InvalidTokenError(ServiceError):
    pass


class UserNotFoundError(ServiceError):
    pass


class InvalidGuessLengthError(ServiceError):
    def __init__(self, expected_length: int):
        self.expected_length = expected_length
        super().__init__(f"단어는 {expected_length}글자여야 합니다.")


class DailyAttemptLimitExceededError(ServiceError):
    pass
