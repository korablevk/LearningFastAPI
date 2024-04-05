from datetime import date, datetime
from typing import List, Optional
import pandas as pd
from io import BytesIO
import csv
import codecs
import json

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy import insert
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker

from app.hotels.dao import HotelDAO

router = APIRouter(prefix="/importer")


def convert_to_json(csv_file):
    contents = csv_file.file.read()
    buffer = BytesIO(contents)
    df = pd.read_csv(buffer)
    buffer.close()
    csv_file.file.close()
    return df.to_json(orient="records")


@router.post("/hotels", status_code=201)
async def upload_csv_file(
        background_tasks: BackgroundTasks,
        table_name: str,
        csv_file: UploadFile = File(...),
        user: Users = Depends(get_current_user),
):
    async with async_session_maker() as session:
        if table_name == "Hotels":
            csv_list_file_json = convert_to_json(csv_file)
            parsed = json.loads(csv_list_file_json)
            add_file = insert(Hotels).values(parsed)
            await session.execute(add_file)
            await session.commit()
        elif table_name == "Rooms":
            csv_list_file_json = convert_to_json(csv_file)
            parsed = json.loads(csv_list_file_json)
            add_file = insert(Rooms).values(parsed)
            await session.execute(add_file)
            await session.commit()
        else:
            raise Exception





    # csvReader = csv.DictReader(codecs.iterdecode(csv_file.file, 'utf-8'))
    # background_tasks.add_task(csv_file.file.close)
    # csv_list_file_json = list(csvReader)
    # name, location, services, rooms_quantity, image_id
    # df = pd.read_csv(csv_file, sep=",", parse_dates=["name", "location", "services", "rooms_quantity", "image_id"],
    #                  low_memory=False)
    # print(df)
    # async with async_session_maker() as session:
    #     if table_name == "Hotels":
    #         # add_file = insert(Hotels).values(csv_list_file_json)
    #     elif table_name == "Rooms":
    #         # add_file = insert(Hotels).values(csv_list_file_json)
    #     else:
    #         raise Exception

    # await session.execute(add_file)
    #
    # await session.commit()
