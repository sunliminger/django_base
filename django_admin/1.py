import pymysql

conn = pymysql.connect(host='120.24.85.238', port=3306, user='root', password='123', database='mysql')
cursor = conn.cursor()
cursor.execute("SELECT * from user")
data = cursor.fetchone()
print(data)
conn.close()