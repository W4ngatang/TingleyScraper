# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2
import csv
import re

searchTerm = '美国' 
outputFile = 'test4.csv'
#base_url = "http://bbs.tianya.cn/post-worldlook-1432690-1.shtml"
base_url = "http://search.tianya.cn/bbs?q=" + searchTerm + "&pn="
threadBase = 'http://bbs.tianya.cn'
#searchBase = 'http://search.tianya.cn/bbs?q='
#iterator = "&pn="

def scrapeSearch(url):

    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    links = []

    for link in soup.find_all('h3'):
        for child in link.children:
            links.append(child.get('href'))
#            print child.get('href')

    return links

def scrapeThread(url, writer):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
   
    # Get the title
    title = soup.find_all(class_='s_title')[0].string
   
    # Get the contents of the posts   
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

    # Get the next thread page if there is one
    nextPage = soup.find_all(class_="js-keyboard-next")
    if nextPage != []:
        scrapeThread(threadBase + nextPage[0].get('href'), writer)


if __name__ == '__main__':

    writer = csv.writer(open(outputFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))

    # go through all the next pages buttons, find the one with the largest value
    # which should be the last page
    sMax = 2

    page = urllib2.urlopen(base_url + '1')
    soup = BeautifulSoup(page)

    # find out how many pages of search result pages there are
    for result in soup.find_all(href=re.compile("javascript")):
        if result.string != None:
            if result.string.isdigit():
                num = int(result.string)
                if num > sMax:
                    sMax = num

    # build a list of threads to scrape
    toScrape = []
    for i in xrange(sMax):
        toScrape.append(scrapeSearch(base_url + str(i + 1)))

    # actually scrape the threads
    for target in toScrape:
        result = scrapeThread(target)
