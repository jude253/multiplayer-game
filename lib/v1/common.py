from pydantic import BaseModel


class PlayerInfo(BaseModel):
    id: str
    user_name: str
    last_update_utc_timestamp: float
