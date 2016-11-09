FROM tensorflow/tensorflow:0.11.0rc2

MAINTAINER Ben Carson "ben.carson@bigpond.com"

# Version of Pillow in the container is O.L.D.
RUN pip install --upgrade pillow && pip install blinker && pip install requests

ADD oversight /opt/oversight/oversight
ADD im2txt /opt/oversight/oversight/im2txt
ADD bin /opt/oversight/bin

RUN chmod +x /opt/oversight/bin/*

CMD cd /opt/oversight/oversight && python oversight.py
