# nonebot_plugin_cave

适用于 [Nonebot2](https://v2.nonebot.dev) 的 cave (回声洞) 插件

## 📖 介绍
群回声洞插件，各群友投稿加入回声洞库，可以随机抽取其中内容。
用户投稿回声洞后，会自动推送给审核人 (白名单 B 成员) 进行审核，通过审核后，才能加入库中。  

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>

在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```
nb plugin install nonebot-plugin-cave
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-cave
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-cave
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-cave
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-cave
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_cave"
]
```
</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| WHITE_B_OWNER | 是 | 无 | 填写 QQ 号, 如 `["123", "321"]` |

> 可更改白名单 B 的人员，个数不限，默认为 `SUPERUSERS`。

## ❗ 注意:  

- 白名单 B 中的成员必须为 Bot 好友，否则无法推送审核消息! 

## 🎉 使用

以下命令需要加 __命令前缀__（默认为 `/`），可自行设置为空

### 群聊中命令 `/cave`

- 不含参数，正常获取回声洞
- `-g [id]`: 查看当前 ID 的回声洞内容 (最低权限: 白名单A)  
- `-r [id]`: 移除该 ID 的回声洞 (最低权限: 白名单 A)  
- `-a [内容] (支持图片，文字)`: 添加回声洞 
- `-a [回复消息]`: 通过回复消息添加回声洞
- `-c [cd] [unit]`: 更改当前群的冷却时间, `cd` 为数字, `unit` 为单位 (`hour` 或 `min` 或 `sec`) **____中间以空格分隔____** (最低权限: `SUPERUSER`)
- `-h`: 获取回声洞参数帮助菜单和各项的用法 (暂不支持)
- `-m`: 获取新增的投稿的审核情况,时间截至到上次获取  

- `-wAa [艾特/QQ 号]`: 添加此群的白名单 A 成员 (最低权限: 超管或白名单 B 编辑者)
- `-wAr [艾特/QQ 号]`: 移除此群的白名单 A 成员 (最低权限: 超管或白名单 B 编辑者)
- `-wAg`: 查看此群的白名单 A 成员列表 (最低权限: 超管或白名单 B 编辑者)

- `-wBa [艾特/QQ 号]` :添加白名单 B 成员 (最低权限: 超管或白名单 B 编辑者)
- `-wBr [艾特/QQ 号]` :移除白名单 B 成员 (最低权限: 超管或白名单 B 编辑者)
- `-wBg` :查看白名单 B 成员列表 (最低权限: 超管或白名单 B 编辑者)

### 私聊审核命令 `/setcave` (最低权限: 白名单 B)  
- `-t [id/all]`: 通过审核 ([all]: 全部)  
- `-f [id/all]`: 不通过审核 ([all]: 全部)
- `-e [id]`: 查看该 ID 审核情况
- `-l`: 查看当前未审核的所有投稿

> **冷却说明**
> 
> 冷却时间长短、上次获取回声洞的时间, 均分开存储, 各群冷却互不影响
> 
> **敬请注意** 每个群的白名单 A 成员无冷却

## 反馈问题
- [新提交一个 Issue](https://github.com/hmzz804/nonebot_plugin_cave/issues/new)
- [加入 QQ 群聊](https://qm.qq.com/cgi-bin/qm/qr?k=0ooOw1C6cRLFGaw_rEcf60p6hKqojGe_&jump_from=webapi&authKey=o9g5NjKyg4lrluy9wxU8GLrK9AUCxoIFjyJqxMxuYapMwwLfKQRv9VYGZXcPPV5f)
- [Fork 本仓库](https://github.com/hmzz804/nonebot_plugin_cave/fork) 并进行修改后 [提交 Pull Request](https://github.com/hmzz804/nonebot_plugin_cave/compare)
