import asyncio

import pymysql
import time
from create_bot import config, auto_coins
from tgbot.misc.requester import get_btc

def connection_init():
    host = config.db.host
    user = config.db.user
    password = config.db.password
    db_name = config.db.database
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.SSCursor
    )
    return connection


def sql_start():
    connection = connection_init()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    user_id INT, 
                    nickname VARCHAR(50), 
                    name VARCHAR(50), 
                    phone VARCHAR(20), 
                    reg_date INT) 
                    """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS courses(
                    id INT NOT NULL PRIMARY KEY, 
                    coin_name VARCHAR(10), 
                    coin_buy_price FLOAT(15) DEFAULT 0.00, 
                    coin_sell_price FLOAT(15) DEFAULT 0.00, 
                    wallet VARCHAR(100))
                    """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS offers(
                    offer_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    user_id INT, 
                    datetime INT,
                    operation VARCHAR(5),
                    coin VARCHAR(15),
                    quantity FLOAT(15),
                    price FLOAT(15),
                    total FLOAT(15),
                    is_completed VARCHAR(5),
                    crypto_net VARCHAR(50),
                    wallet VARCHAR(100),
                    pay_method VARCHAR(200),
                    pay_details VARCHAR(50),
                    user_nickname VARCHAR(100));
                    """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS supports(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    table_name VARCHAR(40))
                    """)
            cursor.execute("ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4")
            cursor.execute("ALTER TABLE courses CONVERT TO CHARACTER SET utf8mb4")
            cursor.execute("ALTER TABLE offers CONVERT TO CHARACTER SET utf8mb4")
            cursor.execute("ALTER TABLE supports CONVERT TO CHARACTER SET utf8mb4")
            cursor.execute('INSERT IGNORE INTO courses (id, coin_name) VALUES (1, "BTC");')
            cursor.execute('INSERT IGNORE INTO courses (id, coin_name) VALUES (2, "USDT");')
            print('MySQL connected OK')
    finally:
        connection.commit()
        connection.close()




async def get_coins():
    connection = connection_init()
    query = 'SELECT coin_name FROM courses;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    finally:
        connection.close()
        return result


# asyncio.run(get_coins())

async def create_user(user_id, username):
    reg_date = int(time.time())
    connection = connection_init()
    query = 'INSERT INTO users (user_id, nickname, reg_date) VALUES (%s, %s, %s);'
    query_tuple = (user_id, username, reg_date)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def is_user(user_id):
    connection = connection_init()
    query = 'SELECT * FROM users WHERE user_id = (%s);'
    query_tuple = (user_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchall()
            if len(result) > 0:
                return True
            else:
                return False
    finally:
        connection.close()



async def user_count(timestamp):
    connection = connection_init()
    query = 'SELECT * FROM users WHERE reg_date > (%s);'
    query_tuple = (timestamp,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchall()
    finally:
        connection.close()
        return len(result)


async def get_users():
    connection = connection_init()
    query = 'SELECT user_id FROM users;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    finally:
        connection.close()
        print(result)
        return result



async def get_course(coin, is_money=True):
    connection = connection_init()
    query = 'SELECT * FROM courses WHERE coin_name = (%s);'
    query_tuple = (coin,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result_prev = cursor.fetchone()
            if coin in auto_coins and is_money:
                market = await get_btc()
                buy_price = market - ((market + result_prev[2]) / 100)
                sell_price = market + ((market - result_prev[3]) / 100)
                result = (result_prev[0], result_prev[1], buy_price, sell_price, result_prev[4])
            else:
                result = result_prev
    finally:
        connection.close()
        return result


async def get_all_courses(is_money=True):
    connection = connection_init()
    query = 'SELECT * FROM courses;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result_prev = cursor.fetchall()
            result = []
            for res in result_prev:
                if res[1] in auto_coins and is_money:
                    market = await get_btc()
                    print(market)
                    buy_price = market - (market * res[2] * 0.01)
                    sell_price = market + (market * res[2] * 0.01)
                    result_coin = (res[0], res[1], buy_price, sell_price, res[4])
                    result.append(result_coin)
                else:
                    result.append(res)
    finally:
        connection.close()
        print(result)
        return result


async def change_buy_price(coin, price):
    connection = connection_init()
    query = 'UPDATE courses SET coin_buy_price = %s WHERE coin_name = %s;'
    query_tuple = (price, coin)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()

async def change_sell_price(coin, price):
    connection = connection_init()
    query = 'UPDATE courses SET coin_sell_price = %s WHERE coin_name = %s;'
    query_tuple = (price, coin)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def update_wallet(coin, wallet):
    connection = connection_init()
    query = 'UPDATE courses SET wallet = %s WHERE coin_name = %s;'
    query_tuple = (wallet, coin)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def get_admin_wallet(coin):
    connection = connection_init()
    query = 'SELECT wallet FROM courses WHERE coin_name = %s;'
    query_tuple = (coin,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchone()
    finally:
        connection.close()
        return result


async def create_offer(state):
    async with state.proxy() as data:
        operation = data.as_dict()['operation']
        coin = data.as_dict()['coin']
        price = data.as_dict()['price']
        user_id = data.as_dict()['user_id']
        user_username = data.as_dict()['user_username']
        total = data.as_dict()['total']
        quantity = data.as_dict()['quantity']
        offer_date = int(time.time())
        # crypto_net = data.as_dict()['crypto_net']
        # wallet = data.as_dict()['wallet']
        # pay_method = data.as_dict()['pay_method']
        # pay_details = data.as_dict()['pay_details']
    connection = connection_init()
    query = """
        INSERT INTO offers 
        (user_id, datetime, operation, coin, quantity, price, total, is_completed, user_nickname)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    # query_tuple = (user_id, offer_date, operation, coin, quantity, price, total, 'False', crypto_net, wallet,
    #                pay_method, pay_details)
    query_tuple = (user_id, offer_date, operation, coin, quantity, price, total, 'False', user_username)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def get_offers_req(is_completed):
    connection = connection_init()
    query = 'SELECT * FROM offers WHERE is_completed = (%s);'
    query_tuple = (is_completed,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchall()
    finally:
        connection.close()
        return result


async def get_offer_id(offer_id):
    connection = connection_init()
    query = 'SELECT * FROM offers WHERE offer_id = (%s);'
    query_tuple = (offer_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchone()
    finally:
        connection.close()
        return result


async def change_offer_status(offer_id, offer_status):
    connection = connection_init()
    query = 'UPDATE offers SET is_completed = %s WHERE offer_id = %s;'
    query_tuple = (offer_status, offer_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


