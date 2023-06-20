# -*- coding: utf-8 -*-
import comic
import ganma
import ichijin

type = input("输入抓取网站（comic/ichijin）:")
name = input("输入漫画名字:")
episode = input("输入第几话:")

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':

    if type == "ganma":
        # ganma的漫画名字在ganma.py里面的find里输入，因为刚写的时候不熟悉python，结构很烂，懒得重构了
        ganma.crwal_total()
    elif type == "comic":
        comic = comic.Comic(name, episode)
        comic.crawl()

    elif type == "ichijin":
        ichijin = ichijin.Ichijin(name, episode)
        ichijin.crawl()
