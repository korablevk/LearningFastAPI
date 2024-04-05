from pydantic import BaseModel
from sqlalchemy import JSON


class SHotels(BaseModel):

    id: int
    name: str
    location: str
    services: JSON
    rooms_quantity: int
    image_id: int
