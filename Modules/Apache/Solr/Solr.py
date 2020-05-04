#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from Modules.Apache.Solr import SolrVelocityTemplateRemoteCodeExecutionVulnerability
from Modules.Apache.Solr import SolrVelocityTemplateRemoteCodeExecutionVulnerability2
from Modules.Apache.Solr import SolrRemoteCodeExecutionVulnerability
from Modules.Apache.Solr import SolrRemoteCodeExecutionVulnerability2
from ClassCongregation import Prompt

def Main(ThreadPool,Url,Values,Token,proxies):
    ThreadPool.Append(SolrVelocityTemplateRemoteCodeExecutionVulnerability.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(SolrVelocityTemplateRemoteCodeExecutionVulnerability2.medusa, Url, Values, Token,proxies=proxies)
    ThreadPool.Append(SolrRemoteCodeExecutionVulnerability.medusa, Url, Values,Token,proxies=proxies)
    ThreadPool.Append(SolrRemoteCodeExecutionVulnerability2.medusa, Url, Values, Token,proxies=proxies)
    Prompt("Solr")

