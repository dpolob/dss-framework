FROM python:3.6.10-slim-buster
EXPOSE 5000

COPY . /dss-framework
RUN apt-get update
# RUN apt-get install -y python3
# RUN apt-get install -y python3-pip
RUN apt-get install -y git
#RUN apt-get install -y cron
RUN apt-get install -y vim
#RUN apt-get install -y procps
#RUN git clone https://dpolob:"P289bt25!"@github.com/dpolob/WaterNeeds.git

WORKDIR /dss-framework
RUN pip3 install -r requeriments.txt
CMD /bin/bash