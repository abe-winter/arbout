FROM python:3.7.6

WORKDIR /arbout

# deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# files
COPY lib lib/
COPY static static/
COPY templates templates/
COPY app.py .

ENV AUTOMIG_CON postgres://postgres@arbout-db
EXPOSE 8000
CMD gunicorn -w 2 -b 0.0.0.0 app:APP
