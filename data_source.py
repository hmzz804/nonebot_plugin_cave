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
        with self.data_path.open('w') as f:
            json.dump(self.__data, f, indent=4)
        with self.cave_path.open('w') as f:
            json.dump(self.__cave, f, indent=4)

    def __check_cd(self, cd:int, unit:str, last_time:str) -> list:
        '''
        检查cd情况
        `cd` : 冷却时间的数字
        `unit` : 冷却时间的单位
        `last_time` : 上次使用时间  

        返回列表：  
        第0项(str):现在时间与上次时间的差值字符串
        第1项(bool):cd是否已过
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
        print(str(self.cave_path))


    def select(self, group_id:str):
        '''
        抽取cave
        '''
        group_bool = False
        group_dict = self.__data["groups_dict"]
        for i in group_dict:
            if i == group_id:
                group_bool = True
                group = i
                cd_dict = group_dict[i]
                break
        list_bool = False
        for i in self.__cave:
            if i["state"] == 0:
                list_bool = True
                break
        if self.__cave and list_bool:
            if group_bool:
                check_cd_list = self.__check_cd(self.__data)
                if check_cd_list[1]:
                    while True:
                        send_cave = random.choice(self.__cave)
                        if send_cave["state"] == 0:
                            self.__data["groups_dict"][group]["last_time"] = str(datetime.datetime.now())
                            self.__save()

                            # 此处应该发送消息了
                            """
                            await _cave.finish(
                                message = f"回声洞 ——（{send_cave['cave_id']}）"
                                + f"\n"
                                + Message(send_cave["cqcode"])
                                + f"\n——"
                                + (await bot.get_stranger_info(user_id=send_cave['contributor_id']))["nickname"]
                            )
                            """
                else:
                    pass
                    # 正在冷却
                    # await _cave.finish(message = f"cave冷却中,恁稍等{check_cd_list[0]}")
            else:
                pass
                #await _cave.finish(message = "未找到此群组存储的cd信息，请超管设置此群冷却时间")
        else:
            pass
            #await _cave.finish(message = "库内无内容")


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
