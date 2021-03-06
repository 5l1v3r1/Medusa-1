#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from Modules.Cms.B2Bbuilder import B2BbuilderBackgroundCommandExecutionVulnerability
from Modules.Cms.B2Bbuilder import B2BbuilderContainsVulnerabilitiesLocally
from Modules.Cms.B2Bbuilder import B2BbuilderHeadSQLInjectionVulnerability
from Modules.Cms.B2Bbuilder import B2BbuilderSQLInjectionVulnerability
from Modules.Cms.B2Bbuilder import B2BbuilderSQLInjectionVulnerability2
from Modules.Cms.B2Bbuilder import B2BbuilderSQLInjectionVulnerability3
from Modules.Cms.B2Bbuilder import B2BbuilderSQLInjectionVulnerability4
from ClassCongregation import Prompt

def Main(ThreadPool,Url,Values,Token,proxies):
    ThreadPool.Append(B2BbuilderBackgroundCommandExecutionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(B2BbuilderContainsVulnerabilitiesLocally.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(B2BbuilderHeadSQLInjectionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(B2BbuilderSQLInjectionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(B2BbuilderSQLInjectionVulnerability2.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(B2BbuilderSQLInjectionVulnerability3.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(B2BbuilderSQLInjectionVulnerability4.medusa, Url, Values, Token,proxies=proxies)
    Prompt("B2Bbuilder")