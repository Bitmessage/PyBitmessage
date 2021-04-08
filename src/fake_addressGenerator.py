"""
A thread for creating addresses
"""

import queues
import state
from bmconfigparser import BMConfigParser
from network.threads import StoppableThread


fake_addresses = [
    'BM-2cXDconV3bk6nPwWgBwN7wXaqZoT1bEzGv',
    'BM-2cTWjUVedYftZJbnZfs7MWts92v1R35Try',
    'BM-2cV1UN3er2YVQBcmJaaeYMXvpwBVokJNTo',
    'BM-2cWVkWk3TyKUscdcn9E7s9hrwpv2ZsBBog',
    'BM-2cW2a5R1KidMGNByqPKn6nJDDnHtazoere'
]

class FakeAddressGenerator(StoppableThread):
    """A thread for creating fake addresses"""
    name = "addressGenerator"

    def stopThread(self):
        try:
            queues.addressGeneratorQueue.put(("stopThread", "data"))
        except:
            pass
        super(addressGenerator, self).stopThread()

    def run(self):
        """
        Process the requests for addresses generation
        from `.queues.addressGeneratorQueue`
        """
        while state.shutdown == 0:
            queueValue = queues.addressGeneratorQueue.get()
            streamNumber = 1
            try:
                if len(BMConfigParser().addresses()) > 0:
                    address = fake_addresses[len(BMConfigParser().addresses())]
                else:
                    address = fake_addresses[0]

                label = queueValue[3]
                BMConfigParser().add_section(address)
                BMConfigParser().set(address, 'label', label)
                BMConfigParser().set(address, 'enabled', 'true')
                BMConfigParser().set(
                    address, 'privencryptionkey', '5KUayt1aPSsNWsxMJnk27kv79wfRE3cWVPYLazyLQc752bXfQP3')
                BMConfigParser().save()

                queues.UISignalQueue.put((
                    'updateStatusBar', ""
                ))
                queues.UISignalQueue.put(('writeNewAddressToTable', (
                    label, address, streamNumber)))
                queues.addressGeneratorQueue.task_done()
            except IndexError:
                self.logger.error(
                    'Program error: you can only create 5 fake addresses')
