# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2

base_url = "http://bbs.tianya.cn/post-worldlook-1432690-1.shtml"

if __name__ == '__main__':
    page = urllib2.urlopen(base_url)
    soup = BeautifulSoup(page)

    # print title of page
    # print url
    print base_url
    title = soup.find_all(class_='s_title')
    print title[0].string

    # print time and contents
    for post in soup.find_all(True, {'class':['bbs-content', 'atl-info']}):
        if 'atl-info' in post['class']:
            print "time: ", post.contents[3].string[3:13]
            print "date: ", post.contents[3].string[14:]
        elif 'bbs-content' in post['class']:
            for child in post.children:
                contents = child.encode('utf-8')
                print contents.replace("<br/>", "").strip()
