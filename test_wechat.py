#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Xuxh'

from appium import webdriver
import time
import subprocess
import psutil
import signal
import os


def launch_appium(uid):

    try:
        cmd = "".join(["appium -p ", "4723", " -bp ", "4724", " -U ",  uid, " --command-timeout 600"])
        process = subprocess.Popen(cmd, shell=True)
        time.sleep(4)
    except Exception, ex:
        print ex
        process = None

    return process


def kill_appium_processes(parent_pid, sig=signal.SIGTERM):

    try:
        p = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    child_pid = p.children(recursive=True)

    for pid in child_pid:
        os.kill(pid.pid, sig)


if __name__ == '__main__':

    device = "1df0cd1f"
    proc = launch_appium(device)

    # if Appium is launched successfully, start testing
    if proc is not None:

        pid = proc.pid
        desired_caps = {
                'platformName': 'Android',
                'noReset': 'true',  # keep status of log in
                'deviceName': device,
                'appPackage': 'com.tencent.mm',
                'appActivity': '.ui.LauncherUI',
                'fullReset': 'false',
                'unicodeKeyboard': 'True',
                'resetKeyboard': 'True',
                'chromeOptions': {
                    'androidProcess': 'com.tencent.mm:appbrand0'
                    }
                }
        #Access to wechat
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        time.sleep(10)

        try:
            # click "发现" button
            driver.find_elements_by_id("com.tencent.mm:id/ayn")[2].click()
            time.sleep(3)

            # click "小程序”
            driver.find_elements_by_id("android:id/title")[14].click()
            time.sleep(3)

            # 农行微服务
            driver.find_elements_by_id("com.tencent.mm:id/be")[0].click()
            time.sleep(8)

        # switch to webview
            for context in driver.contexts:
                if context.find('WEBVIEW_com.tencent.mm:appbrand0') != -1:

                    # switch to context WEBVIEW
                    driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand0')
                    print(driver.page_source)

                    # note: there are many window_handles, walk through all handled to locate element
                    for handle in driver.window_handles:
                        try:
                            # switch to handle
                            driver.switch_to.window(handle)  # switch current handle

                            # 点击我的优惠券
                            # driver.find_element_by_xpath("/html/body/wx-view[1]/wx-view[1]/wx-view[2]/wx-view[1]/wx-image")
                            driver.find_element_by_class_name("my-coupon").click()
                            time.sleep(3)
                            break
                        except Exception,ex:
                            print ex

                    # 进入下一页面，重新获取handles
                    for handle in driver.window_handles:
                        try:
                            driver.switch_to.window(handle)
                            driver.find_element_by_class_name("getPhoneNumber").click()
                            time.sleep(2)
                            break
                        except Exception, ex:
                            print ex

                    # switch to NATIVE
                    driver.switch_to.context('NATIVE_APP')
                    time.sleep(2)

                    # click 取消按钮
                    driver.find_element_by_id('com.tencent.mm:id/alk').click()
                    time.sleep(2)
                    # 返回到小程序列表
                    driver.press_keycode(4)
                    time.sleep(1)
                    driver.press_keycode(4)
                    time.sleep(1)
                    break
        except Exception, ex:
            print ex

        # close Appium
        kill_appium_processes(pid)
    else:

        print "Appium is not launched"

