"""Additional SQL helper for searching messages"""

from helper_sql import sqlQuery

try:
    from PyQt4 import QtGui
    haveQt = True
except ImportError:
    haveQt = False


def search_translate(context, text):
    """Translation wrapper"""
    if haveQt:
        return QtGui.QApplication.translate(context, text)
    return text.lower()


def search_sql(xAddress="toaddress", account=None, folder="inbox", where=None, what=None, unreadOnly=False):
    """Perform a search in mailbox tables"""
    # pylint: disable=too-many-arguments, too-many-branches
    if what is not None and what != "":
        what = "%" + what + "%"
        if where == search_translate("MainWindow", "To"):
            where = "toaddress"
        elif where == search_translate("MainWindow", "From"):
            where = "fromaddress"
        elif where == search_translate("MainWindow", "Subject"):
            where = "subject"
        elif where == search_translate("MainWindow", "Message"):
            where = "message"
        else:
            where = "toaddress || fromaddress || subject || message"
    else:
        what = None

    if folder == "sent":
        sqlStatementBase = '''
            SELECT toaddress, fromaddress, subject, status, ackdata, lastactiontime
            FROM sent '''
    else:
        sqlStatementBase = '''SELECT folder, msgid, toaddress, fromaddress, subject, received, read
            FROM inbox '''

    sqlStatementParts = []
    sqlArguments = []
    if account is not None:
        if xAddress == 'both':
            sqlStatementParts.append("(fromaddress = ? OR toaddress = ?)")
            sqlArguments.append(account)
            sqlArguments.append(account)
        else:
            sqlStatementParts.append(xAddress + " = ? ")
            sqlArguments.append(account)
    if folder is not None:
        if folder == "new":
            folder = "inbox"
            unreadOnly = True
        sqlStatementParts.append("folder = ? ")
        sqlArguments.append(folder)
    else:
        sqlStatementParts.append("folder != ?")
        sqlArguments.append("trash")
    if what is not None:
        sqlStatementParts.append("%s LIKE ?" % (where))
        sqlArguments.append(what)
    if unreadOnly:
        sqlStatementParts.append("read = 0")
    if sqlStatementParts:
        sqlStatementBase += "WHERE " + " AND ".join(sqlStatementParts)
    if folder == "sent":
        sqlStatementBase += " ORDER BY lastactiontime"
    return sqlQuery(sqlStatementBase, sqlArguments)


def check_match(toAddress, fromAddress, subject, message, where=None, what=None):
    """Check if a single message matches a filter (used when new messages are added to messagelists)"""
    # pylint: disable=too-many-arguments
    if what is not None and what != "":
        if where in (search_translate("MainWindow", "To"), search_translate("MainWindow", "All")):
            if what.lower() not in toAddress.lower():
                return False
        elif where in (search_translate("MainWindow", "From"), search_translate("MainWindow", "All")):
            if what.lower() not in fromAddress.lower():
                return False
        elif where in (search_translate("MainWindow", "Subject"), search_translate("MainWindow", "All")):
            if what.lower() not in subject.lower():
                return False
        elif where in (search_translate("MainWindow", "Message"), search_translate("MainWindow", "All")):
            if what.lower() not in message.lower():
                return False
    return True
