#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from Modules.Cms.Easethink import EasethinkSQLInjectionVulnerability
from Modules.Cms.Easethink import EasethinkSQLInjectionVulnerability1
from Modules.Cms.Easethink import EasethinkCookieInjectionVulnerability
from Modules.Cms.Easethink import YiXiangSQLInjectionVulnerability
from Modules.Cms.Easethink import YiXiangSQLInjectionVulnerability1
from Modules.Cms.Easethink import YiXiangSQLInjectionVulnerability2
from Modules.Cms.Easethink import YiXiangSQLInjectionVulnerability3

from ClassCongregation import Prompt
def Main(ThreadPool,Url,Values,Token,proxies):
    ThreadPool.Append(EasethinkSQLInjectionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(EasethinkSQLInjectionVulnerability1.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(EasethinkCookieInjectionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(YiXiangSQLInjectionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(YiXiangSQLInjectionVulnerability1.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(YiXiangSQLInjectionVulnerability2.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(YiXiangSQLInjectionVulnerability3.medusa, Url, Values, Token,proxies=proxies)
    Prompt("Easethink")