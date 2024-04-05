FROM python:3.10

RUN mkdir /booking

WORKDIR /booking

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install pip install wheel setuptools pip --upgrade
RUN pip3 install wheel setuptools pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#RUN chmod a+x /booking/docker/*.sh

# RUN alembic upgrade head

CMD ["gunicorn", "app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]

#CMD ["uvicorn", "app.main:app", "--reload"]