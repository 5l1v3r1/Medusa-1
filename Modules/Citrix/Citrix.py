#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from Modules.Citrix import CitrixGatewayPathTraversalVulnerability
from Modules.Citrix import CitrixRemoteCodeExecutionVulnerability
from ClassCongregation import Prompt

def Main(ThreadPool,Url,Values,Token,proxies):
    ThreadPool.Append(CitrixRemoteCodeExecutionVulnerability.medusa,Url,Values,Token,proxies=proxies)
    ThreadPool.Append(CitrixGatewayPathTraversalVulnerability.medusa, Url, Values, Token,proxies=proxies)
    Prompt("Citrix")



