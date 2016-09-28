FROM tensorflow/tensorflow

MAINTAINER Ben Carson "ben.carson@bigpond.com"

# Version of Pillow in the container is O.L.D.
RUN pip install --upgrade pillow

ADD oversight /opt/oversight
ADD train.sh /opt/oversight/

CMD cd /opt/oversight && python oversight.py
