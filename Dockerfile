#Flask container based on debian jesse with the slora cookiecutter flask
FROM ubuntu:14.04
MAINTAINER andre_g
RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip 

ADD blogaggregator /blogaggregator
WORKDIR /blogaggregator
RUN pip install -r requirements/dev.txt
# Expose ports
EXPOSE 5000
CMD ["python", "/blogaggregator/manage.py", "runwaitress"]



