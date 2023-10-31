from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

from . import __main__ as __main__
from .config import ConfigModel

require("nonebot_plugin_alconna")

__version__ = "2.0.0"
__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-cave",
    description="适用于 Nonebot2 的 cave (回声洞) 插件。",
    usage="(待完善)",
    type="application",
    homepage="https://github.com/hmzz804/nonebot_plugin_cave",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"License": "MIT", "Author": "hmzz804"},
)
