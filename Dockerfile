FROM python:3.13-slim
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y --no-install-recommends \
 build-essential pkg-config default-libmysqlclient-dev \
 && rm -rf /var/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 6173

CMD [ "gunicorn", "-c", "./guconfig.py" ]