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

import os
import json
import logging
import time
import threading
import torch

from io import BytesIO
from PIL import Image

from torchvision import transforms

from oversight.signals import image, image_analysis

logger = logging.getLogger('root')

class ObjectDetector(object):
    """
    Classifier class which uses an object detection model to identify labels within the image.
    """

    def __init__(self, module_handle):
        self.lock = threading.Lock()

        # Load model
        self.model = torch.hub.load('pytorch/vision:v0.4.2', module_handle, pretrained=True)
        self.model.eval()

        # Load labels
        with open("imagenet_class_index.json") as index_file:
            class_index = json.load(index_file)
            self.labels = [class_index[str(k)][1] for k in range(len(class_index))]

        image.connect(self.predict)

    def predict(self, sender, **data):
        image_data = data['image']

        # Prepare image
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(Image.open(BytesIO(image_data)))
        input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

        # Run the image through the model
        if torch.cuda.is_available():
            input_batch = input_batch.to('cuda')
            self.model.to('cuda')

        with torch.no_grad():
            output = self.model(input_batch)

        # Process results
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        _, top_indices = torch.sort(output, descending=True)
        
        #logger.info("Found %d objects.", len(top_indices))
        #logger.info("Inference time: %d", end_time-start_time)

        results = [(str(self.labels[index]), output[0][index].item()) for index in top_indices[0][:20]]
        logger.info(results)

        # Emit analysis results
        image_analysis.send(self, source=data['source'], timestamp=data['timestamp'], image=image_data, predictions=results)