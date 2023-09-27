FROM python:3.10

WORKDIR /fpl-player-selector

COPY ./requirements.txt /fpl-player-selector/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fpl-player-selector/requirements.txt

COPY ./.env /fpl-player-selector
COPY ./src /fpl-player-selector/src
COPY ./tests /fpl-player-selector/tests

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]