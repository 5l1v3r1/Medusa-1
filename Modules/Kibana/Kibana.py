#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from Modules.Kibana import KibanaArbitraryFileReadVulnerability
from Modules.Kibana import KibanaRemoteCommandExecutionVulnerability
from ClassCongregation import Prompt
def Main(ThreadPool,Url,Values,Token,proxies):
    ThreadPool.Append(KibanaArbitraryFileReadVulnerability.medusa,Url,Values,Token,proxies=proxies)
    ThreadPool.Append(KibanaRemoteCommandExecutionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    Prompt("Kibana")