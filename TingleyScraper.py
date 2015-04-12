# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2
import httplib
from urlparse import urlparse

import csv
import re
from time import sleep

#searchTerm = '美国' 
outputFile = 'test.csv'
logFile = 'test.log'
base_url = "http://search.tianya.cn/bbs?q="# + searchTerm + "&pn="
threadBase = 'http://bbs.tianya.cn'
delay = 1
#searchBase = 'http://search.tianya.cn/bbs?q='
iterator = "&pn="
#base_url = "http://bbs.tianya.cn/post-worldlook-1432690-1.shtml"

def scrapeSearch(url):

    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    links = []
    titles = []

    for link in soup.find_all('h3'):
        for child in link.children:
            links.append(child.get('href'))
            title = ''
            for ele in child.contents:
                title += str(ele)
            titles.append(title.replace("<span class=\"kwcolor\">", "").replace("</span>",""))
#            print child.get('href')

    return links, titles

def scrapeThread(url, writer, title):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
   
    # Get the title
    #title = soup.find_all(class_='s_title')[0].string
   
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

def checkUrl(url):
    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


if __name__ == '__main__':

    # load the desired search term
    if len(sys.argv) != 2:
        print "Select search term - 1: 美国 (America), 2: 美利坚 (United States of America), 3: 山姆大叔 (Uncle Sam)"
        sys.exit()

    param = sys.argv[1]
    if param == '1':
        searchTerm = '美国'
    elif param == '2':
        searchTerm = '美利坚'
    elif param == '3':
        searchTerm = '山姆大叔'
    else:
        print "Options - 1: 美国 (America), 2: 美利坚 (United States of America), 3: 山姆大叔 (Uncle Sam)"
        sys.exit()

    base_url += base_url + searchTerm + iterator


    writer = csv.writer(open(outputFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))
    logger = csv.writer(open(logFile, 'wb'), delimiter = '|')
    logger.writerow(('Broken links'))

    # go through all the next pages buttons, find the one with the largest value
    # which should be the last page
    sMax = 2

    page = urllib2.urlopen(base_url + '1')
    soup = BeautifulSoup(page)

    # find out how many pages of search result pages there are
    for result in soup.find_all(href=re.compile("javascript")):
        # iterate through all the links with 'javascript' and find the largest number
        if result.string != None:
            if result.string.isdigit():
                num = int(result.string)
                if num > sMax:
                    sMax = num

    # build a list of threads to scrape from one search result page
    for i in xrange(sMax):
        print "Scraping search result page ", i+1
        toScrape, titles = scrapeSearch(base_url + str(i + 1))

        # actually scrape the threads
        print "Scraping threads..."
        for j in xrange(len(toScrape)):
            # check that the URL is valid
            if checkUrl(toScrape[j]):
                result = scrapeThread(toScrape[j], writer,titles[j])
            else:
                logger.writerow((toScrape[j]))

        sleep(delay)
