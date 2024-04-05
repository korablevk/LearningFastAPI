from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import TypeAdapter, parse_obj_as
from sqlalchemy import select

from app.bookings.dao import BookingDAO
from app.bookings.models import Bookings
from app.bookings.schemas import SBooking, SNewBooking
from app.database import async_session_maker
from app.exceptions import (
    DaysOutOfLimit,
    NotExistBooking,
    RoomCannotBeBooked,
    WrongDateForm,
)
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("", status_code=200)
async def get_bookings(user: Users = Depends(get_current_user)): #-> list[SBooking]:
    return await BookingDAO.get_booking(user_id=user.id)


@router.post("", status_code=201)
async def add_booking(
    booking: SNewBooking,
    background_tasks: BackgroundTasks,
    user: Users = Depends(get_current_user),
):
    if booking.date_from >= booking.date_to:
        raise WrongDateForm
    elif (booking.date_to - booking.date_from).days >= 30:
        raise DaysOutOfLimit
    booking = await BookingDAO.add(
        user.id,
        booking.room_id,
        booking.date_from,
        booking.date_to,
    )
    if not booking:
        raise RoomCannotBeBooked
    # TypeAdapter и model_dump - это новинки версии Pydantic 2.0
    booking = TypeAdapter(SNewBooking).validate_python(booking).model_dump()
    # Celery - отдельная библиотека
    # send_booking_confirmation_email.delay(booking, user.email)
    # Background Tasks - встроено в FastAPI
    # background_tasks.add_task(send_booking_confirmation_email, booking, user.email)
    return booking


@router.delete("/{booking_id}", status_code=204)
async def remove_booking(
        booking_id: int,
        user: Users = Depends(get_current_user),
):
    del_booking = await BookingDAO.delete_booking(booking_id=booking_id, user_id=user.id)
    if not del_booking:
        raise NotExistBooking
    return {"status": 204}

