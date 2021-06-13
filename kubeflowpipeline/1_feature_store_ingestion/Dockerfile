FROM ubuntu:latest
FROM  gcr.io/google.com/cloudsdktool/cloud-sdk:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt



ADD featurestore_service.py /app/featurestore_service.py
RUN chmod +x /app/featurestore_service.py



ENTRYPOINT ["python"]
CMD ["/app/featurestore_service.py"]

