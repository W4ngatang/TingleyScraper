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
import socket #import error as SocketError
import errno
from random import randint

base_url = "http://search.tianya.cn/bbs?q="
searchUrl = 'http://search.tianya.cn/bbs?q=美国+美利坚+山姆大叔&pn='
threadBase = 'http://bbs.tianya.cn'
maxDelay = 10
minDelay = 1
delta = 10
iterator = '&pn='

def scrapeSearch(url):

    try:
        page = urllib2.urlopen(url)
    except httplib.BadStatusLine as e:
        return [], []
    soup = BeautifulSoup(page)

    links = []
    titles = []
    
    results = soup.find('div', class_='searchListOne')
    for link in soup.find_all('h3'):
        for child in link.children:
            links.append(child.get('href'))
            titles.append(child.text)
            #print 'Child:', child.text
            #print 'Link:', child.get('href')

    return links, titles

def scrapeThread(url, writer, logger, title, redo):
    try:
        page = urllib2.urlopen(url, timeout=maxDelay)
    except socket.timeout as e:
        logger.writerow((url, "timeout", title))
        redo.append((url, title))
        print "timeout"
        return redo
    except socket.error as e:
        if e.errno != errno.ECONNRESET:
            raise
        logger.writerow((url, "refused", title))
        redo.append((url, title))
        print "Connection refused"
        return redo
    except urllib2.URLError as e:
        logger.writerow((url, "refused", title))
        redo.append((url, title))
        print "Connection refused"
        return redo
    print "connected"

    try:
        soup = BeautifulSoup(page)
    except httplib.IncompleteRead as e:
        print "Incomplete read"
        logger.writerow((url, 'incomplete', title))
        redo.append((url, title))
        return redo
    print "soupified"
   
    # Get the contents of the posts   
    for post in soup.find_all(True, {'class':['bbs-content', 'atl-info']}):
        content = ''
        if 'atl-info' in post['class']:
            date = post.contents[3].string[3:13]
            time = post.contents[3].string[14:]
        elif 'bbs-content' in post['class']:
            for child in post.children:
                if child.string != None and not child.string.isspace():
                    content += unicode(child.string.encode('utf-8').strip())
            writer.writerow((title, url, date, time, content))

    # Get the next thread page if there is one
    nextPage = soup.find_all(class_="js-keyboard-next")
    if nextPage != []:
        sleep(randint(minDelay,maxDelay))
        print "Next page..."
        redo = scrapeThread(threadBase + nextPage[0].get('href'), writer, logger, title, redo)

    return redo

# Make sure URL is valid so it won't throw an error
def checkUrl(url, logger, title, redo):
    p = urlparse(url)
    try:
        conn = httplib.HTTPConnection(p.netloc)
        conn.request('HEAD', p.path)
        print 'Making request'
        resp = conn.getresponse()
    except socket.error as e:
        if e.errno != errno.ECONNRESET:
            raise
        redo.append((url, title))
        logger.writerow((url, "refused", title))
        print "Connection refused"
        return False, redo
    print "Status: ", resp.status
    if resp.status >= 400:
        logger.writerow((url, "broken", title))
    return resp.status < 400, redo


if __name__ == '__main__':

    # load the desired search term
    if len(sys.argv) != 5:
        print "Usage: TianYa.py outputFile logFile searchTerm startPage"
        sys.exit()

    
    param = sys.argv[3]
    if param == '1':
        searchTerm = '美国'
    elif param == '2':
        searchTerm = '美利坚'
    elif param == '3':
        searchTerm = '山姆大叔'
    else:
        print "Parameter Values - 1: 美国 (America), 2: 美利坚 (United States of America), 3: 山姆大叔 (Uncle Sam)"
        sys.exit()
    base_url += base_url + searchTerm + iterator
    

    outputFile = sys.argv[1]
    logFile = sys.argv[2]
    start = sys.argv[4]
#    baseUrl = searchUrl + start

    writer = csv.writer(open(outputFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))
    logger = csv.writer(open(logFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    logger.writerow(('URL', 'Error'))

    # go through all the next pages buttons, find the one with the largest value
    # which should be the last page
    sMax = 2

#    page = urllib2.urlopen(searchUrl + start)
    page = urllib2.urlopen(base_url + start)
    soup = BeautifulSoup(page)

    redos = []

    # find out how many pages of search result pages there are
    for result in soup.find_all(href=re.compile("javascript")):
        # iterate through all the links with 'javascript' and find the largest number
        if result.string != None:
            if result.string.isdigit():
                num = int(result.string)
                if num > sMax:
                    sMax = num

    # build a list of threads to scrape from one search result page
    for i in range(int(start),sMax):
        print "Scraping search result page ", i+1
        toScrape = []
        while toScrape == []:
            #toScrape, titles = scrapeSearch(searchUrl + str(i + 1))
            toScrape, titles = scrapeSearch(base_url + str(i + 1))
            sleep(randint(minDelay + delta, maxDelay + delta))

        # actually scrape the threads
        print "Scraping threads..."
        for j in xrange(len(toScrape)):
            # check that the URL is valid
            print "Scraping thread: ", toScrape[j]
#            scrapeThread(toScrape[j], writer, titles[j])
            check, redos = checkUrl(toScrape[j], logger, titles[j], redos)
            if check:
                print 'Checked URL'
                redos = scrapeThread(toScrape[j], writer,logger, titles[j], redos)
            sleep(randint(minDelay, maxDelay))
        sleep(randint(minDelay + delta, maxDelay + delta))

    # redo whatever missed in first pass through
    print "Redoing errors..."
    while redos != []:
        redo = redos.pop()
        print 'Scraping thread: ', redo[0]
        redos = scrapeThread(redo[0], writer, logger, redo[1], redos)
