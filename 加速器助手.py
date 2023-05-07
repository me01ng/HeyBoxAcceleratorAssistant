from os import system, listdir, getcwd
from os.path import join as os_join
from requests import get
import json
import sys
from tkinter.messagebox import showerror
from time import sleep
import psutil
from winsound import Beep


class StartupComponents:
    def __init__(self):
        self.acc_id, self.acc_mode, self.acc_district, self.game_process_name = sys.argv[1], sys.argv[2], sys.argv[3], \
                                                                                sys.argv[4].strip('"')
        self.acc_path = self.basicConfigurationRead()['acc_path']
        self.startAccelerator(self.acc_path)
        self.url_start = "http://127.0.0.1:38252/api/start_acc?acc_id={}&acc_mode_id={}&server_region={}&node_name=" \
            .format(self.acc_id, self.acc_mode, self.acc_district)
        self.url_stop = "http://127.0.0.1:38252/api/stop_acc?acc_id={}".format(self.acc_id)
        self.url_gameLaunch = "http://127.0.0.1:38252/api/get_launch_scheme?acc_id={}".format(self.acc_id)
        self.open_command = None

    @staticmethod
    def basicConfigurationRead():
        path = os_join(getcwd(), "basic_Configuration.json")
        with open(path, "r", encoding="utf-8") as f:
            basic_Configuration = json.load(f)
        print(basic_Configuration)
        return basic_Configuration

    @staticmethod
    def startAccelerator(acc_path):
        system(r"C:\WINDOWS\system32\schtasks.exe /run /tn HeyBoxTaskDONOTDELETE")
        for i in range(10):
            appList = listdir(acc_path)
            for name in appList:
                if name.endswith(".exe") and name.startswith(("HeyBox", "uninstall")) is False:
                    print("打开成功")
                    return True
            sleep((i // 2) + 0.5)

    def startAcceleration(self):
        response_start = get(self.url_start)
        if response_start.json()['status'] == 'ok':
            response_start.close()
            return True
        else:
            get(self.url_stop)
            sleep(2.5)
            if get(self.url_start).json()['status'] == 'ok':
                response_start.close()
                return True
            else:
                showerror(title="错误", message="启动失败")
                raise Exception("启动失败")

    def detectionProcessExists(self):
        for process in psutil.process_iter():
            try:
                if process.name() == self.game_process_name:
                    print(f"进程名称 {self.game_process_name} 存在")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def openGame(self):
        self.open_command = "start {}".format(
            get(self.url_gameLaunch).json()['result']['launch_scheme'][0]['launch_path'])
        system(self.open_command)
        for i in range(20):
            if self.detectionProcessExists():
                break
            else:
                sleep((i // 3) + 0.5)
        else:
            self.stopAcceleration()
            showerror(title="错误", message="启动游戏失败")
            raise Exception("启动失败")

    def stopAcceleration(self):
        get(self.url_stop)


if len(sys.argv) >= 5:
    Startup = StartupComponents()
    Startup.startAcceleration()
    Startup.openGame()
    while True:
        if Startup.detectionProcessExists():
            sleep(3)
            continue
        else:
            break
    Startup.stopAcceleration()
    Beep(600, 600)
else:
    system("start 配置向导.exe")
