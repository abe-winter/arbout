FROM python:3.7.6

WORKDIR /arbout

# deps
COPY dev-requirements.txt .
RUN pip install -r dev-requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# files
COPY lib lib/
COPY test test/
COPY mypy.ini .
COPY .pylintrc .
COPY app.py .
