import datetime
import json
import os
import random

from nonebot import Config, get_driver
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import (Event, GroupMessageEvent,
                                         PrivateMessageEvent)
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.log import logger
from nonebot.params import CommandArg, CommandStart, EventMessage, State
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command
from nonebot.typing import T_State

from .data_source import Cave

env_config = Config(**get_driver().config.dict())
super_users = env_config.superusers
white_b_owner = env_config.white_b_owner

cave_matcher = on_command(cmd='cave')
@cave_matcher.handle()
async def cave_handle(
    bot: Bot,
    event: GroupMessageEvent,
    state: T_State = State(),
    command = CommandStart(),
    args: Message = CommandArg()
):
    cave = Cave(group_id = str(event.group_id))
    if not args :
        msg = cave.select()
        if 'error' in msg:
            await cave_matcher.finish(message = msg['error'])
        else: await cave_matcher.finish(
            message = f"回声洞 ——（{msg['cave_id']}）"
            + f"\n"
            + Message(msg["cqcode"])
            + f"\n——"
            + (await bot.get_stranger_info(user_id=msg['contributor_id']))["nickname"]
        )
    else:
        ...
