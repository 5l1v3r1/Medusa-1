#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from Modules.Nginx import NginxDirectoryTraversalVulnerability
from Modules.Nginx import NginxCRLFInjectionVulnerability
from ClassCongregation import Prompt
def Main(ThreadPool,Url,Values,Token,proxies):
    ThreadPool.Append(NginxDirectoryTraversalVulnerability.medusa,Url,Values,Token,proxies=proxies)
    ThreadPool.Append(NginxCRLFInjectionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    Prompt("Nginx")



