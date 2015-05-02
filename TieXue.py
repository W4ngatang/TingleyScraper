# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup, diagnose
import urllib2
import httplib
from urlparse import urlparse
import csv
import re
from time import sleep
import lxml.html
import pdb
import chardet

base_url = 'http://bbs.tiexue.net/bbs33-0-'
threadBase = 'http://bbs.tianya.cn'
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
            titles.append(link.get('title'))

    return links, titles

def scrapeThread(url, writer, title):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page.decode('gb2312', 'ignore'), 'html5lib')
    pdb.set_trace()
   
#    raw_string = lxml.html.parse(page)
#    print dir(raw_string)
#    print raw_string.getroot()
#    for item in raw_html:
#        print item.text_content()

    print "About to scrape page: ", url
    print soup.encode('windows-1252')
    # Get the contents of the posts   
    for post in soup.find_all():#True, {'class':['js_box', 'bbsp2', 'date']}):
        pdb.set_trace()
        print 'Found one: ', post
        content = ''
        # first post on page
        if 'js_box' in post['class']:
            print 'found js_box'
            for child in post.children:
                if child['class'] == 'bbsp':
                    print child.string
        # subsequent posts
        elif 'bbsp2' in post['class']:
            print 'found bbsp2'
            for child in post.children:
                if child['class'] == 'bbsp':
                    contents = child.encode('utf-8')
                    #content += contents.replace("<br/>", "").strip()
                    print child.encode('utf-8')
            #writer.writerow((title, url, date, time, content))
        # get post date, time
        elif 'date' in post['class']:
            print post.string[0:9]
            print post.string[10:]


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
    if len(sys.argv) != 3:
        print "Usage: TieXue.py outputFile logFile"
        #print "Select search parameter - 1: 美国 (America), 2: 美利坚 (United States of America), 3: 山姆大叔 (Uncle Sam)"
        sys.exit()

    '''
    # Load correct search term
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
    '''

    # Open output file for writing, and maybe log file
    outputFile = sys.argv[1]
    logFile = sys.argv[2]
    writer = csv.writer(open(outputFile, 'wb'), delimiter = '|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('Title', 'URL', 'Date', 'Time', 'Content'))
    logger = csv.writer(open(logFile, 'wb'), delimiter = '|')
    logger.writerow(('Broken links'))

    '''
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
    '''

    # build a list of threads to scrape from one search result page
    for i in xrange(nPages):
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
