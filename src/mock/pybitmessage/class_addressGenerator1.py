"""
A thread for creating addresses
"""

from six.moves import queue

from pybitmessage import state
from pybitmessage import queues

from pybitmessage.bmconfigparser import BMConfigParser

from pybitmessage.network.threads import StoppableThread


fake_addresses = {
    'BM-2cUgQGcTLWAkC6dNsv2Bc8XB3Y1GEesVLV': {
        'privsigningkey': '5KWXwYq1oJMzghUSJaJoWPn8VdeBbhDN8zFot1cBd6ezKKReqBd',
        'privencryptionkey': '5JaeFJs8iPcQT3N8676r3gHKvJ5mTWXy1VLhGCEDqRs4vpvpxV8'
    },
    'BM-2cUd2dm8MVMokruMTcGhhteTpyRZCAMhnA': {
        'privsigningkey': '5JnJ79nkcwjo4Aj7iG8sFMkzYoQqWfpUjTcitTuFJZ1YKHZz98J',
        'privencryptionkey': '5JXgNzTRouFLqSRFJvuHMDHCYPBvTeMPBiHt4Jeb6smNjhUNTYq'
    },
    'BM-2cWyvL54WytfALrJHZqbsDHca5QkrtByAW': {
        'privsigningkey': '5KVE4gLmcfYVicLdgyD4GmnbBTFSnY7Yj2UCuytQqgBBsfwDhpi',
        'privencryptionkey': '5JTw48CGm5CP8fyJUJQMq8HQANQMHDHp2ETUe1dgm6EFpT1egD7'
    },
    'BM-2cTE65PK9Y4AQEkCZbazV86pcQACocnRXd': {
        'privsigningkey': '5KCuyReHx9MB4m5hhEyCWcLEXqc8rxhD1T2VWk8CicPFc8B6LaZ',
        'privencryptionkey': '5KBRpwXdX3n2tP7f583SbFgfzgs6Jemx7qfYqhdH7B1Vhe2jqY6'
    },
    'BM-2cX5z1EgmJ87f2oKAwXdv4VQtEVwr2V3BG': {
        'privsigningkey': '5K5UK7qED7F1uWCVsehudQrszLyMZxFVnP6vN2VDQAjtn5qnyRK',
        'privencryptionkey': '5J5coocoJBX6hy5DFTWKtyEgPmADpSwfQTazMpU7QPeART6oMAu'
    }
}


class addressGenerator(StoppableThread):
    """A thread for creating fake addresses"""
    name = "addressGenerator"
    address_list = list(fake_addresses.keys())

    def stopThread(self):
        """"To stop address generator thread"""
        try:
            queues.addressGeneratorQueue.put(("stopThread", "data"))
        except queue.Full:
            self.logger.warning('addressGeneratorQueue is Full')
        super(addressGenerator, self).stopThread()

    def run(self):
        """
        Process the requests for addresses generation
        from `.queues.addressGeneratorQueue`
        """
        while state.shutdown == 0:
            queueValue = queues.addressGeneratorQueue.get()
            try:
                address = self.address_list.pop(0)
                print("queueValue: ", queueValue)
                if len(queueValue) >= 3:
                    label = queueValue[3]
                else:
                    label = ''

                BMConfigParser().add_section(address)
                BMConfigParser().set(address, 'label', label)
                BMConfigParser().set(address, 'enabled', 'true')
                BMConfigParser().set(
                    address, 'privsigningkey', fake_addresses[address]['privsigningkey'])
                BMConfigParser().set(
                    address, 'privencryptionkey', fake_addresses[address]['privencryptionkey'])
                BMConfigParser().save()

                queues.addressGeneratorQueue.task_done()
            except IndexError:
                self.logger.error(
                    'Program error: you can only create 5 fake addresses')
