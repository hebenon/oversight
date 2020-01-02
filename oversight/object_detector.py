# Copyright 2016 Ben Carson. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
__author__ = 'bcarson'

import tensorflow as tf
import tensorflow_hub as hub

import os
import logging
import time
import threading

from oversight.signals import image, image_analysis

logger = logging.getLogger('root')

class ObjectDetector(object):
    """
    Classifier class which uses an object detection model to identify labels within the image.
    """

    def __init__(self, module_handle):
        #'https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1'
        self.detector = hub.load(module_handle).signatures['default']
        self.lock = threading.Lock()

        image.connect(self.predict)

    def predict(self, sender, **data):
        image_data = data['image']

        # Prepare image as a tensor
        decoded_jpeg = tf.image.decode_jpeg(image_data)
        converted_img  = tf.image.convert_image_dtype(decoded_jpeg, tf.float32)[tf.newaxis, ...]

        # Run the tensor through the detector
        with self.lock:
            start_time = time.time()
            result = self.detector(converted_img)
            end_time = time.time()

        result = {key:value.numpy() for key,value in result.items()}

        logger.info("Found %d objects.", len(result["detection_scores"]))
        logger.info("Inference time: %d", end_time-start_time)
 
        results = []
       
        for i in range(min(20, len(result["detection_scores"]))):
            #logger.debug(str(result["detection_class_entities"][i]) + ": " + str(result["detection_scores"][i]))
            results += [(str(result["detection_class_entities"][i]), result["detection_scores"][i])]
            logger.info("%s: %2f", str(result["detection_class_entities"][i]), result["detection_scores"][i])    

        # Emit analysis results
        image_analysis.send(self, source=data['source'], timestamp=data['timestamp'], image=image_data, predictions=results)