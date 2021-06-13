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

#RUN gsutil -m cp -r gs://feastproject/taxi/model /app 


ADD serving.py /app/serving.py
RUN chmod +x /app/serving.py



ENTRYPOINT ["python"]
CMD ["/app/serving.py"]




