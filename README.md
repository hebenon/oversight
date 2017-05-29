# Oversight
Oversight is an application that uses machine learning to detect events in IP camera feeds.

## Building
The easiest way to build and run Oversight is using [Docker](https://docker.com). From the directory where you checked out the Oversight code, build the container:

	docker build -t oversight .

## Usage
### Training the model
Before you can run Oversight, you need to train a model that will recognise the different events that you want the system to react to. To do this, you will first need to prepare a set of images that represent each event. For this example, we will use three categories: person, car and nothing, but you can use any categories you want. The last condition, nothing, is important so that the system can tell when none of the other conditions has occurred.

First, prepare a directory structure for the labelled images:

    .
    +-- _config.yml
    +-- _labelled_images
    |   +-- car
    |   +-- nothing
    |   +-- person

In each of the labelled sub-folders place example images from your cameras. In the nothing folder, place images that don't include any of the active categories (e.g. people or cars) you want to track. Now you're ready to train the model.

#### With Docker:
It's best to create a data volume to store your labelled images and the trained model as Docker can struggle with file permissions between the host and container:

    docker create -v /oversight_data --name oversight-data oversight

Then, you can get the local path that the data path corresponds to using docker inspect:

    docker inspect oversight-data

The mount path will be in the "Mounts" section:

    "Mounts": [
        {
            "Name": "dde7f9d22ac3183bacbcd93eaac7fd62472990d8c6b01858df31ed506b634926",
            "Source": "/var/lib/docker/volumes/dde7f9d22ac3183bacbcd93eaac7fd62472990d8c6b01858df31ed506b634926/_data",
            "Destination": "/oversight_data",
            "Driver": "local",
            "Mode": "",
            "RW": true,
            "Propagation": ""
        }
    ]

You can then stage your labelled images:

    cp -R labelled_images /var/lib/docker/volumes/dde7f9d22ac3183bacbcd93eaac7fd62472990d8c6b01858df31ed506b634926/_data/

Finally, you can start training the model:

    sudo docker run --volumes-from oversight-data -d --name oversight-train oversight /opt/oversight/bin/train.sh

    sudo docker logs --follow oversight-train

    Looking for images in 'car'
    Looking for images in 'nothing'
    Looking for images in 'person'
    Creating bottleneck at /oversight_data/bottlenecks/nothing/NYd2kqBk_0002.jpg.txt
    Creating bottleneck at /oversight_data/bottlenecks/nothing/NYd2kqBk_0003.jpg.txt
    Creating bottleneck at /oversight_data/bottlenecks/nothing/NYd2kqBk_0004.jpg.txt
    Creating bottleneck at /oversight_data/bottlenecks/nothing/NYd2kqBk_0006.jpg.txt
    Creating bottleneck at /oversight_data/bottlenecks/nothing/NYd2kqBk_0007.jpg.txt
    ....

Once the process has completed, you're ready to run Oversight.

#### Without Docker:
Training produces some intermediary files, so it's suggested to create a data directory for oversight.

    python <path_to_oversight>/oversight/retrain.py \
    --bottleneck_dir=<path_to_oversight_data>/bottlenecks \
    --how_many_training_steps 4000 \
    --model_dir=<path_to_oversight_data>/inception \
    --output_graph=<path_to_oversight_data>/retrained_graph.pb \
    --output_labels=<path_to_oversight_data>/retrained_labels.txt \
    --image_dir <path_to_labelled_images>

### Running Oversight
Oversight doesn't use config files, but uses command line arguments and environment variables to control its configuration. This allows you to easily inject different configurations at runtime, according to your environment. Any variable supplied as a command line argument will overwrite an environment variable.

#### Command Line Arguments

##### --download_urls, OVERSIGHT_DOWNLOAD_URLS \[TAG:DOWNLOAD_URL ...\]
One or more pairs of tag:download-url pairs. The tag is the name of the camera, and the download-url is the url on the camera where you can retrieve a still jpeg image.

E.g. --download_urls "front:https://user:password@10.0.0.150/Streaming/channels/1/picture side:https://user:password@10.0.0.151/Streaming/channels/1/picture"

##### --model_directory, OVERSIGHT_MODEL_DIRECTORY \[MODEL_DIRECTORY\]
Path to the directory where the pre-trained model is stored. Default is ~/.oversight

E.g. --model_directory ~/.oversight

##### --image_buffer_length, OVERSIGHT_IMAGE_BUFFER_LENGTH \[BUFFER_LENGTH\]
How many images from each camera to store at a time. Images in the buffer will be sent with email notifications. Default is 3.

E.g. --image_buffer-length 5

##### --notification_delay, OVERSIGHT_NOTIFICATION_DELAY \[DELAY\]
How long in seconds to wait after a trigger event before sending a notification. This allows the notification to include images before and after the trigger event. Default is 2 seconds.

E.g. --notification_delay 2

##### --smtp_recipients, OVERSIGHT_SMTP_RECIPIENTS \[RECIPIENTS ...\]
A comma separated list of email addresses to receive email notifications when trigger events occur.

E.g. --smtp_recipients someone@somewhere.com,another@another.com

##### --smtp_server, OVERSIGHT_SMTP_SERVER \[SERVER\]
The SMTP host to send email notifications through.

E.g. --smtp_server mail.somewhere.com

##### --pushover_user, OVERSIGHT_PUSHOVER_USER \[PUSHOVER_USER\]
The Pushover API user to use when sending Pushover notifications.

E.g. --pushover_user auh139ds2lkjxcjbcv73489351xc823

##### --pushover_token, OVERSIGHT_PUSHOVER_TOKEN \[PUSHOVER_TOKEN\]
The Pushover API token to use when sending Pushover notifications.

E.g. --pushover_token cx952oiiuv24ccvx586sdklakjd7c6v346c8bc612lzxbe

##### --image_storage_directory, OVERSIGHT_IMAGE_STORAGE_DIRECTORY \[IMAGE_STORAGE_DIRECTORY\]
Location to store captured images that trigger events. This will only capture an image when the event is first triggered, and won't capture subsequent frames while the trigger is active. Once the trigger is deactivated, a new trigger will capture another image. 

E.g. --image_storage_directory ~/.oversight/captured_images

##### --triggers, OVERSIGHT_TRIGGERS \[TRIGGER:LEVEL ...\]
Triggers are a set of trigger events and a level. The trigger events should correspond to the events that the Oversight model has been trained on. The level for each trigger is normalised from 0.0 to 1.0, and represents the probability of that event being a subject of an image captured from a camera. If it is highly unlikely that this event is in the image, the probability will be closer to 0.0. If it is highly likely, the probability will be closer to 1.0. The configured trigger level is the minimum threshold to activate this trigger. As an example, a trigger of 'person:0.80' has been configured. If an image has been analysed and the probability of the 'person' event is less than 0.80, the trigger will not fire. If the probability is greater than or equal to 0.80, it will fire.

E.g. --triggers "person:0.80 car:0.90 unicorn:0.20"

##### --log_level, OVERSIGHT_LOG_LEVEL \[LOG_LEVEL\]
The level of logging to apply. Valid options (from most verbose to least verbose) are DEBUG, INFO, WARNING, ERROR.

#### Running With Docker:
To run Oversight with Docker, you can override relevant environment options to configure it at runtime. In the example below, a data volume is connected that contains the pre-trained model.

    sudo docker run \
    --volumes-from oversight-data \
    -e "OVERSIGHT_DOWNLOAD_URLS=side:http://user:password@192.168.0.1/Streaming/channels/1/picture front:http://user:password@192.168.0.2/Streaming/channels/1/picture" \
    -e "OVERSIGHT_MODEL_DIRECTORY=/oversight_data" \
    -e "OVERSIGHT_IMAGE_BUFFER_LENGTH=3" \
    -e "OVERSIGHT_SMTP_RECIPIENTS=not_a_real_person@oversight.tech" \
    -e "OVERSIGHT_SMTP_HOST=your.mailserver.com" \
    -e "OVERSIGHT_TRIGGERS=car:0.85 person:0.90" \
    --name oversight -d oversight

#### Running Without Docker:
Without docker, you can either override relevant environment variables, or supply the variables as command line options:

    python oversight_runner.py --download_urls "http://user:password@192.168.0.1/Streaming/channels/1/picture" --model_directory "~/.oversight" --smtp_recipients "not_a_real_person@oversight.tech" --smtp_server "your.mailserver.com"

## The Future
- A more general model that doesn't require individual training.
- More descriptive output than raw categories (using something like [im2txt](https://github.com/tensorflow/models/tree/master/im2txt)).
- More notifiers, e.g. [Twilio](https://www.twilio.com).
- Better secrets management (e.g. integration with [Vault](https://vaultproject.io))
