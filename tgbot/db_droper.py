import pymysql

from create_bot import config


host = config.db.host
user = config.db.user
password = config.db.password
db_name = config.db.database

def connection_init(host, user, password, db_name):
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.SSCursor
    )
    return connection


def deleter():
    connection = connection_init(host, user, password, db_name)
    try:
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE users')
            cursor.execute('DROP TABLE courses')
            cursor.execute('DROP TABLE offers')
            cursor.execute('DROP TABLE supports')
    finally:
        connection.close()

deleter()