from os import path as os_path
from os import getcwd, system, listdir, environ
from requests import get
from PIL import Image
from random import randint
from win32com.client import Dispatch
import json
import sys
from time import sleep


class ConfigurationWizard:
    # 游戏信息获取，在添加新游戏时使用
    @staticmethod
    def gameInformationConfiguration():
        search_word = input("请输入搜索关键字:")
        search_url = "http://127.0.0.1:38252/api/game_search?q={}".format(search_word)
        response = get(search_url)
        search_list = response.json()["result"]["game_list"]
        print("搜索到以下内容")
        for count, v in enumerate(search_list):
            print(count, v["name"])
        choose = input("请输入数字选择的游戏:")
        choose_list = search_list[int(choose)]
        game_information = {
            "game_name": choose_list["name"],
            "acc_id": choose_list["acc_id"],
            "mode_id": choose_list["current_mode_id"],
            "mode_name": choose_list["current_mode_name"],
            "district_id": choose_list['current_district_id'],
            "district_name": choose_list['current_district_name'],
            "launch_schema": choose_list["launch_schema"]
        }
        print("游戏的默认设置是" + str(game_information))
        n = input("如果需要继续设置，请输入n,否则将使用默认设置")
        if n != 'y':
            print("请选择加速模式")
            for count, v in enumerate(choose_list["acc_mode"]):
                print(count, v["acc_mode_name"])
            t = input("请输入数字：")
            game_information['mode_id'] = choose_list["acc_mode"][int(t)]["acc_mode_id"]
            game_information['mode_name'] = choose_list["acc_mode"][int(t)]["acc_mode_name"]
            print("请选择加速地区")
            for count, v in enumerate(choose_list["acc_district"]):
                print(count, v["acc_district_name"])
            t = input("请输入数字：")
            game_information['district_id'] = choose_list["acc_district"][int(t)]["acc_district_id"]
            game_information['district_name'] = choose_list["acc_district"][int(t)]["acc_district_name"]
        else:
            pass
        print(game_information)
        t = input("确认完成设置吗？(y/n)")
        response.close()
        if t == 'y':
            print('好的我记住了')
            while True:
                print("最后一步，请输入游戏启动时运行的进程名，例如apex运行时的进程名是r5apex")
                game_process_name = input(':') + '.exe'
                print("重复：" + game_process_name)
                t = input("确定吗?(y/n)")
                if t == 'y':
                    game_information['game_progress_name'] = game_process_name
                    break
            return game_information
        else:
            print("请重新配置!")
            return False

    # 基本信息获取，在初次启动时调用
    @staticmethod
    def basicConfiguration():
        basic_information = {}
        acc_path = os_path.normpath(input("接下来，请输入您小黑盒的安装路径,也就是补全..\\HeyboxAccelerator"))
        basic_information["acc_path"] = acc_path
        print("重复", basic_information["acc_path"])
        c = input("确定吗?(y/n)")
        if c == 'y':
            print('好的我记住了')
            with open("basic_Configuration.json", "w", encoding="utf-8") as f:
                json.dump(basic_information, f, ensure_ascii=False)
            return basic_information
        else:
            print("请重新配置!")
            return False

    # 基本信息读取，如果存在的话
    @staticmethod
    def basicConfigurationRead():
        with open("basic_Configuration.json", "r", encoding="utf-8") as f:
            basic_Configuration = json.load(f)
        print(basic_Configuration)
        return basic_Configuration

    # 快捷方式创建
    @staticmethod
    def shortcutCreation(filename, arguments: list):
        # 获取当前用户桌面路径
        print(filename, arguments)
        desktop_path = os_path.join(environ['USERPROFILE'], 'Desktop', filename + '.lnk')
        target_path = os_path.join(getcwd(), "加速器助手.exe")
        icon_path = os_path.join(getcwd(), 'logo/{}.ico'.format(filename))
        # 创建快捷方式对象
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(desktop_path)
        # 设置快捷方式的属性
        shortcut.TargetPath = target_path
        shortcut.Arguments = " ".join(arguments)
        shortcut.WorkingDirectory = getcwd()
        shortcut.IconLocation = icon_path
        shortcut.save()

    # 通过创建计划任务，跳过小黑盒启动UAC页面，加速启动，仅在第一次需要使用，需要管理员员权限
    @staticmethod
    def taskCommandCreation(path):
        bat = r'''
@echo off
:: 判断是否已经以管理员权限运行脚本
net session >nul 2>&1
if %errorLevel% neq 0 (
    :: 如果没有管理员权限，则使用 PowerShell 重新启动脚本并请求管理员权限
    powershell -Command "Start-Process '%comspec%' -ArgumentList '/c %~fnx0' -Verb runAs"
    exit /B
)
set taskname="HeyBoxTaskDONOTDELETE"
set taskdesc="accHeyBox!!!!!!!!!!!!"
set taskcommand=""{}""
set username=%USERNAME%
schtasks /create /tn %taskname% /tr %taskcommand% /sc onstart /it /ru %username% /rl HIGHEST /f >nul
if %errorlevel% equ 0 (
   echo Task created successfully.
) else (
   echo Failed to create task.
)
pause
'''.format(os_path.join(path, 'heyboxacc.exe'))
        with open("task.bat", "w", encoding="utf-8") as f:
            f.write(bat)
        system("start {}".format("task.bat"))

    # 通过替换颜色创建不同图标
    @staticmethod
    def iconGenerator(game_name):
        # 读取ICO文件为Image对象
        ico_image = Image.open('logo.ico')

        # 遍历每个像素并进行颜色替换
        color1 = [randint(0, 255), randint(0, 255), randint(0, 255)]
        color2 = [color1[2], color1[0], color1[1]]
        for x in range(ico_image.width):
            for y in range(ico_image.height):
                # 获取像素的RGB颜色值
                r, g, b, a = ico_image.getpixel((x, y))

                # 如果该像素颜色为蓝色，则替换为绿色
                if (r, g, b) == (241, 242, 243):
                    ico_image.putpixel((x, y), (color1[0], color1[1], color1[2], a))
                if (r, g, b) == (58, 60, 63):
                    ico_image.putpixel((x, y), (color2[0], color2[1], color2[2], a))
        # 保存修改后的图像
        ico_image.save('logo/{}.ico'.format(game_name), sizes=[(256, 256)])

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


def changeConfiguration():
    # 初始消息
    basicConfiguration = ConfigurationWizard.basicConfiguration()
    # 创建任务
    ConfigurationWizard.taskCommandCreation(basicConfiguration['acc_path'])
    sleep(2)
    ConfigurationWizard.startAccelerator(basicConfiguration['acc_path'])
    # 游戏信息
    gameInformation = ConfigurationWizard.gameInformationConfiguration()
    # 应用图标
    ConfigurationWizard.iconGenerator(gameInformation['game_name'])
    # 快捷方式
    ConfigurationWizard.shortcutCreation(filename=gameInformation['game_name'],
                                         arguments=[str(gameInformation['acc_id']),
                                                    str(gameInformation['mode_id']),
                                                    str(gameInformation['district_id']),
                                                    f"\"{str(gameInformation['game_progress_name'])}\""])
    print("创建成功！")


def AddGames():
    basicConfiguration = ConfigurationWizard.basicConfigurationRead()
    sleep(2)
    ConfigurationWizard.startAccelerator(basicConfiguration['acc_path'])
    gameInformation = ConfigurationWizard.gameInformationConfiguration()
    ConfigurationWizard.iconGenerator(gameInformation['game_name'])
    ConfigurationWizard.shortcutCreation(filename=gameInformation['game_name'],
                                         arguments=[str(gameInformation['acc_id']),
                                                    str(gameInformation['mode_id']),
                                                    str(gameInformation['district_id']),
                                                    f"\"{str(gameInformation['game_progress_name'])}\""])
    print("创建成功！")


if os_path.exists("basic_Configuration.json"):
    while True:
        cch = input("欢迎使用加速器助手，这里是配置向导，请选择：\n1.变更配置\n2.增加游戏\n3.退出\n")
        if cch == '1':
            changeConfiguration()
        elif cch == '2':
            AddGames()
        elif cch == '3':
            sys.exit()
        else:
            print("错误的代码")
            continue

else:
    changeConfiguration()
