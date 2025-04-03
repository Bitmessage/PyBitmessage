import helper_startup
import state
import shutil
import sqlite3

expected_ver = 11

print("Looking up database file..")
helper_startup.loadConfig()
db_path = state.appdata + "messages.dat"
print("Database path: {}".format(db_path))
db_backup_path = db_path + ".blob-keys"
print("Backup path: {}".format(db_backup_path))
shutil.copyfile(db_path, db_backup_path)
print("Copied to backup")

print()

print("Open the database")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT value FROM settings WHERE key='version';")
ver = int(cur.fetchall()[0][0])
print("PyBitmessage database version: {}".format(ver))
if ver != expected_ver:
    print("Error: version must be {}".format(expected_ver))
    conn.close()
    print("Quitting..")
    quit()
print("Version OK")

print()

print("Converting..")
q = "UPDATE inbox SET msgid=CAST(msgid AS TEXT), sighash=CAST(sighash AS TEXT);"
print(q)
cur.execute(q)
q = "UPDATE pubkeys SET transmitdata=CAST(transmitdata AS TEXT);"
print(q)
cur.execute(q)
q = "UPDATE sent SET msgid=CAST(msgid AS TEXT), toripe=CAST(toripe AS TEXT), ackdata=CAST(ackdata AS TEXT);"
print(q)
cur.execute(q)

print("Commiting..")
conn.commit()
print("Conversion done")

print("Close the database")
conn.close()
print("Finished")
