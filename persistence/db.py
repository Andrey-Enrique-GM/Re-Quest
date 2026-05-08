import pymysql

def get_connection():
    return pymysql.connect(
        host="34.30.245.236",
        user="andrey",
        password="andrey",
        database="requestDB",
        port=3306
    )