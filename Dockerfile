FROM ubuntu
MAINTAINER Tim3 <https://github.com/UKS-Tim3>

# Instaling dependencies
RUN apt-get update && apt-get -y install python3 && apt-get -y install python3-pip && apt-get -y install git

RUN git clone https://github.com/UKS-Tim3/Issuebox.git /opt/issuebox

# For testing purposes
# RUN git clone -b develop https://github.com/UKS-Tim3/Issuebox.git /opt/issuebox

ADD .docker/run.sh /usr/local/bin
RUN pip3 install --upgrade pip
RUN pip3 install -r /opt/issuebox/requirements.txt

EXPOSE 8003

CMD ["/bin/bash", "-e", "/usr/local/bin/run.sh"]
