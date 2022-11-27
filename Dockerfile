ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN apt-get update && apt-get install nginx -y
RUN python -m pip install -r requirements.txt

RUN mkdir -p /app
WORKDIR /app
COPY default /etc/nginx/sites-available/default
COPY . .

EXPOSE 7777
CMD nginx; voila --Voila.tornado_settings='{"headers":{"Content-Security-Policy":"frame-ancestors self *" }}' calstats.ipynb --theme=dark --port 8866 --no-browser --enable_nbextensions=True