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
import logging
import os
import time

from signals import image, image_analysis

from im2txt import configuration
from im2txt import inference_wrapper
from im2txt.inference_utils import caption_generator
from im2txt.inference_utils import vocabulary

logger = logging.getLogger('root')


class Im2TxtClassifier(object):
    """
    Classifier class which uses the Im2Txt model to predict the contents of the image.
    """

    def __init__(self, model_directory):
        checkpoint_path = os.path.expanduser(model_directory)
        vocab_file = os.path.expanduser(os.path.join(model_directory, "word_counts.txt"))

        # Build the inference graph.
        g = tf.Graph()
        with g.as_default():
            model = inference_wrapper.InferenceWrapper()
            restore_fn = model.build_graph_from_config(configuration.ModelConfig(), checkpoint_path)
        g.finalize()

        # Create tensorflow session
        self.session = tf.Session(graph=g)

        # Load the model from checkpoint.
        restore_fn(self.session)

        # Create the vocabulary and generator
        self.vocab = vocabulary.Vocabulary(vocab_file)
        self.generator = caption_generator.CaptionGenerator(model, self.vocab)

        image.connect(self.predict)

    def predict(self, sender, **data):
        image_data = data['image']

        start = time.time()

        # Generate a caption for this image.
        caption = self.generator.beam_search(self.session, image_data)[0]
        sentence = " ".join([self.vocab.id_to_word(w) for w in caption.sentence[1:-1]])

        logger.debug("im2txt prediction time: %s", str(time.time() - start))

        # Emit analysis results
        image_analysis.send(self, timestamp=data['timestamp'], image=image_data, caption=sentence)
