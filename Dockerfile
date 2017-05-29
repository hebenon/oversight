FROM tensorflow/tensorflow

MAINTAINER Ben Carson "ben.carson@bigpond.com"

# Version of Pillow in the container is O.L.D.
RUN pip install --upgrade pillow blinker requests

ADD . /opt/oversight/

RUN chmod +x /opt/oversight/bin/*

CMD cd /opt/oversight && python oversight/oversight_runner.py
