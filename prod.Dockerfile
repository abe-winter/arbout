FROM python:3.7.6

WORKDIR /arbout

# deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# static css
COPY Makefile .
RUN mkdir static
RUN make static/bootstrap.min.css && rm *.zip

# files
COPY lib lib/
COPY static static/
COPY templates templates/
COPY app.py .

ENV AUTOMIG_CON postgres://postgres@arbout-db
EXPOSE 8000
CMD gunicorn -w 2 -b 0.0.0.0 --access-logfile - --error-logfile - app:APP
