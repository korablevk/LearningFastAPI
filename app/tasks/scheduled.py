import asyncio

from app.tasks.celery_app import celery_app


async def get_data():
    await asyncio.sleep(5)


# @celery_app.task(name="periodic_task")
# def periodic_task():
#     """Пример запуска асинхронной функции внутри celery таски"""
#     print(12345)
#     asyncio.run(get_data())