# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2
import csv

outputFile = 'test3.csv'
#base_url = "http://bbs.tianya.cn/post-worldlook-1432690-1.shtml"
base_url = "http://bbs.tianya.cn/post-worldlook-1438884-1.shtml"
base = "http://bbs.tianya.cn"
#base_url = "http://search.tianya.cn/bbs?q=美国"
iterator = "&pn="

def scrapeThread(url, writer):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    title = soup.find_all(class_='s_title')[0].string

    for post in soup.find_all(True, {'class':['bbs-content', 'atl-info']}):
        content = ''
        if 'atl-info' in post['class']:
            time = post.contents[3].string[3:13]
            date = post.contents[3].string[14:]
        elif 'bbs-content' in post['class']:
            for child in post.children:
                contents = child.encode('utf-8')
                content += contents.replace("<br/>", "").strip()
            writer.writerow((title, url, date, time, content))

    nextPage = soup.find_all(class_="js-keyboard-next")
    if nextPage != []:
        scrapeThread(base + nextPage[0].get('href'), writer)

if __name__ == '__main__':

    writer = csv.writer(open(outputFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))

    scrapeThread(base_url, writer)

    '''
    post = urllib2.urlopen(base_url)
    postSoup = BeautifulSoup(post)
                   
    # Get the title
    title = postSoup.find_all(class_='s_title')[0].string
                     
    # Get the contents of the posts   
    for post in postSoup.find_all(True, {'class':['bbs-content', 'atl-info']}):
        content = ''
        if 'atl-info' in post['class']:
            time = post.contents[3].string[3:13]
            date = post.contents[3].string[14:]
        elif 'bbs-content' in post['class']:
            for child in post.children:
                contents = child.encode('utf-8')
                content += contents.replace("<br/>", "").strip()
        writer.writerow((title, base_url, date, time, content))

    # Get the next thread page if there is one
    nextPage = postSoup.find_all(class_="js-keyboard-next")
    print nextPage
    if nextPage != []:
        print nextPage[0].get('href') 
    '''
