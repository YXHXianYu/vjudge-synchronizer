#
# Created by YXH_XianYu 2023.9.29
#

# ----- Imports -----

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import yaml
import sys

class VjudgeSynchronizer:

    def __init__(self):

        # ----- Load Configs -----
        yml = yaml.load(open(r'config.yml', 'r', encoding='utf-8'), Loader=yaml.FullLoader)

        self.vjudge_link: str = yml['vjudge-link']
        self.board_link: str = yml['board-link']

        self.contest_length_proportional_scaling: bool = bool(yml['contest-length-proportional-scaling'])

        self.vjudge_wait_time: float = yml['vjudge-wait-time']
        self.board_wait_time: float = yml['board-wait-time']
        self.loop_wait_time: float = yml['loop-wait-time']

        self.vjudge_account: str = yml['vjudge-account']
        self.vjudge_password: str = yml['vjudge-password']

        # ----- Load Web Driver -----
        self.wd = webdriver.Chrome(service=Service(r'chromedriver.exe'))

        self.haveEnd = self.login_vjudge()
        if self.haveEnd:
            print("Contest have ended.")
            return

        self.vjudge_contest_length = self.get_vjudge_contest_length()
        self.board_contest_length = self.get_board_contest_length()

        print("vjudge contest length: ", self.vjudge_contest_length, "sec")
        print("board contest length: ", self.board_contest_length, "sec")

    def get_current_time(self):
        self.wd.get(self.vjudge_link)
        self.wd.implicitly_wait(self.vjudge_wait_time)
        t1 = [int(i) for i in self.wd.find_element(By.ID, "span-elapsed").text.split(':')]
        v1 = t1[0] * 60 * 60 + t1[1] * 60 + t1[2]
        return v1

    def get_vjudge_contest_length(self):
        self.wd.get(self.vjudge_link)
        self.wd.implicitly_wait(self.vjudge_wait_time)
        t1 = [int(i) for i in self.wd.find_element(By.ID, "span-elapsed").text.split(':')]
        v1 = t1[0] * 60 * 60 + t1[1] * 60 + t1[2]
        t2 = [int(i) for i in self.wd.find_element(By.ID, "span-remaining").text.split(':')]
        v2 = t2[0] * 60 * 60 + t2[1] * 60 + t2[2]
        return v1 + v2

    # 本函数假定该比赛已经结束！
    def get_board_contest_length(self):
        self.wd.get(self.board_link)
        self.wd.implicitly_wait(self.board_wait_time)
        t1 = self.wd.find_element(By.XPATH, '//div[contains(text(), "Elapsed:")]').text.split(':')
        v1 = int(t1[1]) * 60 * 60 + int(t1[2]) * 60 + int(t1[3])
        return v1

    def get_current_status(self, process_ratio: int):
        self.wd.get(self.board_link + "?progress-ratio=" + str(process_ratio))
        self.wd.implicitly_wait(self.board_wait_time)

        result = []
        problems = self.wd.find_elements(By.XPATH, '//table[@class="standings"]//th[@class="success"]')
        for problem in problems:
            result.append(problem.text.split("\n"))
        
        # print(result)

        return result

    # 登录vjudge
    # 并返回比赛是否结束
    def login_vjudge(self):
        self.wd.get(self.vjudge_link)
        self.wd.implicitly_wait(self.vjudge_wait_time)

        try:
            self.wd.find_element(By.XPATH, '//a[@class="nav-link logout"]').click()
        except NoSuchElementException:
            pass

        self.wd.find_element(By.XPATH, '//a[@class="nav-link login"]').click()
        self.wd.find_element(By.XPATH, '//input[@id="login-username"]').send_keys(self.vjudge_account)
        self.wd.find_element(By.XPATH, '//input[@id="login-password"]').send_keys(self.vjudge_password)
        self.wd.find_element(By.XPATH, '//button[@id="btn-login"]').click()

        while True:
            try:
                self.wd.find_element(By.XPATH, '//input[@id="login-captcha"]')
                print(" ===== Important! ===== ")
                print("You need to enter vjudge captcha in terminal:")
                captcha = sys.stdin.readline()
                self.wd.find_element(By.XPATH, '//input[@id="login-captcha"]').clear()
                self.wd.find_element(By.XPATH, '//input[@id="login-captcha"]').send_keys(captcha)
                self.wd.find_element(By.XPATH, '//button[@id="btn-login"]').click()
                time.sleep(self.vjudge_wait_time)
            except NoSuchElementException:
                break

        return bool(self.wd.find_element(By.XPATH, '//span[@id="info-running"]').text == 'Ended')

    def close(self):
        self.wd.close()

    def get_process_ratio(
            self,
            current_time: int,
            contest_length_proportional_scaling: bool = True):

        if not contest_length_proportional_scaling:
            assert False, "非等比缩放功能没写，有兴趣可以直接提交PR\ngithub.com/YXHXianYu\n"
        else:
            return int(1.0 * current_time / self.vjudge_contest_length * 10000)

    def get_announcement(self, current_time: int, contest_status):
        s = "比赛时间: " + str(int(current_time/3600)) + ":" + str(int(current_time/60%60)) + ":" + str(int(current_time%60)) + "\n"
        for i in contest_status:
            s += i[0] + " " + i[1] + "; "
        s += '\n\n' + 'From github.com/yxhxianyu/vjudge-synchronizer'
        return s

    def set_announcement(self, announcement: str):
        self.wd.get(self.vjudge_link)
        time.sleep(self.vjudge_wait_time)

        try:
            self.wd.find_element(By.XPATH, '//button[@id="btn-update"]').click()
            time.sleep(self.vjudge_wait_time)
            textarea = self.wd.find_element(By.XPATH, '//textarea[@id="contest-announcement-edit"]')
            textarea.click()
            textarea.clear()
            textarea.send_keys(announcement)
            time.sleep(self.vjudge_wait_time)
            self.wd.find_element(By.XPATH, '//div[@class="modal-footer"]/button[@id="btn-confirm"]').click()
        except NoSuchElementException:
            print("Accouncement setting error.")

    def run(self):

        if not hasattr(self, 'haveEnd'):
            print("Initialization error.")
            return
        
        if self.haveEnd:
            print("Contest have ended.")
            return

        while True:
            current_time = self.get_current_time()
            print("current_time: ", current_time)

            process_ratio = self.get_process_ratio(current_time)
            print("process_ratio: ", process_ratio)

            current_status = self.get_current_status(process_ratio)
            announcement = self.get_announcement(current_time, current_status)
            print("Announcement: ") 
            print(announcement)
            self.set_announcement(announcement)

            time.sleep(self.loop_wait_time)

vs = VjudgeSynchronizer()

vs.run()

vs.close()
        
exit(0)