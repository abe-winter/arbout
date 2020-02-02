FROM python:3.7.6

WORKDIR /arbout

# deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# files
COPY lib lib/
COPY app.py .
