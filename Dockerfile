FROM tensorflow/tensorflow

MAINTAINER Ben Carson "ben.carson@bigpond.com"

ADD src /opt/oversight

CMD cd /opt/oversight && python oversight.py