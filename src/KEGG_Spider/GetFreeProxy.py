#!/usr/bin/env python
import sys
import requests
import lxml
from lxml import etree
import urllib
import socket
import argparse


__author__ = "Zhikun Wu"
__eamil__ = "598466208@qq.com"
__date__ = "2018.05.14"


class GetFreeProxy():
    """
    Get the free proxy.
    This part is mainly from "https://github.com/jhao104/proxy_pool"
    """
    def __init__(self):
        pass

    @staticmethod
    def freeProxy66(area=34, page=3):
        """
        proxy: http://www.66ip.cn
        area: 1: beijing, 2: shanghai ...
        page: mutiple pages in different areas
        """
        IPPools = set()
        area = int(area)
        page = int(page)
        area = 34 if area > 34 else area
        page = 3 if page > 3 else page
        for area_index in range(1, area+1):
            for i in range(1, page+1):
                url = "http://www.66ip.cn/areaindex_{}/{}.html".format(area_index, i)
                r = requests.get(url)
                status_code = r.status_code
                if status_code != 200:
                    continue
                else:
                    text = r.text
                    html = etree.HTML(text)
                    ip_list = html.xpath("//*[@id='footer']/div/table/tr[position()>1]/td[1]/text()")
                    port_list = html.xpath("//*[@id='footer']/div/table/tr[position()>1]/td[2]/text()")
                    for i, p in zip(ip_list, port_list):
                        IPPools.add("%s:%s" % (i, p))
        return IPPools

    @staticmethod
    def freeProxyXici(page=3):
        url_list = [
            "http://www.xicidaili.com/nn/", # 高匿
            "http://www.xicidaili.com/nt/", # 透明
        ]
        page = int(page)
        for u in url_list:
            for p in range(1, page+1):
                p = p if p > 1 else ""
                url = u + str(p)
                r = requests.get(url)
                status_code = r.status_code
                if status_code != 200:
                    continue
                else:
                    text = r.text
                    html = etree.HTML(text)
                    ip_list = html.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                    # ip_list = html.xpath('.//table[@id="ip_list"]//tr')
                break

def Very_proxy_pool(proxy_pools, out_file):
    # proxy="http://192.168.0.127:80"
    goodProxy = set()
    for proxy in list(proxy_pools):
        proxy_support=urllib.request.ProxyHandler({'http':proxy})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        # socket.setdefaulttimeout(3)
        try:
            response = urllib.request.urlopen('http://icanhazip.com',timeout = 3)
            # print(response.read().decode("utf-8"))
            goodProxy.add(proxy)
        except urllib.error.URLError:
            continue
        except:
            continue
    out_h = open(out_file, 'w')
    for p in list(goodProxy):
        out_h.write("%s\n" % p)
    out_h.close()


def main():
    parser = argparse.ArgumentParser(description="Get the proxy and verify them.")
    parser.add_argument("-o", "--out", help="The output file containing the proxy ip.")
    args = parser.parse_args()
    gg = GetFreeProxy()
    proxy_pools = gg.freeProxy66()
    Very_proxy_pool(proxy_pools, args.out)


if __name__ == '__main__':
    main()