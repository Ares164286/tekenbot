FROM python:3.12

WORKDIR /bot

COPY requirements.txt /bot/

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev \
    python3-wheel \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv --copies /opt/venv \
  && . /opt/venv/bin/activate \
  && pip install --upgrade pip \
  && pip install -r requirements.txt

COPY . /bot

CMD ["python", "main.py"]
