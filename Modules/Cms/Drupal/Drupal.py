#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from Modules.Cms.Drupal import DrupalRemoteCodeExecutionVulnerability

from ClassCongregation import Prompt
def Main(ThreadPool,Url,Values,Token,proxies):
    ThreadPool.Append(DrupalRemoteCodeExecutionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    Prompt("Drupal")