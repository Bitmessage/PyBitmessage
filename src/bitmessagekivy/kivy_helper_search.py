"""
Sql queries for bitmessagekivy
"""
from helper_sql import sqlQuery


def search_sql(
        xAddress="toaddress", account=None, folder="inbox", where=None,
        what=None, unreadOnly=False, start_indx=0, end_indx=20):
    """Method helping for searching mails"""
    # pylint: disable=too-many-arguments, too-many-branches
    if what is not None and what != "":
        what = "%" + what + "%"
    else:
        what = None

    if folder == "sent" or folder == "draft":
        sqlStatementBase = (
            '''SELECT toaddress, fromaddress, subject, message, status,'''
            ''' ackdata, lastactiontime FROM sent ''')
    elif folder == "addressbook":
        sqlStatementBase = '''SELECT label, address From addressbook '''
    else:
        sqlStatementBase = (
            '''SELECT folder, msgid, toaddress, message, fromaddress,'''
            ''' subject, received, read FROM inbox ''')

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
    if folder != "addressbook":
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
        for colmns in where:
            if len(where) > 1:
                if where[0] == colmns:
                    filter_col = "(%s LIKE ?" % (colmns)
                else:
                    filter_col += " or %s LIKE ? )" % (colmns)
            else:
                filter_col = "%s LIKE ?" % (colmns)
            sqlArguments.append(what)
        sqlStatementParts.append(filter_col)
    if unreadOnly:
        sqlStatementParts.append("read = 0")
    if sqlStatementParts:
        sqlStatementBase += "WHERE " + " AND ".join(sqlStatementParts)
    if folder == "sent" or folder == "draft":
        sqlStatementBase += \
            " ORDER BY lastactiontime DESC limit {0}, {1}".format(
                start_indx, end_indx)
    elif folder == "inbox":
        sqlStatementBase += \
            " ORDER BY received DESC limit {0}, {1}".format(
                start_indx, end_indx)
    # elif folder == "addressbook":
    #     sqlStatementBase += " limit {0}, {1}".format(start_indx, end_indx)
    return sqlQuery(sqlStatementBase, sqlArguments)
