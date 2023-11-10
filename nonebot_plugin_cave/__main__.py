from nonebot.adapters import Event, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import on_command

from nonebot_plugin_saa import MessageFactory, Text

from . import __version__

# region command register
# TODO: 使用更好的办法进行指令注册。
cave_main = on_command("cave")
cave_add = on_command("cave-a")
cave_remove = on_command("cave-r")
cave_set_cd = on_command("cave-c")
cave_manage = on_command("cave-m")
cave_whitelist = on_command("cave-w")
cave_help = on_command("cave-h")
cave_get = on_command("cave-g")
cave_version = on_command("cave-v")
# endregion


# region handlers
@cave_main.handle()
async def _(event: Event, matcher: Matcher):
    pass


@cave_get.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    pass


@cave_add.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    pass


@cave_remove.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    pass


@cave_set_cd.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    pass


@cave_manage.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    pass


@cave_whitelist.handle()
async def _(event: Event, matcher: Matcher, message: Message = CommandArg()):
    pass


@cave_help.handle()
async def _(event: Event, matcher: Matcher):
    pass


@cave_version.handle()
async def _(event: Event, matcher: Matcher):
    MessageFactory([Text(f"当前的 nonebot-plugin-cave 版本为: {__version__}")]).send(
        reply=True
    )


# endregion
