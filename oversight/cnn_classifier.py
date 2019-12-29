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
import os

from oversight.signals import image, image_analysis


class CNNClassifier(object):
    """
    Classifier class which uses a Convolutional Neural Network (CNN) to predict the contents of the image.
    The CNNClassifier requires a graph that has been pre-trained with labels of the expected events.
    """

    def __init__(self, model_directory, session):
        self.session = session

        graph_file = os.path.expanduser(os.path.join(model_directory, "retrained_graph.pb"))
        label_file = os.path.expanduser(os.path.join(model_directory, "retrained_labels.txt"))

        self.labels = [line.rstrip() for line in tf.gfile.GFile(label_file)]

        with tf.gfile.FastGFile(graph_file, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

        image.connect(self.predict)

    def predict(self, sender, **data):
        image_data = data['image']

        # Feed the image_data as input to the graph and get first prediction
        softmax_tensor = self.session.graph.get_tensor_by_name('final_result:0')

        predictions = self.session.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        results = []

        for node_id in top_k:
            results += [(self.labels[node_id], predictions[0][node_id])]

        # Emit analysis results
        image_analysis.send(self, source=data['source'], timestamp=data['timestamp'], image=image_data, predictions=results)
