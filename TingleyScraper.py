# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2
import csv

outputFile = 'test.csv'
#base_url = "http://bbs.tianya.cn/post-worldlook-1432690-1.shtml"
base_url = "http://search.tianya.cn/bbs?q=美国"

def scrapeSearch(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    links = []

    for link in soup.find_all('h3'):
        for child in link.children:
            links.append(child.get('href'))
            print child.get('href')

    return links

def scrapeThread(url):
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
#            writer.writerow((title, url, date, time, content))
            print title,",",url,",",date,",",time,",",content
            print '\n'

if __name__ == '__main__':

#    writer = csv.writer(open(outputFile, 'wb'), delimiter = ',')
#    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))

    toScrape = scrapeSearch(base_url)
    print "Done gathering URLs, scraping..."

    for target in toScrape:
        scrapeThread(target)

    '''
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
            time = post.contents[3].string[3:13]
            date = post.contents[3].string[14:]
        elif 'bbs-content' in post['class']:
            for child in post.children:
                contents = child.encode('utf-8')
                content += contents.replace("<br/>", "").strip()
            writer.writerow((title, url, date, time, content))
    '''
