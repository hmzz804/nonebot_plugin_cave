import datetime
import json
import random
from pathlib import Path
from typing import Dict, List

class Cave():
    def __init__(self, group_id:str) -> None:
        # 路径
        self.data_path = Path(r"data/cave/data.json").absolute()
        self.cave_path = Path(r"data/cave/cave.json").absolute()
        # 路径文件夹
        self.dir = Path(r"data/cave").absolute()
        self.dir.mkdir(parents=True, exist_ok=True)
        # 初始化属性
        self.__cave: List[dict] = []
        self.__data: Dict = {}
        self.__group_id: str = group_id
        self.__load()

    def __load(self):
        """
        读取`cave.json`,`data.json`
        """
        if self.check_path():
            with self.data_path.open("r") as f:
                self.__data: Dict = json.load(f)
            with self.cave_path.open("r") as f:
                self.__cave: List[dict] = json.load(f)
        else:
            with self.data_path.open("w") as f:
                initialize_dict = {
                    "groups_dict":{},
                    "white_B": [],
                    "total_num": 0,
                    "id_num": 0
                }
                json.dump(initialize_dict, f, indent=4)
            with self.cave_path.open("w") as f:
                initialize_list = []
                json.dump(initialize_list, f, indent=4)
            self.__load()
        if self.__group_id not in self.__data['groups_dict']:
            self.__data["groups_dict"][self.__group_id] = {
                "cd_num": 1,
                "cd_unit": "sec",
                "last_time": "1000-01-01 00:00:00.114514",
                "m_list": [],
                "white_A":[]
            }
        self.__save()

    def __save(self):
        """
        保存`cave.json`,`data.json`
        """
        with self.data_path.open('w') as f:
            json.dump(self.__data, f, indent=4)
        with self.cave_path.open('w') as f:
            json.dump(self.__cave, f, indent=4)

    def check_path(self) -> bool:
        '''
        检查是否包含存储数据的路径
        '''
        return self.data_path.exists() and self.data_path.is_file() \
            and self.cave_path.exists() and self.data_path.is_file()

    def check_wA_id(self, id:str) -> bool:
        '''
        检查白名单A中是否有指定id
        '''
        return id in [i for i in self.__data["groups_id"][self.__group_id]["white_A"]]

    def check_wB_id(self, id:str) -> bool:
        '''
        检查白名单B中是否有指定id
        '''
        return id in [i for i in self.__data["white_B"]]

    def check_set_id(self, id:int, change_state:int) -> bool:
        '''
        检查要操作的id的状态,并将传入的id的state改为change_state\\
        state值的意义：
            state 0 : 通过审核，可正常获取
            state 1 : 待审核
            state 2 : 未通过审核
            state 3 : 被-r删除
        '''
        for i in self.__cave:
            if i['cave_id'] == id:
                if change_state != None : i['state'] = change_state
                self.__save()
                return i['state'] == 1
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
        now_time = datetime.datetime.now()
        last_time = datetime.datetime.strptime(last_time,"%Y-%m-%d %H:%M:%S.%f")
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

    def print_all(self):
        '''
        打印读取`data文件`,`cave文件`
        '''
        with self.data_path.open('r') as f:
            print(f.read())
        with self.cave_path.open('r') as f:
            print(f.read())
        print(self.__data)
        print(self.__cave)

    def select(self) -> dict:
        '''
        抽取cave \\
        返回要发送的消息的部分内容
        '''
        if (0 not in list(i['state']  for i in self.__cave) ) or \
            self.__cave == []:
            return {'error':'库内暂无内容。'}
        check_cd_result = self.check_cd(self.__data)
        if not check_cd_result[1]:
            return {'error':f"cave冷却中,恁稍等{check_cd_result[0]}"}
        while True:
            send_msg = random.choice(self.__cave)
            if send_msg["state"] == 0:
                self.__data["groups_dict"][self.__group_id]["last_time"] = str(datetime.datetime.now())
                self.__save()
                return send_msg
    
    def add(self, new_content:dict) -> dict:
        '''
        添加cave \\
        参数：
            new_content : 新添加的内容(dict),
                需包含字段: `cqcode:str`, `contributor_id:str`, `state:int`
        返回要发送的消息的部分内容\\
        state值的意义：
            state 0 : 通过审核，可正常获取
            state 1 : 待审核
            state 2 : 未通过审核
            state 3 : 被-r删除
        '''
        try:
            cqcode = new_content['cqcode']
            contributor_id = new_content['contributor_id']
            state = new_content['state']
        except Exception as e: raise KeyError('Missing parameter in Cave.add', e)
        self.__data["total_num"] += 1
        self.__data["id_num"] += 1
        
        #id存储部分，待改
        cave_id = self.__data['id_num']
        
        for i in self.__data["groups_dict"]:
            self.__data["groups_dict"][i]["m_list"]:list.append({
                'cave_id':cave_id,
                'state':state,
                'time':str(datetime.datetime.now())})
        self.__cave.append({
                'cave_id':cave_id,
                'cqcode':cqcode,
                'contributor_id':contributor_id,
                'state':state})
        self.__save()
        return {
            'success':f'添加成功，序号为 {cave_id}，\n来自{contributor_id}',
            'white_B':self.__data['white_B'],
            'cave_id':cave_id
        }

    def remove(self, index:int) -> dict:
        '''
        移除cave
            index : 序号
        '''
        for i in self.__cave:
            if i['cave_id'] == index:
                self.__cave.remove(i)
                self.__save()
                return {'success':'删除成功！'}
        self.__data["groups_dict"][self.__group_id]["m_list"]:list.append({
            'cave_id':index,
            'state':3,
            'time':str(datetime.datetime.now())})
        return {'error':f"索引为“{index}”的内容不存在或已被删除。"}

    def get_cave(self, index:int) -> dict:
        '''
        查看cave
            index : 序号
        '''
        for i in self.__cave:
            if i['cave_id'] == index:
                return i
        return {'error':f'索引为“{index}”的内容不存在或已被删除。'}
    
    def set_cd(self, cd_num:int, cd_unit:str) -> dict:
        '''
        设置群冷却时间
            cd_num : 冷却时间的数字
            cd_unit : 冷却时间的单位('sec','min','hour')
        '''
        if cd_unit not in ['sec','min','hour']: return {'error':f'无法将“{cd_unit}”识别为有效单位'}
        if not(0 < cd_num < 500): return {'error':'冷却时间需大于0，小于500'}
        self.__data["groups_dict"][self.__group_id]["cd_num"] = cd_num
        self.__data["groups_dict"][self.__group_id]["cd_unit"] = cd_unit
        self.__data["groups_dict"][self.__group_id]["last_time"] = "1000-01-01 00:00:00.114514"
        self.__save()
        return {'success':f'成功修改本群cave冷却时间为{cd_num}{cd_unit}'}

    def get_m(self) -> dict:
        '''
        获取新增的投稿的审核情况，时间截至到上次获取\\
        返回信息列表，并在文件中清除
        '''
        m_info:list = self.__data["groups_dict"][self.__group_id]["m_list"]
        if m_info == [] : return {'error':'暂无新增的回声洞处理'}
        self.__data["groups_dict"][self.__group_id]["m_list"]:list.clear()
        self.__save()
        return m_info


    def wA_add(self, a_id:str) -> dict:
        '''
        添加白名单A成员
            a_id : 添加的账号
        返回结果
        '''
        if self.check_wA_id(id=a_id): return {'error':f'此账号已在群“{self.__group_id}”的白名单A中！'}
        else:
            self.__data["groups_dict"][self.__group_id]["white_A"].append(a_id)
            self.__save()
            return {'success':f'成功将账号“{a_id}”添加到群“{self.__group_id}”的白名单A中！'}

    def wA_remove(self, r_id:str) -> dict:
        '''
        删除白名单A成员
            r_id : 删除的账号
        返回结果
        '''
        if self.check_wA_id(id=r_id): 
            self.__data["groups_dict"][self.__group_id]["white_A"].remove(r_id)
            self.__save()
            return {'success':f'成功将账号“{r_id}”移出群“{self.__group_id}”的白名单A！'}
        else: return {'error':f'账号“{r_id}”不在群“{self.__group_id}”的白名单A中！'}

    def wA_get(self) -> list:
        '''
        获取当前群的白名单A的成员列表
        '''
        return self.__data["groups_dict"][self.__group_id]["white_A"]


    def wB_add(self, a_id) -> dict:
        '''
        添加白名单B成员
            a_id : 添加的账号
        返回结果
        '''
        if self.check_wB_id(id=a_id): return {'error':f'此账号已在群“{self.__group_id}”的白名单B中！'}
        else:
            self.__data["white_B"].append(a_id)
            self.__save()
            return {'success':f'成功将账号“{a_id}”添加到的白名单B中！'}

    def wB_remove(self, r_id) -> dict:
        '''
        删除白名单B成员
            r_id : 删除的账号
        返回结果
        '''
        if  self.check_wB_id(id=r_id):
            self.__data["white_B"].remove(r_id)
            self.__save()
            return {'success':f'成功将账号“{r_id}”移出白名单B！'}
        else: return {'error':f'账号“{r_id}”不在白名单B中'}

    def wB_get(self) -> list:
        '''
        获取当前的白名单B的成员列表
        '''
        return self.__data["white_B"]



    def set_t(self, cave_id:int) -> dict:
        '''
        通过审核
        '''
        if self.check_set_id(id = cave_id, change_state = 0):
            for i in self.__data["groups_dict"]:
                self.__data["groups_dict"][i]["m_list"]:list.append({
                    'cave_id':cave_id,
                    'state':0,
                    'time':str(datetime.datetime.now())})
            self.__save()
            return {'success':f'操作成功，序号:({cave_id})通过审核，加入回声洞。'}
        else: return {'error':'此序号不存在或已被删除或已被审核！'}

    def set_f(self, cave_id:int) -> dict:
        '''
        不通过审核
        '''
        if self.check_set_id(id = cave_id, change_state = 2):
            for i in self.__data["groups_dict"]:
                self.__data["groups_dict"][i]["m_list"]:list.append({
                    'cave_id':cave_id,
                    'state':2,
                    'time':str(datetime.datetime.now())})
            self.__save()
            return {'success':f'操作成功，序号:({cave_id})通过不审核，已将其删除。'}
        else: return {'error':'此序号不存在或已被删除或已被审核！'}

    def set_l(self) -> list:
        '''
        返回当前未处理的审核序号列表
        '''
        msg = []
        for i in self.__cave:
            if i['state'] == 1:
                msg.append(i)
        return msg

    def set_e(self, cave_id:int) -> dict:
        '''
        返回此id的审核情况\\
        state值的意义：
            state 0 : 通过审核，可正常获取
            state 1 : 待审核
            state 2 : 未通过审核
            state 3 : 被-r删除
        '''
        if self.check_set_id(id = cave_id, change_state = None):
            for i in self.__cave:
                if i['cave_id'] == cave_id:
                    return {'success':i['state']}
        else: return {'error':'此序号不存在或已被删除或已被审核'}

