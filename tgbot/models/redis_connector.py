import redis

from create_bot import config


r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)

def redis_start():
    r.set('is_working', 'True')
    print('Redis connected OK')

async def toggle_working():
    response = r.get('is_working').decode('utf-8')
    if response == 'True':
        r.set('is_working', 'False')
    else:
        r.set('is_working', 'True')

async def is_working():
    response = r.get('is_working').decode('utf-8')
    if response == 'True':
        status = True
    else:
        status = False
    return status