FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["uwsgi", "--socket", "0.0.0.0:5000", "--protocol", "http", "-w", "wsgi:app"]
