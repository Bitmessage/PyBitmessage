from helper_sql import *


def search_sql(xAddress="toaddress", account=None, folder="inbox", where=None, what=None, unreadOnly=False):
    if what is not None and what != "":
        what = "%" + what + "%"
    else:
        what = None

    if folder == "sent":
        sql_statement_base = '''
            SELECT toaddress, fromaddress, subject, status, ackdata, lastactiontime 
            FROM sent '''
    else:
        sql_statement_base = '''SELECT folder, msgid, toaddress, fromaddress, subject, received, read
            FROM inbox '''
    sql_statement_parts = []
    sqlArguments = []
    if account is not None:
        if xAddress == 'both':
            sql_statement_parts.append("(fromaddress = ? OR toaddress = ?)")
            sqlArguments.append(account)
            sqlArguments.append(account)
        else:
            sql_statement_parts.append(xAddress + " = ? ")
            sqlArguments.append(account)
    if folder is not None:
        if folder == "new":
            folder = "inbox"
            unreadOnly = True
        sql_statement_parts.append("folder = ? ")
        sqlArguments.append(folder)
    else:
        sql_statement_parts.append("folder != ?")
        sqlArguments.append("trash")
    if what is not None:
        sql_statement_parts.append("%s LIKE ?" % (where))
        sqlArguments.append(what)
    if unreadOnly:
        sql_statement_parts.append("read = 0")
    if len(sql_statement_parts) > 0:
        sql_statement_base += "WHERE " + " AND ".join(sql_statement_parts)
    if folder == "sent":
        sql_statement_base += " ORDER BY lastactiontime"
    return sqlQuery(sql_statement_base, sqlArguments)
