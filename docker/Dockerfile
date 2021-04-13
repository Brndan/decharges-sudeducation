FROM python:3.9-slim

WORKDIR /srv/app/

RUN apt-get update && apt-get install -y locales default-libmysqlclient-dev build-essential

# Set the locale
RUN sed -i '/fr_FR.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR:fr \
    LC_ALL=fr_FR.UTF-8

COPY requirements.txt /
RUN python -m pip install -r /requirements.txt uwsgi && rm /requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT [ "uwsgi", "-i", "uwsgi.ini" ]
