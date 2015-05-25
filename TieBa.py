# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urllib2
import httplib
import requests
from urlparse import urlparse
import csv
import re
from time import sleep
import socket #import error as SocketError
import errno
from random import randint
import pdb

# Heads up: scraper is specific to this forum (tieba.baidu.com)
# so there are many magic numbers floating around
# Also, 'subreplies' are not part of source and
# thus cannot be found using a web scraper
# TODO comment code
# TODO deal with logger
# TODO search results to scrape: 
# http://tieba.baidu.com/f?kw=%E7%BE%8E%E5%9B%BD&ie=utf-8&pn=49600
# note pn skips by 50 (as though each thread has an id)

baseUrl = "http://search.tianya.cn/bbs?q="
searchBase = 'http://tieba.baidu.com/f/search/res?isnew=1&kw=%C3%C0%B9%FA&qw='
searchIterator = '&rn=10&un=&only_thread=0&sm=1&sd=&ed=&ie=gbk&pn='
threadBase = 'http://tieba.baidu.com/p/'
pageBase = 'http://tieba.baidu.com'
threadIterator = '?pn='
maxDelay = 10
minDelay = 1
delta = 1

# Scrape the search results for a list of posts to scrape
def scrapeSearch(url):
    print 'Scraping', url
    try:
        page = requests.get(url, timeout=maxDelay)
    except requests.exceptions.Timeout as e:
        # return blank and will try again
        return [], []
    except requests.exceptions.ConnectionError as e:
        return [], []
    print 'Opened page'
    soup = BeautifulSoup(page.text)

    links = []
    titles = []
    
    results = soup.find('div', class_='s_post_list')
    # I found that even purple links are of class 'bluelink'?
    for link in results.find_all(class_='bluelink'):
        # need to extract thread id to find first page of thread
        threadID = link.get('href')[3:13]
        if threadID.isdigit():
            links.append(threadBase + threadID + threadIterator)
            titles.append(link.text)

    return links, titles

# Scrape a forum post
def scrapeThread(url, writer, logger, title, redo):
    print 'Scraping', url
    # try and open the page
    try:
        page = requests.get(url, timeout=maxDelay)
    # timeout error
    except socket.timeout as e:
        logger.writerow((url, "timeout", title))
        redo.append((url, title))
        print "Error: timeout"
        return redo
    # other errors
    except socket.error as e:
        if e.errno != errno.ECONNRESET:
            raise
        logger.writerow((url, "refused", title))
        redo.append((url, title))
        print "Error: connection refused"
        return redo
    except requests.exceptions.Timeout as e:
        redo.append((url,title))
        print "Error: timeout"
        return redo
    except requests.exceptions.ConnectionError as e:
        redo.append((url,title))
        print "Error: connection refused"
        return redo
    print "Connected"

    try:
        soup = BeautifulSoup(page.text, 'html.parser')
    except httplib.IncompleteRead as e:
        print "Incomplete read"
        logger.writerow((url, 'incomplete', title))
        redo.append((url, title))
        return redo
    print "Soupified"
   
    content = ''
    
    for post in soup.find_all(True, {'class':['d_post_content', 'l_post']}):
        if 'd_post_content' in post['class']:
            #print post.text
            content += post.text.strip().replace('|',';').replace('\n','').replace('\r','')
            if content != '':
                writer.writerow((title, url, date, time, content))
            content = ''
        elif 'l_post' in post['class']:
            raw = post['data-field']
            idx = raw.index('date')+7
            date = raw[idx:idx+10]
            time = raw[idx+11:idx+16]

    return redo

# Find the number of pages in this forum post
def lastPage(url, title, redo):
    try:
        page = requests.get(url, timeout=maxDelay)
    except requests.exceptions.Timeout as e:
        redo.append((url,title))
        print "Error: timeout"
        return -1, redo
    except requests.exceptions.ConnectionError as e:
        redo.append((url, title))
        print "Error: connection refused"
        return -1, redo
    soup = BeautifulSoup(page.text, 'html.parser')
    maxPage = 0 # default to 1
    linkBar = soup.find_all(class_='l_pager')
    if linkBar != [] and len(linkBar[0].contents) >= 2:
        #pdb.set_trace()
        if linkBar[0].contents[-2].get('href')[17:].isdigit(): # get the last page
            maxPage = int(linkBar[0].contents[-2].get('href')[17:])
    return maxPage + 1, redo # for sake of iteration

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
    print "Status:", resp.status
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
        #searchTerm = '美国'
        searchTerm = '%C3%C0%B9%FA'
    elif param == '2':
        searchTerm = '%E7%BE%8E%E5%88%A9%E5%9D%9A'
    elif param == '3':
        searchTerm = '%E5%B1%B1%E5%A7%86%E5%A4%A7%E5%8F%94'
    else:
        print "Parameter Values - 1: 美国 (America), 2: 美利坚 (United States of America), 3: 山姆大叔 (Uncle Sam)"
        sys.exit()

    start = sys.argv[4]
    base_url = searchBase + searchTerm + searchIterator

    outputFile = sys.argv[1]
    logFile = sys.argv[2]
    redos = []

    writer = csv.writer(open(outputFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))
    logger = csv.writer(open(logFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    logger.writerow(('URL', 'Error'))

    # go through all the next pages buttons, find the one with the largest value
    # which should be the last page
    # cheating, looks like max of 76 pages of search results
    sMax = 77

    # build a list of threads to scrape from one search result page
    for i in range(int(start),sMax):
        print "Scraping search result page", i+1
        toScrape = []
        while toScrape == []:
            #toScrape, titles = scrapeSearch(searchUrl + str(i + 1))
            toScrape, titles = scrapeSearch(base_url + str(i + 1))
            sleep(randint(minDelay + delta, maxDelay + delta))
        # to remove duplicates found
        # TODO create a set of all sites visited for more robust
        # duplicate finding
        toScrape = list(set(toScrape))

        # actually scrape the threads
        print "Scraping threads..."
        #print toScrape, titles
        for j in xrange(len(toScrape)):
            maxP, redos = lastPage(toScrape[j]+'1', titles[j], redos)
            if maxP != -1:
                for k in xrange(maxP):
                    # check that the URL is valid
                    #print "Scraping thread: ", toScrape[j]
    #                check, redos = checkUrl(toScrape[j]+str(k+1), logger, titles[j], redos)
    #                if check:
    #                    print 'Checked URL'
                    redos = scrapeThread(toScrape[j]+str(k+1), writer,logger,titles[j], redos)
                    sleep(randint(minDelay, maxDelay))
            #sleep(randint(minDelay + delta, maxDelay + delta))

    # redo whatever missed in first pass through
    print "Redoing errors..."
    while redos != []:
        redo = redos.pop()
        #print 'Scraping thread: ', redo[0]
        redos = scrapeThread(redo[0], writer, logger, redo[1], redos)
