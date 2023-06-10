# -*- coding: utf-8 -*-
import comic
import ganma
import ichijin

type = "ichijin"

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':

    if type == "ganma":
        # ganma的漫画名字在ganma.py里面的find里输入，因为刚写的时候不熟悉python，结构很烂，懒得重构了，把comic的优化了一下
        ganma.crwal_total()
    elif type == "comic":
        comic = comic.Comic(input("漫画名字:"), input("第几话:"))
        comic.crawl()

    elif type == "ichijin":
        ichijin = ichijin.Ichijin("屑", "2")
        ichijin.crawl()
