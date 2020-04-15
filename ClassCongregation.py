#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from fake_useragent import UserAgent
import urllib.parse
import nmap
import requests
import pymysql
import sqlite3
from tqdm import tqdm
import logging
import os
import re
import base64
import random
import sys
import time
import threading
from config import dns_log_url,dns_log_key,debug_mode
def IpProcess(Url):
    if Url.startswith("http"):  # 记个小知识点：必须带上https://这个头不然urlparse就不能正确提取hostname导致后面运行出差错
        res = urllib.parse.urlparse(Url)  # 小知识点2：如果只导入import urllib包使用parse这个类的话会报错，必须在import requests导入这个包才能正常运行
    else:
        res = urllib.parse.urlparse('http://%s' % Url)
    return (res.hostname)
LoopholesList=[]#漏洞名称列表
def NumberOfLoopholes():#漏洞个数输出函数以及名称的函数
    print("\033[1;40;32m[ ! ] The number of vulnerabilities scanned was:\033[0m"+"\033[1;40;36m {}             \033[0m".format(len(LoopholesList)))
    for i in LoopholesList:
        time.sleep(0.1)#暂停不然瞬间刷屏
        print("\033[1;40;35m[ ! ] {}\033[0m".format(i))
    LoopholesList.clear()#清空容器这样就不会出问题了


def BotNumberOfLoopholes():#机器人用的漏洞个数
    bot_loopholes_number=len(LoopholesList)
    LoopholesList.clear()
    return bot_loopholes_number

class WriteFile:#写入文件类
    def result(self,TargetName,Medusa):
        self.FileName=TargetName+"result"
        regular_match_results = re.search(r'存在([\w\u4e00-\u9fa5!@#$%^*()&-=+_`~/?.,<>\\|\[\]{}]*)',Medusa).group(0)#正则匹配，匹配存在后面的所有字符串，直到换行符结束
        LoopholesList.append(regular_match_results)#每调用一次就往列表中写入存在漏洞的名称漏洞
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.FilePath = os.path.split(os.path.realpath(__file__))[0]+"\\ScanResult\\"+self.FileName + ".txt"#不需要输入后缀，只要名字就好
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.FilePath = os.path.split(os.path.realpath(__file__))[0] + "/ScanResult/" +self.FileName+ ".txt"  # 不需要输入后缀，只要名字就好
        with open(self.FilePath, 'w+',encoding='utf-8') as f:  # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
            f.write(Medusa+"\n")


class AgentHeader:#使用随机头类
    def result(self,Values):#使用随机头传入传入参数
        try:
            self.Values = Values
            if len(Values)>11:
                return Values
            ua = UserAgent(verify_ssl=False)
            if self.Values.lower()=="None":#如果参数为空使用随机头
                return (ua.random)
            elif self.Values.lower()=="firefox":#如果是火狐字符串使用火狐头
                return (ua.firefox)
            elif self.Values.lower()=="ie":#IE浏览器
                return (ua.ie)
            elif self.Values.lower()=="msie":#msie
                return (ua.msie)
            elif self.Values.lower()=="opera":#Opera Software
                return (ua.opera)
            elif self.Values.lower()=="chrome":#谷歌浏览器
                return (ua.chrome)
            elif self.Values.lower()=="AppleWebKit":#AppleWebKit
                return (ua.google)
            elif self.Values.lower()=="Gecko":#Gecko
                return (ua.ff)
            elif self.Values.lower()=="safari":#apple safari
                return (ua.safari)
            else:
                return (ua.random)#如果用户瞎几把乱输使用随机头
        except:
            return "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36"#报错使用随机头


class NmapScan:#扫描端口类
    def __init__(self,Url):
        Host=IpProcess(Url)#调用IP处理函数
        self.Host= Host#提取后的网址或者IP
        #self.Port = "445"#测试
        self.Port = "1-65535"#如果用户没输入就扫描全端口

    def ScanPort(self):
        try:
            Nmap = nmap.PortScanner()
            ScanResult = Nmap.scan(self.Host, self.Port, '-sV')
            HostAddress= re.compile('{\'([\d.]+)\': {').findall(str(ScanResult['scan']))[0]#只能用正则取出ip的值
            for port in ScanResult['scan'][HostAddress]['tcp']:
                Nmaps=ScanResult['scan'][HostAddress]['tcp'][port]
                NmapDB(Nmaps,port,self.Host,HostAddress).Write()
        except IOError:
             print("Please enter the correct nmap scan command.")

#为每个任务加个唯一的加密ID然后存入，后面和读取数据库后进行全量端口爆破做铺垫
class NmapDB:#NMAP的数据库
    def __init__(self,Nmap,port,ip,domain):
        self.state = Nmap['state']  # 端口状态
        self.reason = Nmap['reason']  # 端口回复
        self.name = Nmap['name']  #  	服务名称
        self.product = Nmap['product']  # 服务器类型
        self.version = Nmap['version']  # 版本
        self.extrainfo = Nmap['extrainfo']  # 其他信息
        self.conf = Nmap['conf']  # 配置
        self.cpe = Nmap['cpe']  # 消息头
        self.port = port  # 有哪些端口
        self.ip = ip  # 扫描的目标
        self.domain=domain #域名
        # 如果数据库不存在的话，将会自动创建一个 数据库
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        # 获取所创建数据的游标
        self.cur = self.con.cursor()
        # 创建表
        try:
            self.cur.execute("CREATE TABLE Nmap\
                        (domain TEXT,\
                        ip TEXT,\
                        port TEXTL,\
                        state TEXT,\
                        name TEXT,\
                        product TEXT,\
                        reason TEXT,\
                        version TEXT,\
                        extrainfo TEXT,\
                        conf TEXT,\
                        cpe TEXT)")
        except:
            pass

    def Write(self):
        try:

            #sql_insert = """INSERT INTO Nmap (domain,ip,port,state,name,product,reason,version,extrainfo,conf,cpe) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(self.domain,self.ip,self.port,self.state,self.name,self.product,self.reason,self.version,self.extrainfo,self.conf,self.cpe)
            self.cur.execute("""INSERT INTO Nmap (domain,ip,port,state,name,product,reason,version,extrainfo,conf,cpe) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(self.domain,self.ip,self.port,self.state,self.name,self.product,self.reason,self.version,self.extrainfo,self.conf,self.cpe,))
            # 提交
            self.con.commit()
            self.con.close()
        except:
            pass

class NmapRead:#读取Nmap扫描后的数据
    def __init__(self,id):
        self.id = id  # 每个任务唯一的ID值
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        self.cur = self.con.cursor()
    def Read(self):
        try:
            port_list=[]
            self.cur.execute("select * from Nmap where id =?", (self.id,))
            values = self.cur.fetchall()
            for i in values:
                if i[3]=="open":
                    port_list.append(i[2])#发送端口号到列表中
            self.con.close()
            return port_list
        except:
            pass

class SessionKey:
    def __init__(self,username,session_key,session_time):
        self.username=username
        self.session_key=session_key
        self.session_time=session_time
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        # 获取所创建数据的游标
        self.cur = self.con.cursor()
        # 创建表
        try:
            self.cur.execute("CREATE TABLE session_key\
                        (username TEXT PRIMARY KEY,\
                        session_key TEXT,\
                        session_time TEXTL)")
        except:
            pass
    def write(self):#把验证后的两个session写入数据库中
        try:

            # sql_insert = """INSERT INTO Nmap (domain,ip,port,state,name,product,reason,version,extrainfo,conf,cpe) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(self.domain,self.ip,self.port,self.state,self.name,self.product,self.reason,self.version,self.extrainfo,self.conf,self.cpe)
            self.cur.execute("""INSERT INTO session_key (username,session_key,session_time) VALUES (?,?,?)""",(self.username, self.session_key, self.session_time,))
            # 提交
            self.con.commit()
            self.con.close()
        except:
            pass
    def read(self):#对传入的两个session进行验证
        try:
            self.cur.execute("select * from session_key where username =?", (self.username,))
            values = self.cur.fetchall()
            for i in values:
                if i[0]==self.username and self.session_key==i[1] and self.session_time==i[2]:
                    self.con.close()
                    return 1
            self.con.close()
            return 0
        except:
            return 0
class BlastingDB:#数据库爆破模块，到时候要重写移除这里
    def __init__(self,DataBaseUserFileName,DataBasePasswrodFileName):
        self.DataBaseUserFileName=DataBaseUserFileName
        self.DataBasePasswrodFileName = DataBasePasswrodFileName
    def BoomDB(self,Url):
        global BoomDBFileName
        try:
            if self.DataBaseUserFileName!=None and self.DataBasePasswrodFileName!=None:
                with open(self.DataBaseUserFileName, encoding='utf-8') as f:
                    for UserLine in tqdm(f,ascii=True,desc="DatabaseBlastingProgress:"):
                        User = UserLine
                        with open(self.DataBasePasswrodFileName, encoding='utf-8') as fp:
                            for PassWrodLine in tqdm(fp,desc="Single user password progress",ascii=True):
                                PassWrod = PassWrodLine
                                try:
                                    Url=IpProcess(Url)
                                    conn = pymysql.connect(Url, User, PassWrod, 'mysql', 3306)
                                    conn.close()
                                    if sys.platform == "win32" or sys.platform == "cygwin":
                                        BoomDBFileName = os.path.split(os.path.realpath(__file__))[
                                                             0] + "\\ScanResult\\BoomDBOutputFile.txt"
                                    elif sys.platform == "linux" or sys.platform == "darwin":
                                        BoomDBFileName = os.path.split(os.path.realpath(__file__))[0]+"/ScanResult/BoomDBOutputFile.txt"
                                    with open(BoomDBFileName, 'a', encoding='utf-8') as fg:
                                        fg.write("Database address:"+Url +"      Account:"+User+"      Passwrod:"+PassWrod+ "\n")  # 写入单独的扫描结果文件中
                                except Exception as e:
                                    pass
        except IOError:
            print("Input file content format is incorrect")
        try:
            if self.DataBaseUserFileName == None or self.DataBasePasswrodFileName==None:
                with open(os.path.split(os.path.realpath(__file__))[0]+"\\Dictionary\\MysqlUser.txt", encoding='utf-8') as f:#打开默认的User文件
                    for UserLine in tqdm(f,ascii=True,desc="Total progress of the blasting database:"):
                        User = UserLine
                        with open(os.path.split(os.path.realpath(__file__))[0]+"/Dictionary/MysqlPasswrod.txt", encoding='utf-8') as fp:#打开默认的密码文件
                            for PassWrodLine in tqdm(fp,desc="Single user password progress",ascii=True):
                                PassWrod = PassWrodLine
                                try:
                                    Url = IpProcess(Url)
                                    conn = pymysql.connect(Url, User, PassWrod, 'mysql', 3306)
                                    conn.close()
                                    if sys.platform == "win32" or sys.platform == "cygwin":
                                        BoomDBFileName = os.path.split(os.path.realpath(__file__))[
                                                             0] + "\\ScanResult\\BoomDBOutputFile.txt"
                                    elif sys.platform == "linux" or sys.platform == "darwin":
                                        BoomDBFileName = os.path.split(os.path.realpath(__file__))[0]+"/ScanResult/BoomDBOutputFile.txt"
                                    with open(BoomDBFileName, 'a', encoding='utf-8') as fg:
                                        fg.write("Database address:"+Url +"      Account:"+User+"      Passwrod:"+PassWrod+ "\n")  # 写入单独的扫描结果文件中
                                except Exception as e:
                                    pass
        except IOError:
            print("Input file content format is incorrect")


class BotVulnerabilityInquire:#机器人数据查询
    def __init__(self, token):  # 先通过id查，后面要是有用户ID 再运行的时候创建一个用户信息的表或者什么的到时候再说
        self.token = token
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform == "linux" or sys.platform == "darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        # 获取所创建数据的游标
        self.cur = self.con.cursor()
    def Number(self):#用来查询存在漏洞的个数
        self.cur.execute("select * from Medusa where timestamp =?", (self.token,))
        values = self.cur.fetchall()
        Number=len(values)
        self.con.close()
        return Number

    def Inquire(self):
        self.cur.execute("select * from Medusa where timestamp =?", (self.token,))
        values = self.cur.fetchall()
        result_list=[]#存放json的返回结果列表用

        for i in values:
            json_values = {}
            json_values["url"] = i[1]
            json_values["name"] = i[2]
            json_values["details"] = i[7]
            result_list.append(json_values)
        self.con.close()
        return result_list

class GithubCveApi:#CVE写入表
    def __init__(self,CveJsonList):
        try:
            self.cve_id = CveJsonList["id"]  # 唯一的ID
            self.cve_name =CveJsonList["name"]  # 名字
            self.cve_html_url =CveJsonList["html_url"] # 链接
            self.cve_created_at=CveJsonList["created_at"]  # 创建时间
            self.cve_updated_at=CveJsonList["updated_at"]  # 更新时间
            self.cve_pushed_at=CveJsonList["pushed_at"] # push时间
            self.cve_forks_count=CveJsonList["forks_count"] # fork人数
            self.cve_watchers_count=CveJsonList["watchers_count"] # star人数
            self.cve_write_time=str(int(time.time()))#写入时间



            # 如果数据库不存在的话，将会自动创建一个 数据库
            if sys.platform == "win32" or sys.platform == "cygwin":
                self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
            elif sys.platform == "linux" or sys.platform == "darwin":
                self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0]+"/Medusa.db")
            # 获取所创建数据的游标
            self.cur = self.con.cursor()
            # 创建表
            try:
                #如果设置了主键那么就导致主健值不能相同，如果相同就写入报错
                self.cur.execute("CREATE TABLE GithubCVE\
                            (id INTEGER PRIMARY KEY,\
                            github_id TEXT NOT NULL,\
                            name TEXT NOT NULL,\
                            html_url TEXT NOT NULL,\
                            created_at TEXT NOT NULL,\
                            updated_at TEXT NOT NULL,\
                            pushed_at TEXT NOT NULL,\
                            forks_count TEXT NOT NULL,\
                            watchers_count TEXT NOT NULL,\
                            write_time TEXT NOT NULL,\
                            update_write_time TEXT NOT NULL)")
            except:
                pass
        except:
            pass
    def Write(self):
        try:
            self.cur.execute("""INSERT INTO GithubCVE (github_id,name,html_url,created_at,updated_at,pushed_at,forks_count,watchers_count,write_time,update_write_time) \
    VALUES (?,?,?,?,?,?,?,?,?,?)""",(self.cve_id,self.cve_name,self.cve_html_url,self.cve_created_at,self.cve_updated_at, self.cve_pushed_at, self.cve_forks_count,self.cve_watchers_count,self.cve_write_time,self.cve_write_time,))
            # 提交
            self.con.commit()
            self.con.close()
        except:
            pass
    def Update(self,UpdateTime):
        self.cve_update_write_time = str(UpdateTime)  # 跟新时间
        try:
            self.cur.execute("""UPDATE GithubCVE SET forks_count = ?,updated_at=?,pushed_at=?,watchers_count=?,update_write_time=?  WHERE github_id = ?""", (self.cve_forks_count,self.cve_updated_at,self.cve_pushed_at,self.cve_watchers_count,self.cve_update_write_time,self.cve_id,))
            # 提交
            self.con.commit()
            self.con.close()
        except:
            pass
    def Sekect(self):

        self.cur.execute(
            """SELECT * FROM GithubCVE WHERE github_id=?""",(self.cve_id,))
        values = self.cur.fetchall()
        cve_query_results=None
        if len(values)==0:
            cve_query_results=False
        if len(values)==1:
            cve_query_results=True
        # 提交
        self.con.commit()
        self.con.close()
        return cve_query_results





class VulnerabilityDetails:#所有数据库写入都是用同一个类
    def __init__(self,medusa,url,token):
        try:
            self.url = str(url)  # 目标域名
            self.timestamp=str(int(time.time()))#获取时间戳
            self.name=medusa['name']#漏洞名称
            self.number = medusa['number']  # CVE编号
            self.author = medusa['author'] # 插件作者
            self.create_date = medusa['create_date']  # 插件编辑时间
            self.algroup = medusa['algroup']  # 插件名称
            self.rank = medusa['rank'] # 漏洞等级
            self.disclosure = medusa['disclosure']  # 漏洞披露时间，如果不知道就写编写插件的时间
            self.details=base64.b64encode(medusa['details'].encode(encoding="utf-8"))# 对结果进行编码写入数据库，鬼知道数据里面有什么玩意
            self.affects=medusa['affects']# 漏洞组件
            self.desc_content=medusa['desc_content']# 漏洞描述
            self.suggest=medusa['suggest']# 修复建议
            self.version = medusa['version']  # 漏洞影响的版本
            self.token=token#传入的token
            # 如果数据库不存在的话，将会自动创建一个 数据库
            if sys.platform == "win32" or sys.platform == "cygwin":
                self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
            elif sys.platform == "linux" or sys.platform == "darwin":
                self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0]+"/Medusa.db")
            # 获取所创建数据的游标
            self.cur = self.con.cursor()
            # 创建表
            try:
                #如果设置了主键那么就导致主健值不能相同，如果相同就写入报错
                self.cur.execute("CREATE TABLE Medusa\
                            (id INTEGER PRIMARY KEY,\
                            url TEXT NOT NULL,\
                            name TEXT NOT NULL,\
                            affects TEXT NOT NULL,\
                            rank TEXT NOT NULL,\
                            suggest TEXT NOT NULL,\
                            desc_content TEXT NOT NULL,\
                            details TEXT NOT NULL,\
                            number TEXT NOT NULL,\
                            author TEXT NOT NULL,\
                            create_date TEXT NOT NULL,\
                            disclosure TEXT NOT NULL,\
                            algroup TEXT NOT NULL,\
                            version TEXT NOT NULL,\
                            timestamp TEXT NOT NULL,\
                            token TEXT NOT NULL)")
            except:
                pass
        except:
            pass
    def Write(self):#统一写入
        try:
            self.cur.execute("""INSERT INTO Medusa (url,name,affects,rank,suggest,desc_content,details,number,author,create_date,disclosure,algroup,version,timestamp,token) \
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            self.url, self.name, self.affects, self.rank, self.suggest, self.desc_content, self.details, self.number,
            self.author, self.create_date, self.disclosure, self.algroup, self.version, self.timestamp, self.token,))
            # 提交
            self.con.commit()
            self.con.close()
        except:
            pass



class VulnerabilityInquire:#数据库查询仅限于web版
    def __init__(self):
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        # 获取所创建数据的游标
        self.cur = self.con.cursor()
    def Inquire(self,token):
        try:
            self.cur.execute("select * from Medusa where token =?",(str(token),))
            values = self.cur.fetchall()
            result_list = []  # 存放json的返回结果列表用

            for i in values:
                json_values = {}
                json_values["url"] = i[1]
                json_values["name"] = i[2]
                json_values["affects"] = i[3]
                json_values["rank"] = i[4]
                json_values["suggest"] = i[5]
                json_values["desc_content"] = i[6]
                json_values["details"] = i[7]
                json_values["number"] = i[8]
                json_values["author"] = i[9]
                json_values["create_date"] = i[10]
                json_values["disclosure"] = i[11]
                json_values["algroup"] = i[12]
                json_values["version"] = i[13]
                json_values["timestamp"] = i[14]
                json_values["token"] = i[15]
                result_list.append(json_values)
            self.con.close()
            return result_list
        except:
            return ""

class login:#登录
    def __init__(self,username):
        self.username=username
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        # 获取所创建数据的游标
        self.cur = self.con.cursor()
    def logins(self):#根据数据进行查询用户名和数据库是否相等
        self.cur.execute("select * from user_info where user =?",(self.username,))
        values = self.cur.fetchall()
        try:
            global passwd
            for i in values:
                passwd= i[1]#获取密码
            if passwd!=None:#判断是否在数据库中
                self.con.close()
                return passwd
        except:
            return 0
class UserTable:#注册
    def __init__(self):
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        # 获取所创建数据的游标
        self.cur = self.con.cursor()
        # 创建表
        try:
            self.cur.execute("CREATE TABLE UserInfo\
                            (id INTEGER PRIMARY KEY,\
                            username TEXT NOT NULL,\
                            password TEXT NOT NULL,\
                            mailbox TEXT NOT NULL,\
                            token TEXT NOT NULL,\
                            creation_time TEXT NOT NULL,\
                            update_time TEXT NOT NULL)")
        except:
            pass
    def WriteUser(self,username,password,mailbox,token):#写入新用户
        CreationTime = str(int(time.time())) # 创建时间
        self.AccountToken = token  # 生成的token
        try:
            self.cur.execute("INSERT INTO UserInfo(username,password,mailbox,token,creation_time,update_time)\
            VALUES (?,?,?,?,?,?)",(username, password,mailbox,token,CreationTime,CreationTime,))
            # 提交
            self.con.commit()
            self.con.close()
            return True
        except:
            return False
    def UpdateUser(self,username,token,password):#更新用户密码token
        try:
            self.cur.execute("""UPDATE UserInfo SET password = ?,token=?,update_time=? WHERE username= ?""", (password,token,str(int(time.time())),username,))
            # 提交
            self.con.commit()
            self.con.close()
        except:
            pass
    def CheckUserPresence(self,inquire_user,inquire_mailbox):#查询用户是否存在
        try:
            self.cur.execute("select * from UserInfo where username =? and mailbox = ?",(inquire_user,inquire_mailbox,))
            if self.cur.fetchall():#判断是否有数据
                self.con.close()
                return True
            else:
                return False
        except:
            return False
    def CheckUserToken(self,token):
        try:
            self.cur.execute("select * from UserInfo where token =?", (token,))
            if self.cur.fetchall():#判断是否有数据
                self.con.close()
                return True
            else:
                return False
        except:
            return False

class UserScansWebsiteTable:#用户扫描了哪些网站，时间，模块
    def __init__(self):
        if sys.platform == "win32" or sys.platform == "cygwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "\\Medusa.db")
        elif sys.platform=="linux" or sys.platform=="darwin":
            self.con = sqlite3.connect(os.path.split(os.path.realpath(__file__))[0] + "/Medusa.db")
        # 获取所创建数据的游标
        self.cur = self.con.cursor()
        # 创建表
        try:
            self.cur.execute("CREATE TABLE UserScansWebsite\
                            (id INTEGER PRIMARY KEY,\
                            token TEXT NOT NULL,\
                            url TEXT NOT NULL,\
                            creation_time TEXT NOT NULL,\
                            module TEXT NOT NULL)")
        except:
            pass
    def Write(self,token,url,creation_time,module):#写入新用户
        self.AccountToken = token  # 生成的token
        try:
            self.cur.execute("INSERT INTO UserScansWebsite(token,url,creation_time,module)\
            VALUES (?,?,?,?)",(token,url,creation_time,module,))
            # 提交
            self.con.commit()
            self.con.close()
        except:
            pass


class ErrorLog:#报错写入日志
    def __init__(self):
        global filename
        if sys.platform == "win32" or sys.platform == "cygwin":
            filename=os.path.split(os.path.realpath(__file__))[0]+'\\my.log'#获取当前文件所在的目录，即父目录
        elif sys.platform == "linux" or sys.platform == "darwin":
            filename = os.path.split(os.path.realpath(__file__))[0] + '/my.log'  # 获取当前文件所在的目录，即父目录
        #filename=os.path.realpath(__file__)#获取当前文件名
        log_format = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
        logging.basicConfig(filename=filename, filemode='a', level=logging.INFO,
                            format=log_format)  # 初始化配置信息
    def Write(self,url,name):
        logging.info(url)
        logging.warning(name)

class Dnslog:#Dnslog判断
    def __init__(self):
        H = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        salt=""
        for i in range(15):
            salt += random.choice(H)
        self.host=str(salt+"."+dns_log_url)
    def dns_host(self):
        return str(self.host)
    def result(self):
        #DNS判断后续会有更多的DNS判断，保持准确性
         return self.ceye_dns()
    def ceye_dns(self):
        try:
            # status = requests.post('http://log.ascotbe.com/api/validate', timeout=2,data=data)
            # code=status.status_code
            # if code == 200:
            status = requests.get("http://api.ceye.io/v1/records?token="+dns_log_key+"&type=dns&filter=", timeout=6)
            dns_log_text=status.text
            if dns_log_text.find(self.host)!=-1:#如果找到Key
                return True
            else:
                return False
        except Exception:
            ErrorLog().Write(self.host,"Dnslog")


class Ysoserial:
    def __init__(self):
        system_type=sys.platform
        if system_type=="win32" or system_type=="cygwin":
            self.ysoserial=os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "."),'Dictionary\\ysoserial.jar')
        elif system_type=="linux" or system_type=="darwin":
            self.ysoserial= os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "."),'Dictionary/ysoserial.jar')
    def result(self):
        return self.ysoserial
    
class randoms:#生成随机数
    def result(self,nub):
        H = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        salt = ""
        for i in range(nub):
            salt += random.choice(H)
        return salt
class UrlProcessing:#URL处理函数
    def result(self,url):
        if url.startswith("http"):#判断是否有http头，如果没有就在下面加入
            res = urllib.parse.urlparse(url)
        else:
            res = urllib.parse.urlparse('http://%s' % url)
        return res.scheme, res.hostname, res.port

class Proxies:#代理处理函数
    def result(self, proxies_ip):
        if proxies_ip==None:
            return proxies_ip
        else:
            return {"http": "http://{}".format(proxies_ip), "https": "https://{}".format(proxies_ip)}




class ThreadPool:#线程池，所有插件都发送过来一起调用
    def __init__(self):
        self.ThreaList=[]#存放线程列表
        self.text=0#统计线程数
    def Append(self,plugin,url,Values,Token,proxies):
        self.text+=1
        ua = AgentHeader().result(Values)
        self.ThreaList.append(threading.Thread(target=plugin, args=(url,ua,Token,proxies)))
    def SubdomainAppend(self,plugin,Url,SubdomainJudge):
        self.ThreaList.append(threading.Thread(target=plugin, args=(Url, SubdomainJudge)))
    def NmapAppend(self,plugin,Url):
        self.ThreaList.append(threading.Thread(target=plugin, args=(Url)))
    def Start(self,ThreadNumber):
        if debug_mode:#如果开了debug模式就不显示进度条
            for t in self.ThreaList:  # 开启列表中的多线程
                t.start()
                while True:
                    # 判断正在运行的线程数量,如果小于5则退出while循环,
                    # 进入for循环启动新的进程.否则就一直在while循环进入死循环
                    if (len(threading.enumerate()) < ThreadNumber):
                        break
            for p in self.ThreaList:
                p.join()
        else:#如果没开Debug就改成进度条形式
            for t in tqdm(self.ThreaList,ascii=True,desc="\033[1;40;32m[ + ] Medusa scan progress bar\033[0m"): # 开启列表中的多线程
                t.start()
                while True:
                    # 判断正在运行的线程数量,如果小于5则退出while循环,
                    # 进入for循环启动新的进程.否则就一直在while循环进入死循环
                    if (len(threading.enumerate()) < ThreadNumber):
                        break
            for p in tqdm(self.ThreaList,ascii=True,desc="\033[1;40;32m[ + ] Medusa cleanup thread progress\033[0m"):
                p.join()
        self.ThreaList.clear()#清空列表，防止多次调用导致重复使用

class Prompt:#输出横幅，就是每个组件加载后输出的东西
    def __init__(self,name):
        self.name=name
        if debug_mode:
            pass
        else:
            sizex, sizey=CommandLineWidth().getTerminalSize()
            prompt="\033[1;40;32m[ + ] Loading attack module: \033[0m" + "\033[1;40;35m{}\033[0m".format(self.name)
            PromptSize=sizex-len(prompt)+28
            FillString = ""
            for i in range(0, PromptSize):
                FillString = FillString + " "
            sys.stdout.write("\r" + prompt + FillString)
            time.sleep(0.2)
            sys.stdout.flush()

class CommandLineWidth:  # 输出横幅，就是每个组件加载后输出的东西
    def getTerminalSize(self):
        import platform  # 获取使用这个软件的平台
        current_os = platform.system()  # 获取操作系统的具体类型
        tuple_xy = None
        if current_os == 'Windows':
            tuple_xy = self._getTerminalSize_windows()
            if tuple_xy is None:
                tuple_xy = self._getTerminalSize_tput()
                # needed for window's python in cygwin's xterm!
        if current_os == 'Linux' or current_os == 'Darwin' or current_os.startswith('CYGWIN'):
            tuple_xy = self._getTerminalSize_linux()
        if tuple_xy is None:
            tuple_xy = (80, 25)  # default value
        return tuple_xy

    # 函数名前下划线代表这是一个私有方法 这样我们在导入我们的这个模块的时候 python是不会导入方法名前带有下划线的方法的
    def _getTerminalSize_windows(self):
        res = None
        try:
            from ctypes import windll, create_string_buffer
            """
            STD_INPUT_HANDLE = -10  获取输入的句柄
            STD_OUTPUT_HANDLE = -11 获取输出的句柄
            STD_ERROR_HANDLE = -12  获取错误的句柄
            """
            h = windll.kernel32.GetStdHandle(-12)  # 获得输入、输出/错误的屏幕缓冲区的句柄
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        except:
            return None
        if res:
            import struct
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
        else:
            return None

    # 函数名前下划线代表这是一个私有方法 这样我们在导入我们的这个模块的时候 python是不会导入方法名前带有下划线的方法的

    def _getTerminalSize_tput(self):
        try:
            import subprocess
            proc = subprocess.Popen(["tput", "cols"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            output = proc.communicate(input=None)
            cols = int(output[0])
            proc = subprocess.Popen(["tput", "lines"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            output = proc.communicate(input=None)
            rows = int(output[0])
            return (cols, rows)
        except:
            return None
    def _getTerminalSize_linux(self):
        def ioctl_GWINSZ(fd):
            try:
                import fcntl, termios, struct, os
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            except:
                return None
            return cr

        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            try:
                env = os.environ
                cr = (env['LINES'], env['COLUMNS'])
            except:
                return None
        return int(cr[1]), int(cr[0])

class ErrorHandling:
    def Outlier(self,error,plugin_name):
        self.error=str(error)
        self.plugin_name=plugin_name
        if debug_mode:
            self.Process()
        else:
            pass
    def Process(self):
        if self.error.find("timed out")!=-1:
            self.ErrorBanner(self.plugin_name,"connection timeout")
        elif self.error.find("Invalid URL") != -1:
            self.ErrorBanner(self.plugin_name,"prompts url")
        elif self.error.find("getaddrinfo failed") != -1:
            self.ErrorBanner(self.plugin_name,"get addr info failed")
        elif self.error.find("Invalid header") != -1:
            self.ErrorBanner(self.plugin_name, "prompts header")
        else:
            self.ErrorBanner(self.plugin_name, "unknown")

    def ErrorBanner(self,plugin_name,error):
        print("\033[1;40;31m[ X ] {} plugin {} error\033[0m".format(plugin_name,error))


