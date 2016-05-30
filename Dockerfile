FROM ubuntu
MAINTAINER Tim3 <https://github.com/UKS-Tim3>

# Instaling dependencies
RUN apt-get update && apt-get install python3 && apt-get install -y python3-pip

ADD . /opt/issuebox
ADD .docker/run.sh /usr/local/bin
RUN pip3 install -r /opt/issuebox/requirements.txt

CMD ["/bin/bash", "-e", "/usr/local/bin/run.sh"]
