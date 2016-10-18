__author__ = 'bcarson'

import logging

from signals import image_analysis, trigger_event

logger = logging.getLogger('root')


class Monitor(object):
    def __init__(self, triggers):
        self.triggers = triggers
        self.active_triggers = set()

        image_analysis.connect(self.handle_image_analysis)

    def handle_image_analysis(self, sender, **data):
        # Get predictions
        predictions = data['predictions']

        # Check for a result
        for (prediction, probability) in predictions:
            logger.debug("prediction %s: %f", prediction, probability)

            # The graph uses softmax in the final layer, so it's *unlikely* that this will be useful.
            # That being said, it's possible to configure multiple triggers with low thresholds.
            if prediction in self.triggers and probability >= self.triggers[prediction]:
                # Prevent alarm storms by not acting on active triggers
                if prediction not in self.active_triggers:
                    logger.warning("Trigger event active: %s %f", prediction, probability)
                    self.active_triggers.add(prediction)

                    trigger_event.send(self, prediction=prediction, probability=probability,
                                       timestamp=data['timestamp'], image=data['image'])
            else:
                # Log any clearing alarms
                if prediction in self.active_triggers:
                    logger.warning("Trigger event ended: %s %f", prediction, probability)

                self.active_triggers.discard(prediction)  # Remove from active triggers (if it exists)