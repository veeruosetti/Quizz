from enum import Enum

from app.constants import (
    ONE_MINUTE,
    TWO_MUNUTES,
    THREE_MINUTES,
    FOUR_MINUTES,
    FIVE_MINUTES,
    FROZEN, 
    OPEN
)

class QuizStatusEnum(str, Enum):
    OPEN = OPEN
    FROZEN = FROZEN

class QuestionDurationEnum(int, Enum):
    ONE_MINUTE = ONE_MINUTE
    TWO_MUNUTES = TWO_MUNUTES
    THREE_MINUTES = THREE_MINUTES
    FOUR_MINUTES = FOUR_MINUTES
    FIVE_MINUTES = FIVE_MINUTES