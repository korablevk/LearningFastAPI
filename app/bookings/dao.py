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


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                """
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
                LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """

                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id).filter(booked_rooms.c.room_id.is_not(None))).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                # Рекомендую выводить SQL запрос в консоль для сверки
                # logger.debug(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if None > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
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

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.mappings().one()
                else:
                    raise RoomFullyBooked
        except RoomFullyBooked:
            raise RoomFullyBooked
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)

    '''
    SELECT room_id, user_id, date_from, date_to, bookings.price, total_cost, total_days, image_id, name, description, services
    FROM bookings
    JOIN rooms ON bookings.room_id = rooms.id
    WHERE user_id = 3;
    '''

    @classmethod
    async def get_booking(
            cls,
            user_id: int,
    ):
        try:
            async with (async_session_maker() as session):
                get_book_inf = (
                    select(Bookings.room_id,
                           Bookings.user_id,
                           Bookings.date_from,
                           Bookings.date_to,
                           Bookings.price,
                           Bookings.total_cost,
                           Bookings.total_days,
                           Rooms.image_id,
                           Rooms.name,
                           Rooms.description,
                           Rooms.services,
                           )
                    .select_from(Bookings)
                    .join(Rooms, Bookings.room_id == Rooms.id)
                    .where(Bookings.user_id == user_id)
                )

                # logger.debug(get_book_inf.compile(engine, compile_kwargs={"literal_binds": True}))

                all_booking_inf = await session.execute(get_book_inf)
                return all_booking_inf.mappings().all()

        except SQLAlchemyError:
            return None

    '''
    DELETE FROM bookings 
    WHERE user_id = (SELECT user_id FROM bookings
    WHERE bookings.id = 3) AND bookings.id = 5;
    '''

    @classmethod
    async def delete_booking(
            cls,
            user_id: int,
            booking_id: int
    ):
        try:
            async with async_session_maker() as session:
                get_user_id = (
                    select(Bookings)
                    .where(Bookings.id == booking_id)
                ).cte("get_user_id")

                delete_booking = (
                    delete(Bookings)
                    .where(and_(
                        Bookings.id == booking_id,
                        get_user_id.c.user_id == user_id
                    ))
                )

                booking_to_delete = await session.execute(delete_booking)
                await session.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)

        except SQLAlchemyError:
            print("Не тот room_id")


'''
WITH booked_rooms AS (
SELECT * FROM bookings
WHERE room_id = 1 AND user_id = 3
)   
SELECT COUNT(booked_rooms.room_id) 
FROM rooms
LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
WHERE rooms.id = 1
GROUP BY rooms.quantity, booked_rooms.room_id;
'''
# booked_rooms = (
#     select(Bookings)
#     .where(
#         and_(
#             Bookings.room_id == room_id,
#             Bookings.user_id == user_id
#         )
#     )
# ).cte("booked_rooms")
#
# '''
# SELECT COUNT(booked_rooms.room_id)
# FROM rooms
# LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
# WHERE rooms.id = 1
# GROUP BY rooms.quantity, booked_rooms.room_id;
# '''
#
# get_booking_exist = (
#     select(
#         func.count(booked_rooms.c.room_id).label(
#             "rooms_left"
#         ))
#     .select_from(Rooms)
#     .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
#     .where(Rooms.id == room_id)
#     .group_by(Rooms.quantity, booked_rooms.c.room_id)
# )
#
# rooms_left = await session.execute(get_booking_exist)
# rooms_left: int = rooms_left.scalar()
#
# print(rooms_left)
#
# if rooms_left > 0:
#     delete_booking = delete(Bookings).filter_by(
#         room_id=room_id,
#         user_id=user_id,
#     )
#
#     booking_to_delete = await session.delete(delete_booking)
#     await session.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
# else:
#     return None