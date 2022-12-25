import sqlite3 as sq
import time
import io

from create_bot import auto_coins
from tgbot.misc.requester import get_btc

def sql_start():
    global base, cur
    base = sq.connect('crypto.db')
    cur = base.cursor()
    if base:
        print('SQLite connected OK')
    base.execute("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, user_id INTEGER, nickname VARCHAR(50), 
        name VARCHAR(50), phone VARCHAR(20), reg_date INTEGER)
        """)
    base.execute("""
        CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY, coin_name VARCHAR(10), 
        coin_buy_price FLOAT(15) DEFAULT 0.00, coin_sell_price FLOAT(15) DEFAULT 0.00, wallet VARCHAR(100))
        """)
    base.execute("""
        CREATE TABLE IF NOT EXISTS offers(offer_id INTEGER PRIMARY KEY, user_id INTEGER, datetime INTEGER, 
        operation VARCHAR(5), coin INTEGER, quantity DECIMAL(15), price DECIMAL(15), total DECIMAL(15), 
        is_completed VARCHAR(5), crypto_net VARCHAR(50), wallet VARCHAR(100), pay_method VARCHAR(200), 
        pay_details VARCHAR(50))
        """)
    base.execute("""
        CREATE TABLE IF NOT EXISTS supports(support_id INTEGER PRIMARY KEY, user_id INTEGER, text VARCHAR(4000), 
        is_completed VARCHAR(5))
        """)
    base.execute("""
            CREATE TABLE IF NOT EXISTS worktime(id INTEGER PRIMARY KEY, is_worktime VARCHAR(10))
            """)
    base.execute("""
            INSERT INTO worktime (is_worktime) 
            SELECT 'True' 
            WHERE NOT EXISTS(SELECT * FROM worktime WHERE id = 1);
            """)
    base.execute("""
        INSERT INTO courses (coin_name) VALUES 'BTC';
        """)
    base.execute("""
        INSERT INTO courses (coin_name) 
        SELECT 'USDT' 
        WHERE NOT EXISTS(SELECT * FROM courses WHERE coin_name = 'USDT');
        """)
    base.commit()

def get_coins():
    base = sq.connect('crypto.db')
    cur = base.cursor()
    result = cur.execute('SELECT coin_name FROM courses').fetchall()
    return result

def dumper():
    with io.open('backupdatabase.sql', 'w') as p:
        for line in base.iterdump():
            p.write('%s\n' % line)

async def create_user(user_id, username):
    reg_date = int(time.time())
    cur.execute('INSERT INTO users (user_id, nickname, reg_date) VALUES (?, ?, ?)', (user_id, username, reg_date))
    base.commit()


async def is_user(user_id):
    result = cur.execute('SELECT * FROM users WHERE user_id = (?)', (user_id,)).fetchall()
    if len(result) > 0:
        return True
    else:
        return False

async def user_count(timestamp):
    result = cur.execute('SELECT * FROM users WHERE reg_date > (?)', (timestamp,)).fetchall()
    return len(result)


async def get_users():
    result = cur.execute('SELECT user_id FROM users').fetchall()
    return result

async def get_course(coin, is_money=True):
    result_prev = cur.execute('SELECT * FROM courses WHERE coin_name = (?)', (coin,)).fetchone()
    if coin in auto_coins and is_money:
        market = await get_btc()
        buy_price = market - ((market + result_prev[2]) / 100)
        sell_price = market + ((market - result_prev[3]) / 100)
        result = (result_prev[0], result_prev[1], buy_price, sell_price, result_prev[4])
    else:
        result = result_prev
    return result

async def get_all_courses(is_money=True):
    result_prev = cur.execute('SELECT * FROM courses').fetchall()
    result = []
    for res in result_prev:
        if res[1] in auto_coins and is_money:
            market = await get_btc()
            buy_price = market - ((market + res[2]) / 100)
            sell_price = market + ((market + res[3]) / 100)
            result_coin = (res[0], res[1], buy_price, sell_price, res[4])
            result.append(result_coin)
        else:
            result.append(res)
    return result

async def change_buy_price(coin, price):
    cur.execute('UPDATE courses SET coin_buy_price = ? WHERE coin_name = ?', (price, coin))
    base.commit()

async def change_sell_price(coin, price):
    cur.execute('UPDATE courses SET coin_sell_price = ? WHERE coin_name = ?', (price, coin))
    base.commit()


async def update_wallet(coin, wallet):
    cur.execute('UPDATE courses SET wallet = ? WHERE coin_name = ?', (wallet, coin))
    base.commit()


async def get_admin_wallet(coin):
    result = cur.execute('SELECT wallet FROM courses WHERE coin_name = (?)', (coin,)).fetchone()
    return result[0]



async def create_offer(state):
    async with state.proxy() as data:
        operation = data.as_dict()['operation']
        coin = data.as_dict()['coin']
        price = data.as_dict()['price']
        user_id = data.as_dict()['user_id']
        total = data.as_dict()['total']
        quantity = data.as_dict()['quantity']
        offer_date = int(time.time())
        crypto_net = data.as_dict()['crypto_net']
        wallet = data.as_dict()['wallet']
        pay_method = data.as_dict()['pay_method']
        pay_details = data.as_dict()['pay_details']
    cur.execute("""
        INSERT INTO offers 
        (user_id, datetime, operation, coin, quantity, price, total, is_completed, crypto_net, wallet, pay_method, 
        pay_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, offer_date, operation, coin, quantity, price, total, 'False', crypto_net, wallet, pay_method,
         pay_details))
    base.commit()


async def get_offers_req(is_completed):
    result = cur.execute('SELECT * FROM offers WHERE is_completed = (?)', (is_completed,)).fetchall()
    return result

async def get_offer_id(offer_id):
    result = cur.execute('SELECT * FROM offers WHERE offer_id = (?)', (offer_id,)).fetchone()
    return result


async def change_offer_status(offer_id, offer_status):
    cur.execute('UPDATE offers SET is_completed = ? WHERE offer_id = ?', (offer_status, offer_id))
    base.commit()

async def is_worktime():
    resp = cur.execute('SELECT is_worktime FROM worktime WHERE id = 1').fetchone()
    if resp[0] == 'True':
        result = True
    else:
        result = False
    return result

async def toggle_worktime_sql():
    status = await is_worktime()
    if status:
        cur.execute('UPDATE worktime SET is_worktime = "False"')
    else:
        cur.execute('UPDATE worktime SET is_worktime = "True"')
    base.commit()


