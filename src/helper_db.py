import subprocess  # nosec
import time

import queues
from bmconfigparser import BMConfigParser
from helper_search import search_sql, check_match
from helper_sql import sqlExecute, sqlQuery


__all__ = ["search_sql", "check_match"]

_groups = ("blacklist", "whitelist", "subscriptions", "addressbook")
_groups_enable = ("blacklist", "whitelist", "subscriptions")


# + genAckPayload
def put_sent(
        to_address, from_address, subject, message, ackdata,
        status, encoding,
        ripe='', ttl=0, msgid='', sent_time=None, last_action_time=None,
        sleep_till_time=0, retrynumber=0):
    """Put message into Sent table"""
    # We don't know msgid until the POW is done.
    # sleep_till_time will get set when the POW gets done
    if not sent_time:
        sent_time = time.time()
    if not last_action_time:
        last_action_time = sent_time
    if not ttl:
        ttl = BMConfigParser().getint('bitmessagesettings', 'ttl')
    sqlExecute(
        "INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        msgid, to_address, ripe, from_address, subject, message, ackdata,
        int(sent_time), int(last_action_time), sleep_till_time, status, retrynumber,
        'sent', encoding, ttl
    )


def _in_inbox_already(sighash):
    return sqlQuery(
        "SELECT COUNT(*) FROM inbox WHERE sighash=?", sighash
    )[0][0] != 0


def put_inbox(
        to_address, from_address, subject, message, msgid, sighash,
        encoding=0, received_time=None, broadcast=False):
    """Put message into Inbox table"""
    if not received_time:
        received_time = time.time()
    if encoding == 0 or _in_inbox_already(sighash):
        return False

    sqlExecute(
        "INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?,?)",
        msgid, to_address, from_address, subject, int(received_time), message,
        'inbox', encoding, 0, sighash
    )

    queues.UISignalQueue.put((
        'displayNewInboxMessage',
        (msgid, to_address, from_address, subject, message)
    ))

    # If we are behaving as an API then we might need to run an
    # outside command to let some program know that a new message
    # has arrived.
    if BMConfigParser().safeGetBoolean('bitmessagesettings', 'apienabled'):
        apinotify_path = BMConfigParser().safeGet(
            'bitmessagesettings', 'apinotifypath')
        if apinotify_path:
            subprocess.call([
                apinotify_path,
                "newBroadcast" if broadcast else "newMessage"])


def put_pubkey(address, address_version, data, used_personally=None):
    """Put pubkey into Pubkeys table"""
    if used_personally is None:
        if sqlQuery(
            "SELECT * FROM pubkeys WHERE address=? AND usedpersonally='yes'",
            address
        ) == []:
            used_personally = False
        else:
            sqlExecute(
                "UPDATE pubkeys SET time=? WHERE address=?",
                time.time(), address
            )
            return
    sqlExecute(
        "INSERT INTO pubkeys VALUES (?,?,?,?,?)",
        address, address_version, data, time.time(),
        'yes' if used_personally else 'no'
    )


def _in_group_already(address, group="addressbook"):
    if group not in _groups:
        return True
    # elif group in _groups_enable:
    #     try:
    #         return sqlQuery(
    #             "SELECT enabled FROM %s WHERE address=?" % group, address
    #         )[-1][0]
    #     except IndexError:
    #         return
    else:
        return sqlQuery(
            "SELECT * FROM %s WHERE address=?" % group, address)


def put_addresslist(label, address, group="blacklist", enabled=True):
    """Put address into address list (e.g. blacklist, subscriptions...)"""
    # We must check to see if the address is already in the
    # subscriptions list. The user cannot add it again or else it
    # will cause problems when updating and deleting the entry.
    # FIXME: address should be primary key in this case
    if _in_group_already(address, group):
        return False
    sqlExecute(
        "INSERT INTO %s VALUES (?,?,?)" % group, label, address, enabled)
    return True


def put_blacklist(label, address):
    """Put address into blacklist"""
    return put_addresslist(label, address, "blacklist")


def put_subscriptions(label, address, enabled=True):
    """Put address into subscriptions"""
    return put_addresslist(label, address, "subscriptions", enabled)


def put_addressbook(label, address):
    """Put address into Addressbook"""
    # First we must check to see if the address is already in the
    # address book. The user cannot add it again or else it will
    # cause problems when updating and deleting the entry.
    if _in_group_already(address):
        return False
    sqlExecute("INSERT INTO addressbook VALUES (?,?)", label, address)
    return True


def get_subscriptions():
    """Generator for Subscriptions"""
    queryreturn = sqlQuery(
        "SELECT label, address FROM subscriptions WHERE enabled=1")
    for row in queryreturn:
        yield row


def get_addressbook():
    """Generator for Addressbook"""
    queryreturn = sqlQuery("SELECT * FROM addressbook")
    for row in queryreturn:
        yield row


def get_addresslist(group="blacklist"):
    """Generator for address list given by group arg"""
    if group not in _groups:
        return
    queryreturn = sqlQuery("SELECT * FROM %s" % group)
    for row in queryreturn:
        yield row


def get_label(address, group="addressbook"):
    """
    Get address label from address list given by group arg
    (default is addressbook)
    """
    if group not in _groups:
        return
    queryreturn = sqlQuery(
        "SELECT label FROM %s WHERE address=?" % group, address)
    try:
        return unicode(queryreturn[-1][0], 'utf-8')
    except IndexError:
        pass


def set_label(address, label, group="addressbook"):
    """Set address label in the address list given by group arg"""
    if group not in _groups:
        return
    sqlExecute("UPDATE %s set label=? WHERE address=?" % group, label, address)


def get_message(msgid):
    """Get inbox message by msgid"""
    queryreturn = sqlQuery("SELECT message FROM inbox WHERE msgid=?", msgid)
    try:
        return queryreturn[-1][0]
    except IndexError:
        return ''
