#Flask container based on debian wheezy with the slora cookiecutter flask, production version
FROM debian:wheezy
MAINTAINER andre_g
RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip \
    python-psycopg2

#install requirements before adding the production code as the code
#changes more often than the requirements
ADD blogaggregator/requirements /blogaggregator/requirements
RUN pip install -r /blogaggregator/requirements/prod.txt

#add production code
ADD blogaggregator /blogaggregator
WORKDIR /blogaggregator

#set env
ENV BLOGAGGREGATOR_ENV prod

# Expose ports
EXPOSE 80
CMD ["python", "/blogaggregator/manage.py", "runwaitress"]
