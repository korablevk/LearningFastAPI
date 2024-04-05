"""
Поместите этот код в hotels/rooms/router.py, если хотите
увидеть работу SQLAlchemy ORM и получить вложенные структуры данных
"""
from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.bookings.models import Bookings
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.models import Rooms

router = APIRouter(prefix="/hotels")


@router.get("/{hotel_id}/rooms", status_code=200)
async def get_rooms(
        hotel_id: int,
        date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
        date_to: date = Query(..., description=f"Например, {datetime.now().date()}")
) -> List:
    return await RoomDAO.get_rooms_by_hotel_id(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


