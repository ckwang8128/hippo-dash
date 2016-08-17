# Hippo Inventory Dashboard
#

FROM ubuntu:14.04.4

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y software-properties-common \
    python-software-properties \
    && apt-add-repository -y ppa:reddit/ppa && apt-get update

RUN apt-get install -y python3 \
    python3-dev \
    python3-setuptools \
    python3-baseplate \
    python3-boto3 \
    python3-botocore \
    python3-dnspython


# Hippo install
ADD ../hippo /opt/hippo
ENV HIPPO_CONFIG_PATH /opt/hippo/config/example.ini
RUN cd /opt/hippo && python3 setup.py develop

# Dashboard install
ADD . /opt/dashboard
RUN cd /opt/dashboard