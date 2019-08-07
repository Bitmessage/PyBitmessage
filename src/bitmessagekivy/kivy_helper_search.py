from helper_sql import *


def search_sql(xAddress="toaddress", account=None, folder="inbox", where=None, what=None, unreadOnly=False):
    if what is not None and what != "":
        what = "%" + what + "%"
    else:
        what = None

    if folder == "sent" or folder == "draft":
        sqlStatementBase = '''
            SELECT toaddress, fromaddress, subject, message, status, ackdata, lastactiontime 
            FROM sent '''
    elif folder == "addressbook":
        sqlStatementBase = '''SELECT label, address From addressbook '''
    else:
        sqlStatementBase = '''SELECT folder, msgid, toaddress, message, fromaddress, subject, received, read
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
    if folder is not "addressbook":
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
    if len(sqlStatementParts) > 0:
        sqlStatementBase += "WHERE " + " AND ".join(sqlStatementParts)
    if folder == "sent":
        sqlStatementBase += " ORDER BY lastactiontime"
    return sqlQuery(sqlStatementBase, sqlArguments)