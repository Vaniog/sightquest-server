import datetime

from pydantic import BaseModel


class CoordinateDTO(BaseModel):
    latitude: float
    longitude: float


class UserDTO(BaseModel):
    id: int


class EventDTO(BaseModel):
    user: UserDTO
    event: str


class QuestTaskDTO(BaseModel):
    id: int


class QuestPointDTO(BaseModel):
    id: int
    tasks: list[QuestTaskDTO]


class SettingsDTO(BaseModel):
    quest_points: list[QuestPointDTO]
    duration: datetime.timedelta


class AuthorizationDTO(EventDTO):
    token: str


class LocationUpdateDTO(EventDTO):
    coordinates: CoordinateDTO


class SettingsUpdateDTO(EventDTO):
    settings: SettingsDTO


class PlayerCaughtDTO(EventDTO):
    secret: str


class TaskCompletedDTO(EventDTO):
    photo_id: int
    task_id: int
