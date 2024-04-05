from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select

from app.bookings.models import Bookings
from app.database import async_session_maker


@pytest.mark.parametrize("room_id,user_id,date_from,date_to,price", [
    (5, 2, "2030-05-01", "2030-05-15", 7080),
])
async def test_add_role(
        room_id,
        user_id,
        date_from,
        date_to,
        price,
):
    async with async_session_maker() as session:
        add_booking = (
            insert(Bookings)
            .values(
                room_id=room_id,
                user_id=user_id,
                date_from=datetime.strptime("2023-07-10", "%Y-%m-%d"),
                date_to=datetime.strptime("2023-07-24", "%Y-%m-%d"),
                price=price,
            )
            .returning(
                Bookings.id,
                Bookings.user_id,
                Bookings.room_id,
                Bookings.date_from,
                Bookings.date_to,
            )
        )

        await session.execute(add_booking)
        await session.commit()
        # return new_booking.mappings().one()

        query = select(Bookings)
        result = await session.execute(query)
        print(result)

