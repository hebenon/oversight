# Oversight
Oversight is an application that uses machine learning to detect events in IP camera feeds.

## Building
The easiest way to build and run Oversight is using [Docker](https://docker.com). From the directory where you checked out the Oversight code, build the container:

	docker build -t oversight .

## Usage
### Training the model
Before you can run Oversight, you need to train a model that will recognise the different events that you want the system to react to. To do this, you will first need to prepare a set of images that represent each event. For this example, we will use three categories: person, car and nothing. The last condition, nothing, is important so that the system can tell when none of the other conditions has occurred.

### Running Oversight


## The Future
- Support for multiple cameras. This is mechanically easy, but needs a sane way of managing the config.
- More notifiers, e.g. [Pushover](https://pushover.net) or [Twilio](https://www.twilio.com).
