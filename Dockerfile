FROM tiangolo/uwsgi-nginx-flask:python2.7

#COPY ./app /app/app
#COPY ./ppc_optimization /app/ppc_optimization
#COPY main.py /app/main.py

COPY ./app /app

RUN apt-get update
RUN apt-get install -y vim
RUN pip install Cython
RUN pip install numpy
RUN apt-get install -y unixodbc-dev
WORKDIR /app/ppc_optimization
RUN python setup.py install
RUN apt-get install -y rabbitmq-server
RUN pip install celery
WORKDIR /app
ENTRYPOINT rabbitmq-server -detached && celery -A main.celery worker --loglevel=INFO --detach --pidfile="$HOME/%n.pid" --logfile="$HOME/%n.log" && python main.py