# -*- coding: utf-8 -*-
import comic
import ganma

type = "comic"

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    if type == "ganma":
        ganma.crwal_total()
    if type == "comic":
        comic.crawl(input("第几话:"))
