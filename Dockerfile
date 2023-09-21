FROM python:3.10

WORKDIR /fpl-player-selector

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./.env /fpl-player-selector
COPY ./src /fpl-player-selector/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]