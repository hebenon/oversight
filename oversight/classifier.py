__author__ = 'bcarson'

import tensorflow as tf
import os


class Classifier(object):

    def __init__(self, model_directory):
        graph_file = os.path.expanduser(os.path.join(model_directory, "retrained_graph.pb"))
        label_file = os.path.expanduser(os.path.join(model_directory, "retrained_labels.txt"))

        self.labels = [line.rstrip() for line in tf.gfile.GFile(label_file)]

        with tf.gfile.FastGFile(graph_file, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

    def predict(self, sess, image_data):
        # Feed the image_data as input to the graph and get first prediction
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

        predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        results = []

        for node_id in top_k:
            results += [(self.labels[node_id], predictions[0][node_id])]

        return results
