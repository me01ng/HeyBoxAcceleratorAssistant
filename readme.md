## 小黑盒加速器助手

偶然间发现小黑盒加速器是通过web开发的，只要在浏览器中输入相应地址就可以访问，同时加速游戏也是通过向地址get完成，于是萌生了自动化加速的想法。

### 一、功能简介

1.免管理员授权打开小黑盒加速器

2.自动加速指定游戏并打开

3.游戏关闭后自动关闭加速

### 二、用户需要的操作

##### 1.第一次使用：

解压缩后在桌面找到设置向导快捷方式

根据设置向导完成基本设置

其中有一块需要管理员权限，是为了运行一个bat文件，主要内容为：

```shell
schtasks /create /tn %taskname% /tr %taskcommand% /sc onstart /it /ru %username% /rl HIGHEST /f >nul
```

是为了在计划程序中创建使用管理员权限启动小黑盒加速器任务，请放心授权

一切准备完毕后会生成一个游戏的快捷方式

##### 2.其后使用

点击快捷方式即可自动启动加速和游戏

关闭游戏后会在滴声后关闭加速器

##### 3.添加其他游戏

再次点击设置向导即可添加，所添加游戏与之前游戏并不冲突

### 三、急需改进的地方

目前检测游戏进程是否存在的方式过于低效，大大浪费了CPU资源，代码如下：

```python
    def detectionProcessExists(self):
        for process in psutil.process_iter():
            try:
                if process.name() == self.game_process_name:
                    print(f"进程名称 {self.game_process_name} 存在")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
```

暂时还没有发现更好的方法

### 四、其他

全部程序可以说是由ChatGPT主编，本人只是拼接剪辑，非计算机专业，有不当之处，还望指正。



