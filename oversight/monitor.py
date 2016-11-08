__author__ = 'bcarson'

import logging

from signals import image_analysis, trigger_event

logger = logging.getLogger('root')


class Monitor(object):
    def __init__(self, triggers):
        self.triggers = triggers
        self.active_triggers = set()

        image_analysis.connect(self.handle_image_analysis)

    def process_events(self, events, timestamp, image):
        # Process all the triggers, and check if there's any changes.
        for trigger in self.triggers:
            if trigger in events:
                # Prevent alarm storms by not acting on active triggers
                if trigger not in self.active_triggers:
                    logger.warning("Trigger event active: %s", trigger)
                    self.active_triggers.add(trigger)

                    trigger_event.send(self, event=trigger, timestamp=timestamp, image=image)
            else:
                # Log any clearing alarms
                if trigger in self.active_triggers:
                    logger.warning("Trigger event ended: %s", trigger)

                self.active_triggers.discard(trigger)  # Remove from active triggers (if it exists)

    def handle_image_analysis(self, sender, **data):
        timestamp = data['timestamp']
        image = data['image']
        events = []

        # Check for a CNN predictions data source
        if 'predictions' in data:
            # Get predictions
            predictions = data['predictions']
            logger.debug("Predictions received: %s" + str(predictions))
            events = [prediction for (prediction, probability) in predictions if probability >= self.triggers[prediction]]
        elif 'caption' in data:
            caption = data['caption']
            logger.debug("Caption received: %s" % caption)
            events = [trigger for trigger in self.triggers if trigger in caption]

        self.process_events(events, timestamp, image)


