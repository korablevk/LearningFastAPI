from datetime import date

from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.functions import coalesce

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomDAO(BaseDAO):
    model = Rooms

    ''' 
    WITH cnt_booked_rooms AS (
    SELECT room_id, COUNT(room_id) AS cnt
    FROM bookings
	WHERE (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
            (date_from <= '2023-05-15' AND date_to > '2023-05-15')
    GROUP BY room_id
    )
    SELECT id, hotel_id, name, description, price, services, quantity, image_id, COALESCE(rooms.quantity - cnt_booked_rooms.cnt, rooms.quantity) AS rooms
    FROM rooms
    LEFT JOIN cnt_booked_rooms ON cnt_booked_rooms.room_id = rooms.id
    WHERE hotel_id = 1;
    '''

    @classmethod
    async def get_rooms_by_hotel_id(
            cls,
            hotel_id: int,
            date_from: date,
            date_to: date,
    ):
        try:
            async with async_session_maker() as session:
                numbers_booked_rooms = (
                    select(Bookings.room_id, func.count(Bookings.room_id).label("cnt"))
                    .select_from(Bookings)
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
                    .group_by(Bookings.room_id)
                    .cte("numbers_booked_rooms")
                )
                '''
                    SELECT id, hotel_id, name, description, price, services, quantity, image_id, COALESCE(rooms.quantity - cnt_booked_rooms.cnt, rooms.quantity) AS rooms
                    FROM rooms
                    LEFT JOIN cnt_booked_rooms ON cnt_booked_rooms.room_id = rooms.id
                    WHERE hotel_id = 1;
                '''

                rooms_list_in_hotel_by_id = (
                    select(Rooms.id,
                           Rooms.hotel_id,
                           Rooms.name,
                           Rooms.description,
                           Rooms.price,
                           Rooms.services,
                           Rooms.quantity,
                           Rooms.image_id,
                           (coalesce(Rooms.quantity - numbers_booked_rooms.c.cnt, Rooms.quantity)).label('left_rooms'),

                           )
                    .select_from(Rooms)
                    .join(numbers_booked_rooms, Rooms.id == numbers_booked_rooms.c.room_id, isouter=True)
                    .where(Rooms.hotel_id == hotel_id)
                )

                rooms_list_in_hotel = await session.execute(rooms_list_in_hotel_by_id)
                return rooms_list_in_hotel.mappings().all()

        except SQLAlchemyError:
            pass
