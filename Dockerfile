FROM tensorflow/tensorflow

MAINTAINER Ben Carson "ben.carson@bigpond.com"

# Version of Pillow in the container is O.L.D.
RUN pip install --upgrade pillow blinker requests

ADD oversight /opt/oversight/oversight
ADD bin /opt/oversight/bin

RUN chmod +x /opt/oversight/bin/*

CMD cd /opt/oversight/oversight && python oversight_runner.py
