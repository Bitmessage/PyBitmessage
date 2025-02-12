"""
Sql queries for bitmessagekivy
"""
from pybitmessage.helper_sql import sqlQuery
from dbcompat import dbstr


def search_sql(
        xAddress="toaddress", account=None, folder="inbox", where=None,
        what=None, unreadOnly=False, start_indx=0, end_indx=20):
    # pylint: disable=too-many-arguments, too-many-branches
    """Method helping for searching mails"""
    if what is not None and what != "":
        what = "%" + what + "%"
    else:
        what = None
    if folder in ("sent", "draft"):
        sqlStatementBase = (
            '''SELECT toaddress, fromaddress, subject, message, status,'''
            ''' ackdata, senttime FROM sent '''
        )
    elif folder == "addressbook":
        sqlStatementBase = '''SELECT label, address From addressbook '''
    else:
        sqlStatementBase = (
            '''SELECT folder, msgid, toaddress, message, fromaddress,'''
            ''' subject, received, read FROM inbox '''
        )
    sqlStatementParts = []
    sqlArguments = []
    if account is not None:
        if xAddress == 'both':
            sqlStatementParts.append("(fromaddress = ? OR toaddress = ?)")
            sqlArguments.append(dbstr(account))
            sqlArguments.append(dbstr(account))
        else:
            sqlStatementParts.append(xAddress + " = ? ")
            sqlArguments.append(dbstr(account))
    if folder != "addressbook":
        if folder is not None:
            if folder == "new":
                folder = "inbox"
                unreadOnly = True
            sqlStatementParts.append("folder = ? ")
            sqlArguments.append(dbstr(folder))
        else:
            sqlStatementParts.append("folder != ?")
            sqlArguments.append(dbstr("trash"))
    if what is not None:
        for colmns in where:
            if len(where) > 1:
                if where[0] == colmns:
                    filter_col = "(%s LIKE ?" % (colmns)
                else:
                    filter_col += " or %s LIKE ? )" % (colmns)
            else:
                filter_col = "%s LIKE ?" % (colmns)
            sqlArguments.append(dbstr(what))
        sqlStatementParts.append(filter_col)
    if unreadOnly:
        sqlStatementParts.append("read = 0")
    if sqlStatementParts:
        sqlStatementBase += "WHERE " + " AND ".join(sqlStatementParts)
    if folder in ("sent", "draft"):
        sqlStatementBase += \
            "ORDER BY senttime DESC limit {0}, {1}".format(
                start_indx, end_indx)
    elif folder == "inbox":
        sqlStatementBase += \
            "ORDER BY received DESC limit {0}, {1}".format(
                start_indx, end_indx)
    return sqlQuery(sqlStatementBase, sqlArguments)
