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
super_users:list = list(env_config.superusers)
white_b_owner:list[str] = env_config.white_b_owner

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
    if not args:
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
    args = str(args).strip()
    if not (len(args) >= 2 and args[0] == "-") : await cave_matcher.finish(message = "参数格式有误!")
    if args[1] == "a":
        cqcode = args.replace('-a', '', 1).strip()
        msg = cave.add(new_content={
            'cqcode':cqcode, 
            'contributor_id':event.get_user_id(),
            'state':1})
        for i in msg['white_B']:
            await bot.send_msg(
                message_type="private",
                user_id=i,
                message=f"待审核回声洞（{msg['cave_id']}）"
                + f"\n"
                + Message(cqcode)
                + f"\n——{(await bot.get_stranger_info(user_id = event.get_user_id()))['nickname']}"
                + f"（{event.get_user_id()}）"
            )
        await cave_matcher.finish(message = MessageSegment(msg['success']) )
    
    elif args[1] == "r":
        ...
    elif args[1] == "g":
        ...
    elif args[1] == "c":
        ...
    elif args[1] == "m":
        ...
    elif args[1] == "h":
        ...
    elif args[1] == "v":
        ...
    elif args[1] == "w":
        ...
    else: await cave_matcher.finish(message = f"无法将“{args[1]}”识别为有效参数")

async def user_checker(event: Event) -> bool:
    return event.get_user_id() in white_b_owner

_setcave = on_command(cmd="setcave", rule=user_checker)
@_setcave.handle()
async def _setcave_handle(
    bot: Bot,
    event: PrivateMessageEvent,
    state: T_State = State(),
    args: Message = CommandArg()
):
    cave = Cave(group_id=None)