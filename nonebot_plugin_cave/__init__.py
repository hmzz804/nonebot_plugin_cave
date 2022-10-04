import json

from nonebot import Config, get_driver
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import (Event, GroupMessageEvent,
                                         PrivateMessageEvent)
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.log import logger
from nonebot.params import CommandArg, CommandStart, EventMessage, State
from nonebot.plugin import on_command
from nonebot.typing import T_State

from .data_source import Cave

env_config = Config(**get_driver().config.dict())
super_users:list = list(env_config.superusers)
white_b_owner:list = env_config.white_b_owner

#版本信息
version = """

""".strip() 

cave_matcher = on_command(cmd='cave')
@cave_matcher.handle()
async def cave_handle(
    bot: Bot,
    event: GroupMessageEvent,
    # state: T_State = State(),
    # command = CommandStart(),
    args: Message = CommandArg()
):
    cave = Cave(group_id = str(event.group_id))
    if not args:
        s_result = cave.select()
        if 'error' in s_result:
            await cave_matcher.finish(message = s_result['error'])
        else: await cave_matcher.finish(
            message = f"回声洞 ——（{s_result['cave_id']}）\n"
            + Message(s_result["cqcode"])
            + f"\n——"
            + (await bot.get_stranger_info(user_id=s_result['contributor_id']))["nickname"]
        )
    args = str(args).strip()
    if not (len(args) >= 2 and args[0] == "-") : await cave_matcher.finish(message = "参数格式有误!")
    if args[1] not in ['a','r','g','c','m','h','v','w']: await cave_matcher.finish(message = f"无法将“{args[1]}”识别为有效参数！")
    if args[1] == "a":
        cqcode:str = args.replace('-a', '', 1).strip()
        a_result = cave.add(new_content={
            'cqcode':cqcode, 
            'contributor_id':event.get_user_id(),
            'state':1})
        for i in a_result['white_B']:
            await bot.send_msg(
                message_type="private",
                user_id=i,
                message=f"待审核回声洞（{a_result['cave_id']}）"
                + f"\n"
                + Message(cqcode)
                + f"\n——{(await bot.get_stranger_info(user_id = event.get_user_id()))['nickname']}"
                + f"（{event.get_user_id()}）"
            )
        await cave_matcher.finish(message = Message(a_result['success']) )
    
    elif args[1] == "r":
        if not cave.check_wA_id(event.get_user_id()): await cave_matcher.finish(message = '无-r权限！')
        args:str = args.replace('-r', '', 1).strip()
        if not args: await cave_matcher.finish(message = "参数呢？")
        try: r_index = int(args)
        except: await cave_matcher.finish(message = "后置参数类型有误，请确保为数字")
        r_result = cave.remove(index = r_index)
        if 'error' in r_result: await cave_matcher.finish(message = r_result['error'])
        elif 'success' in r_result: await cave_matcher.finish(message = r_result['success'])
        else: logger.error("There is something wrong with Cave.remove()")

    elif args[1] == "g":
        if not cave.check_wA_id(event.get_user_id()): await cave_matcher.finish(message = '无-g权限！')
        args:str = args.replace('-g', '', 1).strip()
        if not args: await cave_matcher.finish(message = "参数呢？")
        try: g_index = int(args)
        except: await cave_matcher.finish(message = "后置参数类型有误，请确保为数字")
        g_result = cave.get_cave(index = g_index)
        if 'error' in g_result: await cave_matcher.finish(message = g_result['error'])
        else: await cave_matcher.finish(
            message = f"回声洞 ——（{g_result['cave_id']}）"
            + f"\n"
            + Message(g_result["cqcode"])
            + f"\n——"
            + (await bot.get_stranger_info(user_id = g_result['contributor_id']))["nickname"]
        )

    elif args[1] == "c":
        if event.get_user_id() not in super_users: await cave_matcher.finish(message = "无-c权限")
        args:str = args.replace("-c", "", 1).strip()
        args_list:list = args.split(" ")
        if len(args_list) != 2: await cave_matcher.finish(message = f"无法将“{args}”识别为有效参数，请注意数字和单位之间以空格分隔。")
        try: cd_num = int(args_list[0])
        except: await cave_matcher.finish(message = f"无法将“{args_list[0]}”识别为有效数字")
        if not (0 < cd_num < 500): await cave_matcher.finish(message = "冷却时间需大于0，小于500") 
        if args[1] not in ["sec","min","hour"]: await cave_matcher.finish(message = f"无法将“{args_list[1]}”识别为有效单位")
        c_result = cave.set_cd(cd_num = cd_num, cd_unit = args[1])
        if 'error' in c_result: await cave_matcher.finish(message = c_result['error'])
        elif 'success' in c_result: await cave_matcher.finish(message = c_result['success'])
        else: logger.error("There is something wrong with Cave.set_cd()")

    elif args[1] == "m":
        args:str = args.replace('-m', '', 1).strip()
        if args: await cave_matcher.finish(message = f"多余的参数“{args}”")
        m_result = cave.get_m()
        if 'error' in m_result: await cave_matcher.finish(message = m_result['error'])
        m_forward_msg = []
        for i in m_result:
            if i["state"] == 0: state_info = f"时间：{m_result['time']}。通过审核，已加入回声洞。"
            elif i["state"] == 1: state_info = f"时间：{m_result['time']}。收到投稿，等待审核。"
            elif i["state"] == 2: state_info = f"时间：{m_result['time']}。不通过审核，请检查内容后重新投稿。"
            elif i["state"] == 3: state_info = f"时间：{m_result['time']} 。已被删除。"
            else: logger.error(f"There is something wrong with state: \nA non-existent value:{i['state']}")
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
            m_forward_msg.append(every_msg) 
        await bot.send_group_forward_msg(group_id = event.group_id, messages = m_forward_msg)

    elif args[1] == "h":
        #args = args.replace('-h', '', 1).strip()
        #if not args:
        #    url = ""    #图片的url
        #    await cave_matcher.finish(message = MessageSegment.image(url))
        #else:
        #    await cave_matcher.finish(message = f"多余的参数“{args}”")
        pass

    elif args[1] == "v":
        args = args.replace('-v', '', 1).strip()
        if not args:
            await cave_matcher.finish(message = version)
        else:
            await cave_matcher.finish(message = f"多余的参数“{args}”")

    elif args[1] == "w":
        if (event.get_user_id() not in super_users) and (event.get_user_id() not in white_b_owner):
            await cave_matcher.finish(message = "无-w权限")
        args:str = args.replace('-w', '', 1).strip()
        if len(args) < 2: await cave_matcher.finish(message = '请检查参数！')
        if args[0] not in ['a','A','b','B']: await cave_matcher.finish(message = f"无法将“{args[0]}”识别为有效子命令！")
        if args[0] in ["a","A"]:
            if event.get_user_id() not in super_users: await cave_matcher.finish(message = "无cave-wA权限!")
            if args[1] == "a":
                try: wAa_id = int(args[2:])
                except:
                    wAa_msg:dict = json.loads(event.json())["message"]
                    for i in wAa_msg:
                        if i["type"] == "at":
                            wAa_id, wAa_at = i["data"]["qq"], True
                    if not wAa_at: await cave_matcher.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特!")
                wAa_id = str(wAa_id)
                wAa_result = cave.wA_add(a_id = wAa_id)
                if 'error' in wAa_result: await cave_matcher.finish(message = wAa_result['error'])
                elif 'success' in wAa_result: await cave_matcher.finish(message = wAa_result['success'])
                else: logger.error("There is something wrong with Cave.wA_add()")
            elif args[1] == "r":
                try: wAr_id = int(args[2:])
                except:
                    wAr_msg:dict = json.loads(event.json())['message']
                    for i in wAr_msg:
                        if i["type"] == "at":
                            wAr_id, wAr_at = i["data"]["qq"], True
                            break
                    if not wAr_at: await cave_matcher.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特!")
                wAr_id = str(wAr_id)
                wAr_result = cave.wA_remove(r_id = wAr_id)
                if 'error' in wAr_result: await cave_matcher.finish(message = wAr_result['error'])
                elif 'success' in wAr_result: await cave_matcher.finish(message = wAr_result['success'])
                else: logger.error("There is something wrong with Cave.wA_remove()")
            elif args[1] == "g":
                if len(args) > 2: await cave_matcher.finish(message = f'多余的参数{args[2:]}。')
                white_A:list = cave.wA_get()
                # msg = str(f"\n".join(white_A))
                wAg_msg = ""
                for i in white_A: wAg_msg += (await bot.get_stranger_info(user_id = i))["nickname"] + f"（{str(i)}）\n"
                await cave_matcher.finish(message = f"群（{event.group_id}）的白名单A：\n" + wAg_msg)
            else: await cave_matcher.finish(message = f"无法将“{args[1]}”识别为有效子命令！")
        elif args[0] in ["b","B"]:
            if event.get_user_id() not in white_b_owner: await cave_matcher.finish(message = "无cave-wA权限！")
            if args[1] == "a":
                try: wBa_id = int(args[2:])
                except:
                    wBa_msg:dict = json.loads(event.json())['message']
                    for i in wBa_msg:
                        if i["type"] == "at":
                            wBa_id, wBa_at:bool = i["data"]["qq"], True
                    if not wBa_at: await cave_matcher.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特!")
                wBa_id = str(wBa_id)
                wBa_result = cave.wB_add(a_id = wBa_id)
                if 'error' in wBa_result: await cave_matcher.finish(message = wBa_result["error"])
                elif 'success' in wBa_result: await cave_matcher.finish(message = wBa_result["success"])
                else: logger.error("There is something wrong with Cave.wB_add()")
            elif args[1] == "r":
                try: wBr_id = int(args[2:])
                except: 
                    wBr_msg:dict = json.loads(event.json())["message"]
                    for i in wBr_msg:
                        if i ["type"] == "at":
                            wBr_id, wBr_at = i["data"]["qq"], True
                            break
                    if not wBr_at: await cave_matcher.finish(message = f"无法将“{args[2:]}”识别为有效数字或艾特!")
                wBr_id = str(wBr_id)
                wBr_result = cave.wB_remove(r_id = wBr_id)
                if 'error' in wBr_result: await cave_matcher.finish(message = wBr_result['error'])
                elif 'success' in wBr_result: await cave_matcher.finish(message = wBr_result['success'])
                else: logger.error("There is something wrong with Cave.wB_remove()")
            elif args[1] == "g":
                if len(args) > 2: await cave_matcher.finish(message = f'多余的参数{args[2:]}。')
                white_B:list = cave.wB_get()
                # msg = str(f"\n".join(white_B))
                wBg_msg = ""
                for i in white_B: wBg_msg += (await bot.get_stranger_info(user_id = i))["nickname"] + f"（{str(i)}）\n" 
                await cave_matcher.finish(message = f"群（{event.group_id}）的白名单B（以下成员务必添加bot为好友）：" + wBg_msg)

async def user_checker(event: Event) -> bool:
    return event.get_user_id() in white_b_owner

setcave = on_command(cmd="setcave", rule=user_checker)
@setcave.handle()
async def setcave_handle(
    bot: Bot,
    event: PrivateMessageEvent,
    # state: T_State = State(),
    args: Message = CommandArg()
):
    cave = Cave(group_id=None)
    if not args: await setcave.finish(message = "参数呢？")
    args:str = str(args).strip()
    if not(len(args) >= 2 and args[0] =="-"): await setcave.finish(message = "参数格式有误")
    if args[1] not in ['t','f','l','e']: await setcave.finish(message = f"无法将“{args[1]}识别为有效参数")
    if args[1] == 't':
        args = args.replace("-t", "", 1).strip()
        try: t_id = int(args)
        except: await setcave.finish(message = f"无法将“{args}”识别为有效数字！")
        t_result = cave.set_t(cave_id = t_id)
        if 'error' in t_result: await setcave.finish(message = t_result['error'])
        elif 'success' in t_result: await setcave.finish(message = t_result['success'])
        else: logger.error("There is something wrong with Cave.set_t()")

    if args[1] == 'f':
        args = args.replace("-f", "", 1).strip()
        try: f_id = int(args)
        except: await setcave.finish(message = f"无法将“{args}”识别为有效数字！")
        f_result = cave.set_f(cave_id = f_id)
        if 'error' in f_result: await setcave.finish(message = f_result['error'])
        elif 'success' in f_result: await setcave.finish(message = f_result['success'])
        else: logger.error("There is something wrong with Cave.set_f()")

    if args[1] == 'l':
        args = args.replace("-l", "", 1).strip()
        if args: await setcave.finish(message = f"多余的参数“{args}”")
        l_result = cave.set_l()
        if l_result == []: await setcave.finish(message = "暂无待审核的投稿。")
        l_forward_msg = []
        for i in l_result:
            every_msg = {
                "type": "node",
                "data":{
                    "name": "投稿人",
                    "uin": event.self_id,
                    "content": f'待审核回声洞（{i["cave_id"]}）：\n'
                    + i["cqcode"]
                    + f"\n——{(await bot.get_stranger_info(user_id=i['contributor_id']))['nickname']}（{i['contributor_id']}）"
                    + f"（{i['contributor_id']}）"
                }
            }
            l_forward_msg.append(every_msg)
        await bot.send_private_forward_msg(user_id = event.get_user_id(), messages = l_forward_msg)
        await setcave.finish()

    if args[1] == 'e':
        args = args.replace("-e", "", 1).strip()
        try: e_id = int(args)
        except: await setcave.finish(message = f"无法将“{args}”识别为有效数字！")
        e_result = cave.set_e(cave_id = e_id)
        if 'error' in e_result: await setcave.finish(message = e_result['error'])
        elif 'success' in e_result: await setcave.finish(message = e_result['success'])
        else: logger.error("There is something wrong with Cave.set_e()")
