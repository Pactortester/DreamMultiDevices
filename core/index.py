# -*- coding: utf-8 -*-
__author__ = "无声"

import time
from core import MultiAdb as Madb
import multiprocessing
from airtest.core.error import *
from poco.exceptions import *
from airtest.core.api import *
from core import RunTestCase

_print = print
def print(*args, **kwargs):
    _print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), *args, **kwargs)

def main():
    devicesList = Madb.MultiAdb("").get_devicesList()
    if devicesList[0] == "":
        devicesList = Madb.MultiAdb("").getdevices()
    print("测试开始")
    results=""
    if devicesList:
        try:
            pool = multiprocessing.Pool(processes=len(devicesList))
            print("启动进程池")
            results=[]
            for i in range(len(devicesList)):
                madb=Madb.MultiAdb(devicesList[i])
                pool.apply_async(enter_processing, (i,madb,))  # 根据设备列表去循环创建进程，对每个进程调用下面的enter_processing方法。
            pool.close()
            pool.join()
            print("进程回收完毕")
            print("测试结束")
        except AirtestError as ae:
            print("Airtest发生错误" + ae)
        except PocoException as pe:
            print("Poco发生错误" + pe)
        except Exception as e:
            print("发生未知错误" + e)
    else:
        print("未找到设备，测试结束")

def enter_processing(processNo,madb):
    devices = madb.get_mdevice()
    print("进入{}进程,devicename={}".format(processNo,devices))
    isconnect=""
    try:
        connect_device("Android:///" + devices)
        time.sleep(1)
        auto_setup(__file__)
        isconnect="Pass"
        print("设备{}连接成功".format(devices))
        if isconnect == "Pass":
            try:
                print("设备{}开始安装apk".format(devices))
                install = madb.get_needclickinstall()
                startapp = madb.get_needclickstartapp()
                installResult = madb.PushApk2Devices(devices, install)
                if installResult == "Success":
                    print("{}确定安装成功".format(devices))
                    madb.StartApp(devices, startapp)
                    time.sleep(madb.get_timeoutaction())
                    RunTestCase.RunTestCase(madb)
                    print("{}完成测试".format(devices))
            except Exception as e:
                print(e)
                print("{}安装/运行失败，installResult={}".format(devices, installResult))
        else:
            print("设备{}连接失败".format(devices))
    except Exception as e:
        print(e)
        isconnect="Fail"
        print( "连接设备{}失败".format(devices))
    return isconnect




