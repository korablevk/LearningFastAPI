from datetime import date

from fastapi import Response, status
from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

# from app.logger importer logger
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker, engine
from app.exceptions import NotExistBooking, RoomFullyBooked
from app.hotels.rooms.models import Rooms
from app.logger import logger


class ImportDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        pass