# nonebot_plugin_cave

适用于 [Nonebot2](https://nb2.baka.icu/) 的 cave（回声洞）插件  

## 安装

<details>
<summary>nb-cli安装</summary>

在项目目录文件下运行

```
nb plugin install nonebot-plugin-cave
```

</details>

<details>
<summary>pip安装</summary>

```
pip install nonebot-plugin-cave
```

</details>


## ⭐ 介绍:  
群回声洞插件，各群友投稿加入回声洞库，可以随机抽取其中内容。
用户投稿回声洞后，会自动推送给审核人（白名单B成员）进行审核，通过审核后，才能加入库中。  


## ⚙️ 配置

在全局配置文件`.env`中添加如下
```
WHITE_B_OWNER=["qq号","qq号"]
```

> 可更改白名单B的人员，个数不限，默认为超管

## ❗注意:  
- 1.白名单B中的成员必须为bot好友，否则无法推送审核消息！  
- 2.（待补充）
## 命令:    
以下命令需要加 __命令前缀__（默认为/），可自行设置为空  
### 群聊中命令: `/cave`  

- 不含参数，正常获取cave  
- `-g [id]` :查看当前id的回声洞内容（白名单A）  
- `-r [id]` :移除该id的回声洞（白名单A）  
- `-a [内容]（支持图片，文字）` :添加回声洞  
- `-a [回复消息]` :通过回复消息添加回声洞  
- `-c [cd] [unit]` :更改当前群的冷却时间,cd为数字,unit为单位(`hour` 或 `min` 或 `sec`) **____中间以空格分隔____** （超管）   
- `-h` :获取cave参数帮助菜单和各项的用法（暂不支持）  
- `-m` :获取新增的投稿的审核情况,时间截至到上次获取  

- `-wAa [艾特/QQ号]` :添加此群的白名单A成员（超管或白名单B编辑者）   
- `-wAr [艾特/QQ号]` :移除此群的白名单A成员（超管或白名单B编辑者）  
- `-wAg` :查看此群的白名单A成员列表（超管或白名单B编辑者）  

- `-wBa [艾特/QQ号]` :添加白名单B成员（超管或白名单B编辑者）   
- `-wBr [艾特/QQ号]` :移除白名单B成员（超管或白名单B编辑者）  
- `-wBg` :查看白名单B成员列表（超管或白名单B编辑者）  

### 私聊审核命令: `/setcave`（白名单B）  
- `-t [id/all]` :通过审核   [all]:全部     
- `-f [id/all]` :不通过审核 [all]:全部  
- `-e [id]` :查看该id审核情况   
- `-l` :查看当前未审核的所有投稿   


## 冷却：
**__冷却时间长短、上次获取cave的时间,均为分群的存储,各群冷却互不影响__**  
**__每个群的白名单A成员无冷却__**

## 后记:
- 有问题可[issue](https://github.com/hmzz804/nonebot_plugin_cave/issues)或[加群](https://qm.qq.com/cgi-bin/qm/qr?k=0ooOw1C6cRLFGaw_rEcf60p6hKqojGe_&jump_from=webapi&authKey=o9g5NjKyg4lrluy9wxU8GLrK9AUCxoIFjyJqxMxuYapMwwLfKQRv9VYGZXcPPV5f)
- 欢迎pr
