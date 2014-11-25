#Flask container based on debian jesse with the slora cookiecutter flask
FROM debian:jessie
MAINTAINER andre_g
RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip 

ADD blogaggregator /blogaggregator
WORKDIR /blogaggregator
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 5000

CMD python manage.py server

