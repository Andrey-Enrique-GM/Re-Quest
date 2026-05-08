import pymysql

def get_connection():
    return pymysql.connect(
        host="jdbc:mysql://34.30.245.236:3306/requestDB",
        user="andrey",
        password="andrey",
        database="requestDB",
        port=3306
    )