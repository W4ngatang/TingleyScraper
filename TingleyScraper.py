# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2

BASE_URL = "http://bbs.tianya.cn/post-worldlook-1432690-1.shtml"

if __name__ == '__main__':
    page = urllib2.urlopen(BASE_URL)
    soup = BeautifulSoup(page)

    # print title of page
    # print url

    # print time and contents
    for post in soup.find_all(True, {'class':['bbs-content', 'atl-info']}):
        if 'atl-info' in post['class']:
            print "New Post: "
            for child in post.children:
                if "时间" in child:
                    print child.encode('utf-8')
        elif 'bbs-content' in post['class']:
            for child in post.children:
                contents = child.encode('utf-8')
                print contents.replace("<br/>", "").strip()
