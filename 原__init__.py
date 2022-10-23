import datetime
import json
import os
import random

from nonebot import Config, get_driver
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import CommandArg
from nonebot.plugin import on_command

version = f"""
"""

CAVE_PATH = r'src/plugins/cave/cave.json'
DATA_PATH = r'src/plugins/cave/data.json'

env_config = Config(**get_driver().config.dict())
super_users = env_config.superusers
white_b_owner = env_config.white_b_owner

if not os.path.exists(CAVE_PATH):
    with open(CAVE_PATH,"w") as g:
        initialize_list = []
        json.dump(initialize_list, g, indent=4)
if not os.path.exists(DATA_PATH):
    with open(DATA_PATH,"w") as g:
        initialize_dict = {
            "groups_dict":{},
            "white_B": [],
            "total_num": 0,
            "id_num": 0
        }
        json.dump(initialize_dict, g, indent=4)

def read(path:str):
    with open(path, "r") as a:
        content = json.load(a)
    return content

def write_in(path:str,new_content) -> None :
    with open(path, 'w') as b:
        json.dump(new_content, b, indent=4)

def check_cd(cd:int, unit:str, last_time:str) -> list:
    now_time = datetime.datetime.now()
    last_time = datetime.datetime.strptime(last_time,"%Y-%m-%d %H:%M:%S.%f")
    _sec = (now_time - last_time).seconds
    _day = (now_time - last_time).days
    result = []

    if unit == "hour":
        sec_cd = cd*3600
        result.append(str(round((sec_cd-_sec)/3600,2))+unit)
        if _sec >= sec_cd or _day > 0:
            result.append(True)
        else:
            result.append(False)

    elif unit == "min":
        sec_cd = cd*60
        result.append(str(round((sec_cd-_sec)/60,1))+unit)
        if _sec >= sec_cd or _day > 0:
            result.append(True)
        else:
            result.append(False)

    elif unit == "sec":
        sec_cd = cd
        result.append(str(sec_cd-_sec)+unit)
        if _sec >= sec_cd or _day > 0:
            result.append(True)
        else:
            result.append(False)
    return result


_cave = on_command(cmd='cave')
@_cave.handle()
async def _cave_handle(
    bot: Bot,
    event: GroupMessageEvent,
    args: Message = CommandArg()
):
    cave_list = read(path=CAVE_PATH)
    data_dict = read(path=DATA_PATH)
    group_bool = False
    group_dict = data_dict["groups_dict"]
    for i in group_dict:
        if i == str(event.group_id):
            group_bool = True
            group = i
            cd_dict = group_dict[i]
            break
    if not group_bool:
        data_dict["groups_dict"][str(event.group_id)] = {
            "cd_num": 1,
            "cd_unit": "sec",
            "last_time": "1000-01-01 00:00:00.114514",
            "m_list": [],
            "white_A":[]
        }
        write_in(path = DATA_PATH, new_content = data_dict)
    if not args :
        list_bool = False
        for i in cave_list:
            if i["state"] == 0:
                list_bool = True
                break
        if cave_list and list_bool:
            if group_bool:
                check_cd_list = check_cd(
                    cd = cd_dict["cd_num"],
                    unit = cd_dict["cd_unit"],
                    last_time = cd_dict["last_time"]
                )
                if check_cd_list[1]:
                    while True:
                        send_cave = random.choice(cave_list)
                        if send_cave["state"] == 0:
                            data_dict["groups_dict"][group]["last_time"] = str(datetime.datetime.now())
                            write_in(path = DATA_PATH, new_content = data_dict)
                            await _cave.finish(
                                message = f"回声洞 ——（{send_cave['cave_id']}）"
                                + f"\n"
                                + Message(send_cave["cqcode"])
                                + f"\n——"
                                + (await bot.get_stranger_info(user_id=send_cave['contributor_id']))["nickname"]
                            )
                else:
                    await _cave.finish(message = f"cave冷却中,恁稍等{check_cd_list[0]}")
            else:
                await _cave.finish(message = "未找到此群组存储的cd信息，请超管设置此群冷却时间")
        else:
            await _cave.finish(message = "库内无内容")
    else:
        args = str(args).strip()
        if len(args) >= 2 and args[0] == "-":
            if args[1] == "a":
                args = args.replace('-a', '', 1).strip()
                if args:
                    data_dict["total_num"] += 1
                    data_dict["id_num"] += 1
                    new_element_dict = {
                        "cave_id":data_dict["id_num"],
                        "cqcode":args,
                        "contributor_id":event.get_user_id(),
                        "state":1
                    }
                    for i in data_dict["groups_dict"]:
                        data_dict["groups_dict"][i]["m_list"].append(new_element_dict)
                    cave_list.append(new_element_dict)
                    write_in(path = CAVE_PATH, new_content = cave_list)
                    write_in(path = DATA_PATH, new_content = data_dict)
                    for i in data_dict["white_B"]:
                        await bot.send_msg(
                            message_type="private",
                            user_id=i,
                            message=f"待审核回声洞（{data_dict['id_num']}）"
                            + f"\n"
                            + Message(args)
                            + f"\n"
                            + f"——{(await bot.get_stranger_info(user_id = new_element_dict['contributor_id']))['nickname']}"
                            + f"（{new_element_dict['contributor_id']}）"
                        )
                    await _cave.finish(message=f"添加成功，序号为 {data_dict['id_num']},\n来自{event.get_user_id()}")
                else:
                    await _cave.finish(message="添加失败，请检查内容格式")

            elif args[1] == "r":
                if event.get_user_id() in data_dict["groups_dict"][str(event.group_id)]["white_A"]:
                    args = args.replace('-r', '', 1).strip()
                    if args:
                        try:
                            r_index = int(args)
                        except:
                            await _cave.finish(message = "后置参数类型有误，请确保为数字")
                        r_bool = False
                        for i in cave_list:
                            if i["cave_id"] == r_index:
                                i["state"] = 3
                                r_bool = True
                                break
                        if r_bool:
                            data_dict["total_num"] -= 1
                            write_in(path = CAVE_PATH, new_content = cave_list)
                            write_in(path = DATA_PATH, new_content = data_dict)
                            await _cave.finish(
                                message = f"成功移除回声洞（{r_index}）"
                                +f""
                                +f""
                            )
                        else:
                            await _cave.finish(message = f"索引为{r_index}的内容不存在或已被删除")
                    else:
                        await _cave.finish(message = "参数呢？")
                else:
                    await _cave.finish(message = "无-r权限")

            elif args[1] == "g":
                if event.get_user_id() in data_dict["groups_dict"][str(event.group_id)]["white_A"]:
                    args = args.replace('-g', '', 1).strip()
                    if args:
                        try:
                            s_index = int(args)
                        except:
                            await _cave.finish(message = "后置参数类型有误，请确保为数字")
                        s_bool = False
                        for i in cave_list:
                            if i["cave_id"] == s_index and i["state"] == 0:
                                s_content = i
                                s_bool = True
                                break
                        if s_bool:
                            nick_name = (await bot.get_stranger_info(user_id = s_content['contributor_id']))["nickname"]
                            await _cave.finish(
                                message = f"回声洞 ——（{s_content['cave_id']}）"
                                + f"\n"
                                + Message(s_content["cqcode"])
                                + f"\n——"
                                + nick_name
                            )
                        else:
                            await _cave.finish(message = f"索引为“{s_index}”的内容不存在或已被删除或未通过审核。")
                    else:
                        await _cave.finish(message = "参数呢？")
                else:
                    await _cave.finish(message = "无-g权限")

            elif args[1] == "c":
                if event.get_user_id() in super_users:
                    args = args.replace("-c", "", 1).strip()
                    args_list = args.split(" ")
                    if len(args_list) == 2:
                        try:
                            cd_num = int(args_list[0])
                        except:
                            await _cave.finish(message = f"无法将“{args_list[0]}”识别为有效数字")
                        if args_list[1] == "sec":
                            cd_unit = str("sec")
                        elif args_list[1] == "min":
                            cd_unit = str("min")
                        elif args_list[1] == "hour":
                            cd_unit = str("hour")
                        else:
                            await _cave.finish(message = f"无法将“{args_list[1]}”识别为有效单位")
                        data_dict["groups_dict"][str(event.group_id)]["cd_num"] = cd_num
                        data_dict["groups_dict"][str(event.group_id)]["cd_unit"] = cd_unit
                        data_dict["groups_dict"][str(event.group_id)]["last_time"] = "1000-01-01 00:00:00.114514"
                        write_in(path = DATA_PATH, new_content= data_dict)
                        await _cave.finish(message = f"成功修改本群cave冷却时间为{cd_num}{cd_unit}")
                    else:
                        await _cave.finish(message = f"无法将“{args}”识别为有效参数，请注意数字和单位之间以空格分隔。")
                else:
                    await _cave.finish(message = "无-c权限")

            elif args[1] == "m":
                args = args.replace('-m', '', 1).strip()
                if not args:
                    if data_dict["groups_dict"][str(event.group_id)]["m_list"]:
                        forward_msg = []
                        for i in data_dict["groups_dict"][str(event.group_id)]["m_list"]:
                            if i["state"] == 0:
                                state_info = "通过审核，已加入回声洞。"
                            elif i["state"] == 1:
                                state_info = "待处理..."
                            elif i["state"] == 2:
                                state_info = "不通过审核，请检查内容后重新投稿。"
                            elif i["state"] == 3:
                                state_info = "已被删除。"
                            every_msg = {
                                "type": "node",
                                "data":{
                                    "name": "bot",
                                    "uin": event.self_id,
                                    "content": f'回声洞（{i["cave_id"]}）：'
                                    + f"来自——{(await bot.get_stranger_info(user_id=i['contributor_id']))['nickname']}"
                                    + f"（{i['contributor_id']}）"
                                    + f"\n"
                                    + f"状态：{state_info}"
                                }
                            }
                            forward_msg.append(every_msg)
                        data_dict["groups_dict"][str(event.group_id)]["m_list"].clear()
                        write_in(path = DATA_PATH, new_content= data_dict)
                        await bot.send_group_forward_msg(group_id=event.group_id,messages=forward_msg)
                        await _cave.finish()
                    else:
                        await _cave.finish(message = "暂无新增的回声洞处理")
                else:
                    await _cave.finish(message = f"多余的参数“{args}”")

            elif args[1] == "h":
                #args = args.replace('-h', '', 1).strip()
                #if not args:
                #    url = "https://c2cpicdw.qpic.cn/offpic_new/2166908863//2166908863-3512597815-9272CB4E118A65EC61AD470B23DECFF3/0?term=2"
                #    await _cave.finish(message = MessageSegment.image(url))
                #else:
                #    await _cave.finish(message = f"多余的参数“{args}”")
                pass

            elif args[1] == "v":
                args = args.replace('-v', '', 1).strip()
                if not args:
                    await _cave.finish(message = version)
                else:
                    await _cave.finish(message = f"多余的参数“{args}”")

            elif args[1] == "w":
                if (event.get_user_id() in super_users) or (event.get_user_id() in white_b_owner):
                    args = args.replace('-w', '', 1).strip()
                    if len(args) >= 2:
                        if args[0] in ["a","A"]:
                            if event.get_user_id() in super_users:
                                if args[1] == "a":
                                    A_a_id = args[2:]
                                    try:
                                        A_a_id = int(args[2:])
                                    except:
                                        msg_list = json.loads(event.json())["message"]
                                        for i in msg_list:
                                            if i["type"] == "at":
                                                A_a_id = i["data"]["qq"]
                                                at_bool = True
                                        if not at_bool:
                                            await _cave.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特")
                                    A_a_id = str(A_a_id)
                                    A_a_bool = False
                                    for i in data_dict["groups_dict"][str(event.group_id)]["white_A"]:
                                        if i == A_a_id:
                                            A_a_bool = True
                                            break
                                    if not A_a_bool:
                                        data_dict["groups_dict"][str(event.group_id)]["white_A"].append(A_a_id)
                                        write_in(path = DATA_PATH, new_content = data_dict)
                                        await _cave.finish(message = f"成功将“{A_a_id}”添加到群（{event.group_id}）的白名单A中！")
                                    else:
                                        await _cave.finish(message = f"“{A_a_id}”已在群（{event.group_id}）的白名单A中！")

                                elif args[1] == "r":
                                    try:
                                        A_r_id = int(args[2:])
                                    except:
                                        msg_list = json.loads(event.json())["message"]
                                        for i in msg_list:
                                            if i["type"] == "at":
                                                A_r_id = i["data"]["qq"]
                                                at_bool = True
                                        if not at_bool:
                                            await _cave.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特")
                                    A_r_id = str(A_r_id)
                                    A_r_bool = False
                                    for i in data_dict["groups_dict"][str(event.group_id)]["white_A"]:
                                        if i == A_r_id:
                                            data_dict["groups_dict"][str(event.group_id)]["white_A"].remove(i)
                                            A_r_bool = True
                                            break
                                    if A_r_bool:
                                        write_in(path = DATA_PATH, new_content = data_dict)
                                        await _cave.finish(message = f"成功将“{A_r_id}”移出群（{event.group_id}）的白名单A")
                                    else:
                                        await _cave.finish(message = f"未在群（{event.group_id}）的白名单A中找到“{A_r_id}”，请检查后重试。")

                                elif args[1] == "g":
                                    if len(args) == 2:
                                        white_A = ""
                                        for i in data_dict["groups_dict"][str(event.group_id)]["white_A"]:
                                            white_A += (await bot.get_stranger_info(user_id = i))["nickname"] + f"（{str(i)}）\n"
                                        await _cave.finish(
                                            message = f"群（{event.group_id}）的白名单A："
                                            + f"\n"
                                            + white_A
                                        )
                                    else:
                                        await _cave.finish(message = f"多余的参数“{args[2:]}”")
                                else:
                                    await _cave.finish(message = f"无法将“{args[1]}”识别为有效子命令")
                            else:
                                await _cave.finish(message = "无.cave-wA权限")
                        elif args[0] in ["b","B"]:
                            if event.get_user_id() in white_b_owner:
                                if args[1] == "a":
                                    try:
                                        B_a_id = int(args[2:])
                                    except:
                                        msg_list = json.loads(event.json())["message"]
                                        for i in msg_list:
                                            if i["type"] == "at":
                                                B_a_id = i["data"]["qq"]
                                                at_bool = True
                                        if not at_bool:
                                            await _cave.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特")
                                    B_a_id = str(B_a_id)
                                    B_a_bool = False
                                    for i in data_dict["white_B"]:
                                        if i == B_a_id:
                                            B_a_bool = True
                                            break
                                    if not B_a_bool:
                                        data_dict["white_B"].append(B_a_id)
                                        write_in(path = DATA_PATH, new_content = data_dict)
                                        await _cave.finish(message = f"成功将“{B_a_id}”添加到白名单B")
                                    else:
                                        await _cave.finish(message = f"“{B_a_id}”已在白名单B中！")

                                elif args[1] == "r":
                                    try:
                                        B_r_id = int(args[2:])
                                    except:
                                        msg_list = json.loads(event.json())["message"]
                                        for i in msg_list:
                                            if i["type"] == "at":
                                                B_r_id = i["data"]["qq"]
                                                at_bool = True
                                        if not at_bool:
                                            await _cave.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特")
                                    B_r_id = str(B_r_id)
                                    B_r_bool = False
                                    for i in data_dict["white_B"]:
                                        if i == B_r_id:
                                            data_dict["white_B"].remove(i)
                                            B_r_bool = True
                                            break
                                    if B_r_bool:
                                        write_in(path = DATA_PATH, new_content = data_dict)
                                        await _cave.finish(message = f"成功将“{B_r_id}”移出白名单B")
                                    else:
                                        await _cave.finish(message = f"未在白名单B中找到“{B_r_id}”，请检查后重试。")

                                elif args[1] == "g":
                                    if len(args) == 2:
                                        white_B = ""
                                        for i in data_dict["white_B"]:
                                            white_B += (await bot.get_stranger_info(user_id = i))["nickname"] + f"（{str(i)}）\n"
                                        await _cave.finish(
                                            message = "白名单B（以下人员务必添加bot为好友，否则无法接收推送消息）："
                                            + f"\n"
                                            + white_B
                                        )
                                    else:
                                        await _cave.finish(message = f"多余的参数“{args[2:]}”")
                                else:
                                    await _cave.finish(message = f"无法将“{args[1]}”识别为有效子命令")
                            else:
                                await _cave.finish(message = "无.cave-wB权限")
                        else:
                            await _cave.finish(message = f"无法将“{args[0]}”识别为有效子命令")
                    else:
                        await _cave.finish(message = "参数呢")
                else:
                    await _cave.finish(message = "无-w权限")
            else:
                await _cave.finish(message = f"无法将“{args[1]}”识别为有效参数")
        #else:
            #await _cave.finish(message = "参数格式有误（1）")

setcave = on_command(cmd="setcave")
@setcave.handle()
async def setcave_handle(
    bot: Bot,
    event: PrivateMessageEvent,
    args: Message = CommandArg()
):
    cave_list = read(path = CAVE_PATH)
    data_dict = read(path = DATA_PATH)
    if event.get_user_id() in data_dict["white_B"]:
        if args:
            args = str(args).strip()
            if len(args) >= 2 and args[0] =="-":
                if args[1] == "t":
                    args = args.replace("-t", "", 1).strip()
                    if args:
                        try:
                            args = int(args)
                        except:
                            await setcave.finish(message = f"无法将“{args}”识别为有效数字")
                        t_code = int(4)
                        for i in cave_list:
                            if i["cave_id"] == args:
                                setcave_t_m_dict = i
                                if i["state"] == 0:
                                    t_code = int(0)
                                elif i["state"] == 1:
                                    i["state"] = 0
                                    t_code = int(1)
                                elif i["state"] == 2:
                                    t_code = int(2)
                                elif i["state"] == 3:
                                    t_code = int(3)
                                for i in data_dict["groups_dict"]:
                                    if setcave_t_m_dict not in data_dict["groups_dict"][i]["m_list"]:
                                        data_dict["groups_dict"][i]["m_list"].append(setcave_t_m_dict)
                                break
                        write_in(path = CAVE_PATH, new_content = cave_list)
                        write_in(path = DATA_PATH, new_content = data_dict)
                        if t_code == 0:
                            await setcave.finish(message = f"（{args}）已被其他审核员通过审核。")
                        elif t_code == 1:
                            await setcave.finish(message = f"操作成功，序号:({args})通过审核，加入回声洞。")
                        elif t_code == 2:
                            await setcave.finish(message = f"（{args}）已被其他审核员不通过审核。")
                        elif t_code == 3:
                            await setcave.finish(message = f"（{args}）已被删除。")
                        elif t_code == 4:
                            await setcave.finish(message = f"不存在的序号：{args}")
                        else:
                            await setcave.finish(message = "发生了未知错误，请联系作者反馈。")
                    else:
                        await setcave.finish(message = "参数呢？")

                elif args[1] == "f":
                    args = args.replace("-f", "", 1).strip()
                    if args:
                        try:
                            args = int(args)
                        except:
                            await setcave.finish(message = f"无法将“{args}”识别为有效数字。")
                        f_code = int(4)
                        for i in cave_list:
                            if i["cave_id"] == args:
                                setcave_f_m_dict = i
                                if i["state"] == 0:
                                    f_code = int(0)
                                elif i["state"] == 1:
                                    i["state"] = 2
                                    f_code = int(1)
                                elif i["state"] == 2:
                                    f_code = int(2)
                                elif i["state"] == 3:
                                    f_code = int(3)
                                for i in data_dict["groups_dict"]:
                                    if setcave_f_m_dict not in data_dict["groups_dict"][i]["m_list"]:
                                        data_dict["groups_dict"][i]["m_list"].append(setcave_f_m_dict)
                                break
                        write_in(path = CAVE_PATH, new_content = cave_list)
                        write_in(path = DATA_PATH, new_content = data_dict)
                        if f_code == 0:
                            await setcave.finish(message = f"（{args}）已被其他审核员通过审核。")
                        elif f_code == 1:
                            await setcave.finish(message = f"操作成功，序号:({args})不通过审核。")
                        elif f_code == 2:
                            await setcave.finish(message = f"（{args}）已被其他审核员不通过审核。")
                        elif f_code == 3:
                            await setcave.finish(message = f"（{args}）已被删除。")
                        elif f_code == 4:
                            await setcave.finish(message = f"不存在的序号：{args}")
                        else:
                            await setcave.finish(message = f"发生了未知错误，请联系作者反馈")
                    else:
                        await setcave.finish(message = "参数呢")
                elif args[1] == "l":
                    args = args.replace("-l", "", 1).strip()
                    if not args:
                        forward_msg = []
                        for i in cave_list:
                            if i["state"] == 1:
                                every_msg = {
                                    "type": "node",
                                    "data":{
                                       "name": "投稿人",
			                            "uin": event.self_id,
			                            "content": f'待审核回声洞（{i["cave_id"]}）：'
                                        + f"\n"
                                        + i["cqcode"]
                                        + f"\n"
                                        + f"——{(await bot.get_stranger_info(user_id=i['contributor_id']))['nickname']}（{i['contributor_id']}）"
                                        + f"（{i['contributor_id']}）"
                                    }
                                }
                                forward_msg.append(every_msg)
                        await bot.send_private_forward_msg(user_id=event.user_id,messages=forward_msg)
                        await setcave.finish()
                    else:
                        await setcave.finish(message=f"多余的参数“{args}”")

                elif args[1] == "e":
                    pass
                
                else:
                    await setcave.finish(message = f"无法将“{args[1]}识别为有效参数")
            else:
                await setcave.finish(message="参数格式有误")
        else:
            await setcave.finish(message="参数呢")
    else:
        await setcave.finish(message = "无权限")


