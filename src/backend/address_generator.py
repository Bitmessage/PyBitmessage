"""
Common methods and functions for kivy and qt.
"""

import queues
from bmconfigparser import config
from defaults import (
    networkDefaultProofOfWorkNonceTrialsPerByte,
    networkDefaultPayloadLengthExtraBytes
)


class AddressGenerator(object):
    """"Base class for address generation and validation"""
    def __init__(self):
        pass

    @staticmethod
    def random_address_generation(
        label, streamNumberForAddress=1, eighteenByteRipe=False,
        nonceTrialsPerByte=networkDefaultProofOfWorkNonceTrialsPerByte,
        payloadLengthExtraBytes=networkDefaultPayloadLengthExtraBytes
    ):
        """Start address generation and return whether validation was successful"""

        labels = [config.get(obj, 'label')
                  for obj in config.addresses()]
        if label and label not in labels:
            queues.addressGeneratorQueue.put((
                'createRandomAddress', 4, streamNumberForAddress, label, 1,
                "", eighteenByteRipe, nonceTrialsPerByte,
                payloadLengthExtraBytes))
            return True
        return False

    @staticmethod
    def address_validation(instance, label):
        """Checking address validation while creating"""
        labels = [config.get(obj, 'label') for obj in config.addresses()]
        if label in labels:
            instance.error = True
            instance.helper_text = 'it is already exist you'\
                ' can try this Ex. ( {0}_1, {0}_2 )'.format(
                    label)
        elif label:
            instance.error = False
        else:
            instance.error = True
            instance.helper_text = 'This field is required'
