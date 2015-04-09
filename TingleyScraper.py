# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2
import csv

outputFile = 'test.csv'
base_url = "http://bbs.tianya.cn/post-worldlook-1432690-1.shtml"

if __name__ == '__main__':

    page = urllib2.urlopen(base_url)
    soup = BeautifulSoup(page)

    writer = csv.writer(open(outputFile, 'wb'), delimiter = ',')
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))

    # print title of page
    # print url
    url = base_url
    title = soup.find_all(class_='s_title')[0].string
    print title

    # print time and contents
    for post in soup.find_all(True, {'class':['bbs-content', 'atl-info']}):
        content = ''
        if 'atl-info' in post['class']:
#            print "time: ", post.contents[3].string[3:13]
#            print "date: ", post.contents[3].string[14:]
            time = post.contents[3].string[3:13]
            date = post.contents[3].string[14:]
        elif 'bbs-content' in post['class']:
            for child in post.children:
                contents = child.encode('utf-8')
#                print contents.replace("<br/>", "").strip()
                content += contents.replace("<br/>", "").strip()
            writer.writerow((title, url, date, time, content))
