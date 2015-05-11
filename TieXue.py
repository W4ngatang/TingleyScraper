# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup, diagnose, element
import urllib2
import requests
import httplib
from urlparse import urlparse
import csv
import re
from time import sleep
import lxml.html
import pdb
import chardet

base_url = 'http://bbs.tiexue.net/bbs33-0-'
iterator = '.html'
delay = 1

nPages = 50 # cheating a bit, but appears like there's only 50 pages of results...

def scrapeSearch(url): 
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    links = []
    titles = []

    for link in soup.find_all(class_='listTitle'):
        if worth(link.get('title')):
            links.append(link.get('href'))
            longTitle = link.get('title').replace('\n','')
            titleIdx = longTitle.find('发帖时间')
            if titleIdx > 0:
                titles.append(longTitle[:titleIdx])

    return links, titles

# return true is not whitespace and is a tag (to filter out comments)
def notSpace(child):
    return hasattr(child, 'string') and child.string != None and not child.string.isspace() and type(child) == element.Tag

def scrapeThread(url, writer, title):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html5lib')
    content = ''
   
    # TODO actually find the contents of each post in order
    # Get the contents of the posts   
    for post in soup.find_all(True, {'class':['js_box', 'bbsp2', 'date']}):
        # first post on page
        if 'js_box' in post['class']:
            print 'got one at ', url, 'post: ', post
            for child in post.children:
                if notSpace(child) and 'bbsp' in child['class']:
                    content += child.string.strip()
        # subsequent posts
        elif 'bbsp2' in post['class']:
            for child in post.children:
                # standard post
                if notSpace(child) and 'bbsp' in child['class']:
                    if content != '':
                        content += ','
                    content += child.string.replace('\n', '').strip()
                # used when poster quotes others
                if notSpace(child) and 'yinyong' in child['class']:
                    if content != '':
                        content += ','
                    content += post.string.replace('\n', '').strip()
        # get post date, time
        elif 'date' in post['class']:
            payload = post.string.split()
            date = payload[0].strip()
            time = payload[1].strip()
            writer.writerow((title,url,date,time,content))
            content = ''


    # Get the next thread page if there is one
    nextPage = soup.find_all(class_="js-keyboard-next")
    if nextPage != []:
        scrapeThread(threadBase + nextPage[0].get('href'), writer, title)

def checkUrl(url):
    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400

def worth(title):
    return '美国' in title or '美利坚' in title or '山姆大叔' in title

if __name__ == '__main__':

    # Throw usage if incorrect
    if len(sys.argv) != 4:
        print "Usage: TieXue.py outputFile logFile startPage"
        #print "Select search parameter - 1: 美国 (America), 2: 美利坚 (United States of America), 3: 山姆大叔 (Uncle Sam)"
        sys.exit()

    # Open output file for writing, and maybe log file
    outputFile = sys.argv[1]
    logFile = sys.argv[2]
    startPage = int(sys.argv[3])
    writer = csv.writer(open(outputFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))
    logger = csv.writer(open(logFile, 'wb'), delimiter = '|')
    logger.writerow(('Broken links'))


    # build a list of threads to scrape from one search result page
    for i in xrange(startPage, nPages):
        print "Scraping search result page ", i+1
        toScrape, titles = scrapeSearch(base_url + str(i + 1) + iterator)

        # actually scrape the threads
        print "Scraping threads..."
        for j in xrange(len(toScrape)):
            # check that the URL is valid
            if checkUrl(toScrape[j]):
                result = scrapeThread(toScrape[j], writer,titles[j])
            else:
                logger.writerow((toScrape[j]))

        sleep(delay)
