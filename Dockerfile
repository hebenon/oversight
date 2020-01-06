FROM pytorch/pytorch

MAINTAINER Ben Carson "ben.carson@bigpond.com"

ADD . /opt/oversight/

# Install requirements
RUN pip install -r /opt/oversight/requirements.txt

RUN chmod +x /opt/oversight/bin/*

CMD cd /opt/oversight && python oversight_runner.py
