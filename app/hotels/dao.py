from datetime import date

from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.functions import coalesce

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    '''
    SELECT * FROM hotels
    WHERE id = 1;
    '''

    @classmethod
    async def get_all_rooms(cls, hotel_id: int):
        try:
            async with async_session_maker() as session:
                get_all_rooms = (
                    select(Hotels)
                    .where(Hotels.id == hotel_id)
                )
                all_rooms = await session.execute(get_all_rooms)
                return all_rooms.mappings().all()

        except SQLAlchemyError:
            pass

    '''
    WITH cnt_booked_rooms_in_hotel AS (
            SELECT rooms.hotel_id, SUM(bookings.room_id) AS cnt
            FROM bookings
			JOIN rooms ON rooms.id = bookings.room_id
			WHERE
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
            GROUP BY hotel_id
    )
    SELECT hotels.id, hotels.name, hotels.location, hotels.services, hotels.rooms_quantity, hotels.image_id, COALESCE(hotels.rooms_quantity - cnt_booked_rooms_in_hotel.cnt, hotels.rooms_quantity) AS rooms_left
    FROM hotels
    LEFT JOIN cnt_booked_rooms_in_hotel ON hotels.id = cnt_booked_rooms_in_hotel.hotel_id
    WHERE location LIKE '%Алтай%'
    GROUP BY hotels.id, cnt_booked_rooms_in_hotel.cnt;
    '''

    @classmethod
    async def get_hotel_by_location(
            cls,
            location: str,
            date_from: date,
            date_to: date,
    ):
        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Rooms.hotel_id, func.sum(Bookings.room_id).label("cnt"))
                    .select_from(Bookings)
                    .join(Rooms, Rooms.id == Bookings.room_id)
                    .where(
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
                    .group_by(Rooms.hotel_id)
                ).cte("booked_rooms")

                '''
                SELECT hotels.id, hotels.name, hotels.location, hotels.services, hotels.rooms_quantity, hotels.image_id, COALESCE(hotels.rooms_quantity - cnt_booked_rooms_in_hotel.cnt, hotels.rooms_quantity) AS rooms_left
                FROM hotels
                LEFT JOIN cnt_booked_rooms_in_hotel ON hotels.id = cnt_booked_rooms_in_hotel.hotel_id
                WHERE location LIKE '%Алтай%'
                GROUP BY hotels.id, cnt_booked_rooms_in_hotel.cnt;
                '''
                find_hotel_by_location = (
                    select(
                        Hotels.id,
                        Hotels.name,
                        Hotels.location,
                        Hotels.services,
                        Hotels.rooms_quantity,
                        Hotels.image_id,
                        coalesce(Hotels.rooms_quantity - booked_rooms.c.cnt, Hotels.rooms_quantity).label("rooms_left")
                    )
                    .select_from(Hotels)
                    .join(booked_rooms, Hotels.id == booked_rooms.c.hotel_id, isouter=True)
                    .where(Hotels.location.like(f'%{location}%'))
                    .group_by(Hotels.id, booked_rooms.c.cnt)
                )

                find_hotel_by_location = await session.execute(find_hotel_by_location)
                return find_hotel_by_location.mappings().all()

        except SQLAlchemyError:
            pass

