"""
Additional SQL helper for searching messages.
Used by :mod:`.bitmessageqt`.
"""

# pylint: disable=too-many-arguments
from helper_sql import sqlQuery
from tr import _translate


def search_sql(
    xAddress='toaddress', account=None, folder='inbox', where=None,
    what=None, unreadOnly=False
):
    """
    Search for messages from given account and folder having search term
    in one of it's fields.

    :param str xAddress: address field checked
      ('fromaddress', 'toaddress' or 'both')
    :param account: the account which is checked
    :type account: :class:`.bitmessageqt.account.BMAccount`
      instance
    :param str folder: the folder which is checked
    :param str where: message field which is checked ('toaddress',
      'fromaddress', 'subject' or 'message'), by default check any field
    :param str what: the search term
    :param bool unreadOnly: if True, search only for unread messages
    :return: all messages where <where> field contains <what>
    :rtype: list[list]
    """
    # pylint: disable=too-many-arguments, too-many-branches
    if what:
        what = '%' + what + '%'
        if where == _translate("MainWindow", "To"):
            where = 'toaddress'
        elif where == _translate("MainWindow", "From"):
            where = 'fromaddress'
        elif where == _translate("MainWindow", "Subject"):
            where = 'subject'
        elif where == _translate("MainWindow", "Message"):
            where = 'message'
        else:
            where = 'toaddress || fromaddress || subject || message'

    sqlStatementBase = 'SELECT toaddress, fromaddress, subject, ' + (
        'status, ackdata, lastactiontime FROM sent ' if folder == 'sent'
        else 'folder, msgid, received, read FROM inbox '
    )

    sqlStatementParts = []
    sqlArguments = []
    if account is not None:
        if xAddress == 'both':
            sqlStatementParts.append('(fromaddress = ? OR toaddress = ?)')
            sqlArguments.append(account)
            sqlArguments.append(account)
        else:
            sqlStatementParts.append(xAddress + ' = ? ')
            sqlArguments.append(account)
    if folder is not None:
        if folder == 'new':
            folder = 'inbox'
            unreadOnly = True
        sqlStatementParts.append('folder = ? ')
        sqlArguments.append(folder)
    else:
        sqlStatementParts.append('folder != ?')
        sqlArguments.append('trash')
    if what:
        sqlStatementParts.append('%s LIKE ?' % (where))
        sqlArguments.append(what)
    if unreadOnly:
        sqlStatementParts.append('read = 0')
    if sqlStatementParts:
        sqlStatementBase += 'WHERE ' + ' AND '.join(sqlStatementParts)
    if folder == 'sent':
        sqlStatementBase += ' ORDER BY lastactiontime'
    return sqlQuery(sqlStatementBase, sqlArguments)


def check_match(
        toAddress, fromAddress, subject, message, where=None, what=None):
    """
    Check if a single message matches a filter (used when new messages
    are added to messagelists)
    """
    # pylint: disable=too-many-arguments
    if not what:
        return True

    if where in (
        _translate("MainWindow", "To"), _translate("MainWindow", "All")
    ):
        if what.lower() not in toAddress.lower():
            return False
    elif where in (
        _translate("MainWindow", "From"), _translate("MainWindow", "All")
    ):
        if what.lower() not in fromAddress.lower():
            return False
    elif where in (
        _translate("MainWindow", "Subject"),
        _translate("MainWindow", "All")
    ):
        if what.lower() not in subject.lower():
            return False
    elif where in (
        _translate("MainWindow", "Message"),
        _translate("MainWindow", "All")
    ):
        if what.lower() not in message.lower():
            return False
    return True
