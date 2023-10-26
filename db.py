import pymysql

host = 'localhost'
user = 'root'
passwd = '0913158716'

# Initializing connection
db = pymysql.connections.Connection(
    host=host,
    user=user,
    password=passwd
)

# Creating cursor object
cur = db.cursor()

# Executing SQL query
cur.execute("CREATE DATABASE IF NOT EXISTS blogpage")
cur.execute("SHOW DATABASES")

# Displaying db
for dbs in cur:
    print(dbs)

# Closing the cursor and connection to the db
cur.close()
db.close()
