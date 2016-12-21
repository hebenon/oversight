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

| Command Line Argument |      Environment Variable     |                                                                                        Description                                                                                        | Example                                                             |
| :---                  | :---                          | :---                                                                                                                                                                                      | :---                                                                |
| download_urls         | OVERSIGHT_DOWNLOAD_URLS       | One or more pairs of tag:download-url pairs. The tag is the name of the camera, and the download-url is the url on the camera where you can retrieve a still jpeg image.                  | front:https://user:password@10.0.0.150/Streaming/channels/1/picture |
| model_directory       | OVERSIGHT_MODEL_DIRECTORY     | Path to the directory where the pre-trained model is stored.                                                                                                                              | ~/.oversight                                                        |
| image_buffer_length   | OVERSIGHT_IMAGE_BUFFER_LENGTH | How many images from each camera to store at a time. Images in the buffer will be sent with email notifications. Default is 3.                                                            | 5                                                                   |
| notification_delay    | OVERSIGHT_NOTIFICATION_DELAY  | How long in seconds to wait after a trigger event before sending a notification. This allows the notification to include images before and after the trigger event. Default is 2 seconds. | 2                                                                   |
| smtp_recipients       | OVERSIGHT_SMTP_RECIPIENTS     | A comma separated list of email addresses to receive email notifications when trigger events occur.                                                                                       | someone@somewhere.com,nobody@nowhere.com                            |                                       |

#### With Docker:

#### Without Docker:

## The Future
- A more general model that doesn't require individual training.
- More descriptive output than raw categories (using something like [im2txt](https://github.com/tensorflow/models/tree/master/im2txt)).
- More notifiers, e.g. [Twilio](https://www.twilio.com).
- Better secrets management (e.g. integration with [Vault](https://vaultproject.io))
