__author__ = 'bcarson'

import logging

from threading import Timer

from signals import image_analysis, trigger_event

logger = logging.getLogger('root')


class Monitor(object):
    def __init__(self, triggers, notification_delay=2):
        self.triggers = triggers
        self.notification_delay = notification_delay
        self.active_triggers = dict()

        self.notification_timer = None

        image_analysis.connect(self.handle_image_analysis)

    def send_notification(self, prediction, probability, source, timestamp, image):
        logger.debug("Sending trigger: %s (%f) @ %s" % (prediction, probability, str(timestamp)))
        trigger_event.send(self, prediction=prediction, probability=probability,
                           source=source, timestamp=timestamp, image=image)

    def handle_image_analysis(self, sender, **data):
        # Get predictions
        predictions = data['predictions']
        source = data['source']

        # Check if this is a new source or not.
        if source not in self.active_triggers:
            self.active_triggers[source] = set()

        # Check for a result
        for (prediction, probability) in predictions:
            logger.debug("prediction %s: %f", prediction, probability)

            # The graph uses softmax in the final layer, so it's *unlikely* that this will be useful.
            # That being said, it's possible to configure multiple triggers with low thresholds.
            if prediction in self.triggers and probability >= self.triggers[prediction]:
                # Prevent alarm storms by not acting on active triggers
                if prediction not in self.active_triggers[source]:
                    logger.warning("Trigger event active: %s %f", prediction, probability)
                    self.active_triggers[source].add(prediction)

                    # Only send a notification if one isn't already triggered.
                    if not self.notification_timer or not self.notification_timer.isAlive():
                        self.notification_timer = Timer(self.notification_delay, self.send_notification,
                                                        (prediction, probability, source, data['timestamp'], data['image']))
                        self.notification_timer.start()
            else:
                # Log any clearing alarms
                if prediction in self.active_triggers[source]:
                    logger.warning("Trigger event ended: %s %f", prediction, probability)

                self.active_triggers[source].discard(prediction)  # Remove from active triggers (if it exists)