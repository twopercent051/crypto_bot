import typing
from aiogram.dispatcher.filters import BoundFilter
from tgbot.models import db_connector


class LogFilter(BoundFilter):
    key = 'is_loged'

    def __init__(self, is_loged: typing.Optional[bool] = None):
        self.is_loged = is_loged

    async def check(self, obj):
        if self.is_loged is None:
            return False
        loged_users = await db_connector.get_users()
        return (obj.from_user.id in loged_users) == self.is_loged


class BlockFilter(BoundFilter):
    key = 'is_blocked'

    def __init__(self, is_blocked: typing.Optional[bool] = None):
        self.is_blocked = is_blocked

    async def check(self, obj):
        if self.is_blocked is None:
            return False
        blocked_users = await db_connector.filter_block_filter()
        print(blocked_users)
        return (obj.from_user.id in blocked_users) == self.is_blocked


class WorktimeFilter(BoundFilter):
    key = 'is_workout'

    def __init__(self, is_workout: typing.Optional[bool] = None):
        self.is_workout = is_workout

    async def check(self, obj):
        if self.is_workout is None:
            return False
        is_worktime = await db_connector.is_worktime()
        return (is_worktime == False)
