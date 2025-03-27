FROM python:3.12
WORKDIR /bot
COPY requirements.txt /bot/
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev \
    python3-wheel \
  && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,id=s/9aeec826-ae84-4243-9bc1-7a5a2dbadfe3-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv \
  && . /opt/venv/bin/activate \
  && pip install -U pip \
  && pip install -r requirements.txt
COPY . /bot
CMD python main.py
