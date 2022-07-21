FROM python:3.8.10

MAINTAINER Platypunk

WORKDIR /app

RUN pip install numpy==1.17.4 \
pip install pyserial==3.5

COPY Codigos /app/

CMD ["bash"]
