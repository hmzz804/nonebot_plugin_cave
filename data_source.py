import datetime
import json
import random
from pathlib import Path
from typing import Dict, List

class Cave():
    def __init__(self):
        # 路径
        self.data_path = Path(r"data/cave/data.json").absolute()
        self.cave_path = Path(r"data/cave/cave.json").absolute()
        # 路径文件夹
        self.dir = Path(r"data/cave").absolute()
        self.dir.mkdir(parents=True, exist_ok=True)
        # 初始化__cave和__data
        self.__cave: List[dict] = []
        self.__data: Dict = {}
        self.__load()

    def __check_path(self) -> bool:
        return self.data_path.exists() and self.data_path.is_file() \
            and self.cave_path.exists() and self.data_path.is_file()

    def __load(self):
        """
        读取`cave.json`,`data.json`
        """
        if self.__check_path():
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

    def __save(self):
        """
        保存`cave.json`,`data.json`
        """
        with self.data_path.open('w') as f:
            json.dump(self.__data, f, indent=4)
        with self.cave_path.open('w') as f:
            json.dump(self.__cave, f, indent=4)

    def __check_cd(self, cd:int, unit:str, last_time:str) -> list:
        '''
        ## 检查cd情况  
        参数：  
        - `cd` : 冷却时间的数字
        - `unit` : 冷却时间的单位
        - `last_time` : 上次使用时间
        
        返回列表：  
        - 第0项(str):现在时间与上次时间的差值字符串
        - 第1项(bool):cd是否已过
        '''
        now_time = datetime.datetime.now()
        last_time = datetime.datetime.strptime(last_time,"%Y-%m-%d %H:%M:%S.%f")
        dif_sec = (now_time - last_time).seconds
        dif_day = (now_time - last_time).days
        result = []
        if unit == "hour":
            sec_cd = cd*3600
            result.append(str(round((sec_cd-dif_sec)/3600,2))+unit)
            if dif_sec >= sec_cd or dif_day > 0:
                result.append(True)
            else:
                result.append(False)
        elif unit == "min":
            sec_cd = cd*60
            result.append(str(round((sec_cd-dif_sec)/60,1))+unit)
            if dif_sec >= sec_cd or dif_day > 0:
                result.append(True)
            else:
                result.append(False)
        elif unit == "sec":
            sec_cd = cd
            result.append(str(sec_cd-dif_sec)+unit)
            if dif_sec >= sec_cd or dif_day > 0:
                result.append(True)
            else:
                result.append(False)
        return result

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

    def select(self, group_id:str) -> dict:
        '''
        ## 抽取cave  
        参数：  
        - `group_id` : 群号(string) 

        返回要发送的消息的部分内容
        '''
        if group_id not in self.__data["groups_dict"]:
            self.__data["groups_dict"][group_id] = {
                "cd_num": 1,
                "cd_unit": "sec",
                "last_time": "1000-01-01 00:00:00.114514",
                "m_list": [],
                "white_A":[]
            }
            self.__save()
            return {'error':'初次使用，正在新建此群冷却存档，请超管使用"/cave-c[数字][单位]"设置冷却时间。'}
        if (0 not in list(i['state']  for i in self.__cave) ) or \
            self.__cave == []:
            return {'error':'库内暂无内容。'}
        check_cd_result = self.__check_cd(self.__data)
        if not check_cd_result[1]:
            return {'error':f"cave冷却中,恁稍等{check_cd_result[0]}"}
        while True:
            send_msg = random.choice(self.__cave)
            if send_msg["state"] == 0:
                self.__data["groups_dict"][group_id]["last_time"] = str(datetime.datetime.now())
                self.__save()
                return send_msg
    
    def add(self):
        '''
        添加cave
        '''

    def remove(self):
        '''
        移除cave
        '''

    def check(self):
        '''
        查看cave
        '''
