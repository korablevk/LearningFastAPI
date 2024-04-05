from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Query

from app.hotels.dao import HotelDAO

router = APIRouter(prefix="/hotels")


@router.get("/{location}")
async def get_hotels_by_location_and_time(
        location: str,
        date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
        date_to: date = Query(..., description=f"Например, {datetime.now().date()}"),
) -> List:
    hotels = await HotelDAO.get_hotel_by_location(location=location, date_from=date_from, date_to=date_to)
    return hotels


@router.get("/id/{hotel_id}", status_code=200)
async def get_hotels(
        hotel_id: int,
) -> List:
    hotels = await HotelDAO.get_all_rooms(hotel_id=hotel_id)
    return hotels
