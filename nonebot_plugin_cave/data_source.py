import json
import os
import random
import urllib.request
from datetime import datetime
from pathlib import Path

import requests


class Cave():
    def __init__(self, **data) -> None:
        # 路径
        self.data_path = Path(r"data/cave/data.json").absolute()
        self.cave_path = Path(r"data/cave/cave.json").absolute()
        # 路径文件夹
        self.dir = Path(r"data/cave").absolute()
        self.pic_dir = Path(r"data/cave/pictures").absolute()
        self.dir.mkdir(parents=True, exist_ok=True)
        self.pic_dir.mkdir(parents=True, exist_ok=True)
        # 初始化属性
        self.cave: list[dict] = []
        self.data: dict = {}

        self.is_group = False
        try:
            self.white_b_owner:list = data['white_b_owner']
            self.super_users:list = data['super_users']
            self.group_id:str = data['group_id']
            self.is_group = True
        except:
            pass
        self.load()

    def load(self):
        """读取`cave.json`,`data.json`"""
        if self.data_path.exists() and self.data_path.is_file():
            with self.data_path.open("r") as f:
                self.data: dict = json.load(f)
        else:
            with self.data_path.open("w") as f:
                initialize_dict = {
                    "groups_dict":{},
                    "white_B":self.white_b_owner,
                    "total_num": 0,
                    "id_num": 0
                    }
                json.dump(initialize_dict, f, indent=4)
            self.load()
        if self.cave_path.exists() and self.cave_path.is_file():
            with self.cave_path.open("r") as f:
                self.cave: list[dict] = json.load(f)
        else:
            with self.cave_path.open("w") as f:
                initialize_list = []
                json.dump(initialize_list, f, indent=4)
            self.load()
        if self.is_group:
            if (self.group_id not in self.data['groups_dict']) and self.group_id:
                self.data["groups_dict"][self.group_id] = {
                    "cd_num": 1,
                    "cd_unit": "sec",
                    "last_time": "1000-01-01 00:00:00.114514",
                    "m_list": [],
                    "white_A":[]
                }
        self.save()

    def save(self) -> None:
        """保存`cave.json`,`data.json`"""
        with self.data_path.open('w') as f:
            json.dump(self.data, f, indent=4)
        with self.cave_path.open('w') as f:
            json.dump(self.cave, f, indent=4)

    def check_path(self) -> bool:
        '''检查是否包含存储数据的路径'''
        return self.data_path.exists() and self.data_path.is_file() \
            and self.cave_path.exists() and self.data_path.is_file()

    def whether_id(self, id:int) -> bool:
        '''检查是否有此id'''
        result = False
        for i in self.cave:
            if i['cave_id'] == id:
                result =True
                break
        return result

    def check_wA_id(self, id:str) -> bool:
        '''检查白名单A中是否有指定id'''
        return id in [i for i in self.data["groups_dict"][self.group_id]["white_A"]]

    def check_wB_id(self, id:str) -> bool:
        '''检查白名单B中是否有指定id'''
        return id in [i for i in self.data["white_B"]]

    def check_id_state(self, id:int, change_state:int) -> bool:
        '''
        检查要操作的id的状态,并将传入的id的state改为change_state\\
        state值的意义：
            state 0 : 通过审核，可正常获取
            state 1 : 待审核
            state 2 : 未通过审核
            state 3 : 被-r删除
        '''
        for i in self.cave:
            if i['cave_id'] == id:
                result = (i['state'] == 1)
                if change_state != None : i['state'] = change_state
                self.save()
                return result
        return False

    def check_cd(self, cd:int, unit:str, last_time:str) -> list:
        '''
        检查cd情况\\
        参数：  
            cd : 冷却时间的数字
            unit : 冷却时间的单位
            last_time : 上次使用时间
        返回列表：  
            第0项(str):现在时间与上次时间的差值字符串
            第1项(bool):cd是否已过
        '''
        now_time = datetime.now()
        last_time = datetime.strptime(last_time,"%Y-%m-%d %H:%M:%S.%f")
        dif_sec, dif_day = (now_time - last_time).seconds, (now_time - last_time).days
        if unit == "hour":
            sec_cd = cd*3600
            result = str(round((sec_cd-dif_sec)/3600,2))+unit
            if dif_sec >= sec_cd or dif_day > 0:
                return [result, True]
            else:
                return [result, False]
        elif unit == "min":
            sec_cd = cd*60
            result = str(round((sec_cd-dif_sec)/60,1))+unit
            if dif_sec >= sec_cd or dif_day > 0:
                return [result, True]
            else:
                return [result, False]
        elif unit == "sec":
            sec_cd = cd
            result = str(sec_cd-dif_sec)+unit
            if dif_sec >= sec_cd or dif_day > 0:
                return [result, True]
            else:
                return [result,False]

    def print_all(self) -> None:
        '''打印data,cave'''
        with self.data_path.open('r') as f:
            print(f.read())
        with self.cave_path.open('r') as f:
            print(f.read())
        print(self.data)
        print(self.cave)

    def get_url_extension(self, url:str) -> str:
        '''获取url的图片的扩展名'''
        with urllib.request.urlopen(url=url) as response:
            info = response.info()
            return info.get_content_subtype()

    def down_load(self, url:str, save_path:Path) -> None:
        '''下载图片'''
        r = requests.get(url)
        with save_path.open("wb") as f:
            f.write(r.content)

    def select(self, check_cd:bool) -> dict:
        '''
        抽取cave \\
        参数:
            check_cd : 是否需要校验冷却时间
        返回要发送的消息的部分内容
        '''
        if (0 not in list(i['state']  for i in self.cave) ) or \
            self.cave == []:
            return {
                'error':'库内暂无内容。'
            }   
        if check_cd:
            check_cd_result = self.check_cd(
                cd = self.data["groups_dict"][self.group_id]["cd_num"],
                unit = self.data["groups_dict"][self.group_id]["cd_unit"],
                last_time = self.data["groups_dict"][self.group_id]["last_time"]
            )
            if not check_cd_result[1]:
                return {
                    'error':f"cave冷却中,恁稍等{check_cd_result[0]}"
                }
        while True:
            send_msg = random.choice(self.cave)
            if send_msg["state"] == 0:
                if check_cd:
                    self.data["groups_dict"][self.group_id]["last_time"] = str(datetime.now())
                    self.save()
                return send_msg
    
    def add(self, message:list, contributor_id:str, state:int) -> dict:
        '''
        添加cave \\
        参数：
            message: 投稿内容的消息段列表
            contributor_id: 投稿人QQ号
            state: 状态码
        返回要发送的消息的部分内容\\
        state值的意义：
            state 0 : 通过审核，可正常获取
            state 1 : 待审核
            state 2 : 未通过审核
            state 3 : 被-r删除
        '''
        #id存储部分，待改
        self.data["total_num"] += 1
        self.data["id_num"] += 1
        cave_id = self.data['id_num']

        pic_num = 0
        for i in message:
            if i['type'] == 'image':
                pic_num += 1
                url = i['data']['url']
                file_extension = self.get_url_extension(url=url)
                save_path = Path(self.pic_dir, f'{cave_id}_{pic_num}.{file_extension}')
                self.down_load(url=url, save_path=save_path)
                i.pop('data')
                i['path'] = str(save_path)
            elif i['type'] == 'text':
                text = i['data']['text']
                i.pop('data')
                i['text'] = text

        for i in self.data["groups_dict"]:
            self.data["groups_dict"][i]["m_list"].append(
                {
                    'cave_id':cave_id,
                    'state':state,
                    'contributor_id':contributor_id,
                    'time':str(datetime.now())
                }
            )
        self.cave.append(
            {
                'cave_id':cave_id,
                'message':message,
                'contributor_id':contributor_id,
                'state':state
            }
        )
        self.save()
        return {
            'success':f'添加成功，序号为 {cave_id}，\n来自{contributor_id}',
            'white_B':self.data['white_B'],
            'cave_id':cave_id
        }

    def remove(self, index:int) -> dict:
        '''
        移除cave
            index : 序号
        '''
        if not self.whether_id(id=index):
            return {
                'error':f"索引为“{index}”的内容不存在或已被删除。"
            }
        for i in self.data["groups_dict"]:
            self.data["groups_dict"][i]["m_list"].append(
                {
                    'cave_id':index,
                    'state':3,
                    'contributor_id':self.get_cave(index=index)['contributor_id'],
                    'time':str(datetime.now())
                }
            )
        for i in self.cave:
            if i['cave_id'] == index:
                deleted = i
                self.cave.remove(i)
        self.save()
        # 删除本地存储关于此回声洞的图片
        for i in deleted['message']:
            if i['type'] == 'image':
                os.remove(path=i['path'])
        return {
            'success':'删除成功！'
        }

    def get_cave(self, index:int) -> dict:
        '''
        查看cave
            index : 序号
        '''
        if not self.whether_id(id=index):
            return {
                'error':f'索引为“{index}”的内容不存在或已被删除。'
            }
        for i in self.cave:
            if i['cave_id'] == index:
                return i
    
    def set_cd(self, cd_num:int, cd_unit:str) -> dict:
        '''
        设置群冷却时间
            cd_num : 冷却时间的数字
            cd_unit : 冷却时间的单位('sec','min','hour')
        '''
        if cd_unit not in ['sec','min','hour']:
            return {
                'error':f'无法将“{cd_unit}”识别为有效单位'
            }
        if not(0 < cd_num < 500):
            return {
                'error':'冷却时间需大于0，小于500'
            }
        self.data["groups_dict"][self.group_id]["cd_num"] = cd_num
        self.data["groups_dict"][self.group_id]["cd_unit"] = cd_unit
        self.data["groups_dict"][self.group_id]["last_time"] = "1000-01-01 00:00:00.114514"
        self.save()
        return {
            'success':f'成功修改本群cave冷却时间为{cd_num}{cd_unit}'
        }

    def get_recent(self) -> list:
        '''
        获取新增的投稿的审核情况，时间截至到上次获取\\
        返回信息列表，并在文件中清除
        '''
        m_info = self.data["groups_dict"][self.group_id]["m_list"]
        if m_info == [] :
            return {
                'error':'暂无新增的回声洞处理'
            }
        self.data["groups_dict"][self.group_id]["m_list"] = []
        self.save()
        return m_info

    def wA_add(self, a_id:str) -> dict:
        '''
        添加白名单A成员
            a_id : 添加的账号
        返回结果
        '''
        if self.check_wA_id(id=a_id): return {'error':f'此账号已在群“{self.group_id}”的白名单A中！'}
        else:
            self.data["groups_dict"][self.group_id]["white_A"].append(a_id)
            self.save()
            return {
                'success':f'成功将账号“{a_id}”添加到群“{self.group_id}”的白名单A中！'
            }

    def wA_remove(self, r_id:str) -> dict:
        '''
        删除白名单A成员
            r_id : 删除的账号
        返回结果
        '''
        if self.check_wA_id(id=r_id): 
            self.data["groups_dict"][self.group_id]["white_A"].remove(r_id)
            self.save()
            return {
                'success':f'成功将账号“{r_id}”移出群“{self.group_id}”的白名单A！'
            }
        else: 
            return {
                'error':f'账号“{r_id}”不在群“{self.group_id}”的白名单A中！'
            }

    def wA_get(self) -> list:
        '''获取当前群的白名单A的成员列表'''
        return self.data["groups_dict"][self.group_id]["white_A"]

    def wB_add(self, a_id) -> dict:
        '''
        添加白名单B成员
            a_id : 添加的账号
        返回结果
        '''
        if self.check_wB_id(id=a_id):
            return {
                'error':f'此账号已在群“{self.group_id}”的白名单B中！'
            }
        else:
            self.data["white_B"].append(a_id)
            self.save()
            return {
                'success':f'成功将账号“{a_id}”添加到的白名单B中！'
            }

    def wB_remove(self, r_id) -> dict:
        '''
        删除白名单B成员
            r_id : 删除的账号
        返回结果
        '''
        if  self.check_wB_id(id=r_id):
            self.data["white_B"].remove(r_id)
            self.save()
            return {
                'success':f'成功将账号“{r_id}”移出白名单B！'
            }
        else:
            return {
                'error':f'账号“{r_id}”不在白名单B中'
            }

    def wB_get(self) -> list:
        '''
        获取当前的白名单B的成员列表
        '''
        return self.data["white_B"]

    def set_true(self, cave_id:int) -> dict:
        '''通过审核'''
        if self.check_id_state(id=cave_id, change_state=0):
            for i in self.data["groups_dict"]:
                self.data["groups_dict"][i]["m_list"].append(
                    {
                        'cave_id':cave_id,
                        'state':0,
                        'contributor_id':self.get_cave(index=cave_id)['contributor_id'],
                        'time':str(datetime.now())
                    }
                )
            self.save()
            return {
                'success':f'操作成功，序号:({cave_id})通过审核，加入回声洞。'
            }
        else:
            return {
                'error':'此序号不存在或已被删除或已被审核！'
            }

    def set_true_all(self) -> None:
        '''当前待审核内容全部通过审核'''
        for i in self.get_waiting_caves():
            self.set_true(cave_id=i['cave_id'])

    def set_false(self, cave_id:int) -> dict:
        '''不通过审核'''
        if self.check_id_state(id=cave_id, change_state=None):
            for i in self.data["groups_dict"]:
                self.data["groups_dict"][i]["m_list"].append(
                    {
                        'cave_id':cave_id,
                        'state':2,
                        'contributor_id':self.get_cave(index=cave_id)['contributor_id'],
                        'time':str(datetime.now())
                    }
                )
            for i in self.cave:
                if i['cave_id'] == cave_id:
                    self.cave.remove(i)
                    self.save()
            self.save()
            return {
                'success':f'操作成功，序号:({cave_id})不通过审核，已将其删除。'
            }
        else:
            return {
                'error':'此序号不存在或已被删除或已被审核！'
            }
    
    def set_false_all(self) -> None:
        '''当前待审核内容全部不通过审核'''
        for i in self.get_waiting_caves():
            self.set_false(cave_id=i['cave_id'])

    def get_waiting_caves(self) -> list:
        '''返回当前未处理的审核序号列表'''
        msg = []
        for i in self.cave:
            if i['state'] == 1:
                msg.append(i)
        return msg

    def get_state(self, cave_id:int) -> dict:
        '''
        返回此id的审核情况\\
        state值的意义：
            state 0 : 通过审核，可正常获取
            state 1 : 待审核
            state 2 : 未通过审核
            state 3 : 被-r删除
        '''
        if self.check_id_state(id = cave_id, change_state = None):
            for i in self.cave:
                if i['cave_id'] == cave_id:
                    return {
                        'success':i['state']
                    }
        else:
            return {
                'error':'此序号不存在或已被删除或已被审核'
            }
