#Flask container based on debian wheezy with the slora cookiecutter flask, production version
FROM debian:wheezy
MAINTAINER andre_g
RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip \
    python-psycopg2

ADD blogaggregator /blogaggregator
WORKDIR /blogaggregator
ENV BLOGAGGREGATOR_ENV prod
RUN pip install -r requirements/prod.txt
# Expose ports
EXPOSE 80
CMD ["python", "/blogaggregator/manage.py", "runwaitress"]
