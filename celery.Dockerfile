FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY celery.requirements.txt /app
RUN pip3 install -r celery.requirements.txt
