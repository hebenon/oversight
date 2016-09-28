#!/bin/bash

# This idea was pretty much ripped wholesale from https://github.com/xblaster/tensor-guess
python /opt/oversight/oversight/retrain.py \
--bottleneck_dir=/oversight_data/bottlenecks \
--how_many_training_steps 4000 \
--model_dir=/oversight_data/inception \
--output_graph=/oversight_data/retrained_graph.pb \
--output_labels=/oversight_data/retrained_labels.txt \
--image_dir /oversight_data/labelled_images
