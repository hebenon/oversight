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

from datetime import datetime, timedelta

from blinker import ANY
from nose.tools import with_setup

from oversight.signals import image_analysis, trigger_event
from oversight.monitor import Monitor

from test_utils import load_image


def teardown():
    # Disconnect any triggers
    for receiver in image_analysis.receivers_for(ANY):
        image_analysis.disconnect(receiver)

    for receiver in trigger_event.receivers_for(ANY):
        trigger_event.disconnect(receiver)

@with_setup(teardown=teardown)
def test_generate_event_if_over_threshold():
    monitor = Monitor(triggers={'test_event': 0.5})

    # Set up test conditions
    now = datetime.utcnow()
    image = load_image()
    generated_events = []

    def event_received(sender,**data):
        generated_events.append(data)

    trigger_event.connect(event_received)

    image_analysis.send('test', timestamp=now, image=image, predictions=[('test_event', 0.99)])

    # Verify result
    expected = dict(timestamp=now, image=image, event='test_event')

    assert len(generated_events) is 1
    assert generated_events[0] == expected

@with_setup(teardown=teardown)
def test_no_event_if_under_threshold():
    monitor = Monitor(triggers={'test_event': 0.5})

    # Set up test conditions
    now = datetime.utcnow()
    image = load_image()
    generated_events = []

    def event_received(sender,**data):
        generated_events.append(data)

    trigger_event.connect(event_received)

    image_analysis.send('test', timestamp=now, image=image, predictions=[('test_event', 0.4)])

    # Verify result
    assert len(generated_events) is 0

@with_setup(teardown=teardown)
def test_no_event_if_already_active():
    monitor = Monitor(triggers={'test_event': 0.5})

    # Set up test conditions
    now = datetime.utcnow()
    image = load_image()
    generated_events = []

    def event_received(sender,**data):
        generated_events.append(data)

    trigger_event.connect(event_received)

    # Trigger once
    image_analysis.send('test', timestamp=now, image=image, predictions=[('test_event', 0.99)])

    # Second prediction - should not generate
    image_analysis.send('test', timestamp=now + timedelta(seconds=1), image=image, predictions=[('test_event', 0.99)])

    # Verify result
    expected = dict(timestamp=now, image=image, event='test_event')

    assert len(generated_events) is 1
    assert generated_events[0] == expected

@with_setup(teardown=teardown)
def test_generate_event_once_active_cleared():
    monitor = Monitor(triggers={'test_event': 0.5})

    # Set up test conditions
    now = datetime.utcnow()
    image = load_image()
    generated_events = []

    def event_received(sender,**data):
        generated_events.append(data)

    trigger_event.connect(event_received)

    # Trigger initial
    image_analysis.send('test', timestamp=now, image=image, predictions=[('test_event', 0.99)])

    # Clear the first alarm.
    image_analysis.send('test', timestamp=now + timedelta(seconds=1), image=image, predictions=[('test_event', 0.4)])

    # Send the third event
    image_analysis.send('test', timestamp=now + timedelta(seconds=2), image=image, predictions=[('test_event', 0.99)])

    # Verify result
    expected_first = dict(timestamp=now, image=image, event='test_event')
    expected_second = dict(timestamp=now + timedelta(seconds=2), image=image, event='test_event')

    assert len(generated_events) is 2
    assert generated_events[0] == expected_first
    assert generated_events[1] == expected_second