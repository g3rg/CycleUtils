'''
Created 30/09/2011
@author g3rg
'''

import urllib2
import cookielib
import datetime
import argparse
import re

from BeautifulSoup import BeautifulSoup, SoupStrainer

URL_ROOT = "http://connect.garmin.com/"
URL_ROOT_HTTPS = "https://connect.garmin.com/"
URL_SIGN_IN_HTTP = URL_ROOT + "signin"
URL_SIGN_IN_HTTPS = URL_ROOT_HTTPS + "signin"
URL_USERNAME = URL_ROOT + "/user/username"
URL_ACTIVITY_BASE = URL_ROOT + "activities"

HEADERS={'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

DEBUG = False
DEBUG_FILE = "debug.txt"

cookieJar = None

def debugWrite(str):
    if DEBUG:
        output = open(DEBUG_FILE, "a")
        output.write(str)
        output.close()

def debugFetch(req, str=None):
    if DEBUG:
        if str == None:
            body = req.read()
        else:
            body = str
        debugWrite("FETCHED: " + req.url + "\r\n" + body + "\r\n--------- END OF FETCH\r\n")

def createDebugFile(options):
    f = open(DEBUG_FILE, "w")
    f.write("DEBUGGING " + __file__ + "\r\n")
    f.write(datetime.datetime.now().isoformat() + "\r\n")
    f.close()
            
def initCookieJar():
    global cookieJar
    cookieJar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    urllib2.install_opener(opener)

def fetchPage(url, data=None):
    req = urllib2.Request(url, data, HEADERS)
    pgFile = urllib2.urlopen(req)
    pgContents = pgFile.read()
    debugFetch(pgFile, pgContents)
    return pgContents

def login(username, password):    
    fetchPage(URL_SIGN_IN_HTTP)
    
    reqData = "login=login&login%3AloginUsernameField=" + username +"&login%3Apassword=" + password + "&login%3AsignInButton=Sign+In&javax.faces.ViewState=j_id1"
    fetchPage(URL_SIGN_IN_HTTPS, reqData)

    pgContents = fetchPage(URL_USERNAME)
    
    try:
        idx = pgContents.index(":")
        idx2 = pgContents.find('"', idx+2)
        username_returned = pgContents[(idx+2):idx2]
    except:
        username_returned = ""    
   
    if DEBUG:
        global cookieJar
        cookieJar.save("cookies.txt", ignore_discard=True)
    
    return username == username_returned

def createActivityPageData(pageNum = 1):
    return "AJAXREQUEST=_viewRoot&activitiesForm=activitiesForm&activitiesForm%3AactivitiesGrid%3AAs=-1" \
        + "&javax.faces.ViewState=j_id2&ajaxSingle=activitiesForm%3ApageScroller&activitiesForm%3A" \
        + "pageScroller=" + str(pageNum) + "&AJAX%3AEVENTS_COUNT=1"

def getActivityList():
    #Get activities page into session
    fetchPage(URL_ACTIVITY_BASE)
    pageNum = 1
    moreData = True
    activityData = []
    
    activityStrainer = SoupStrainer('a', href=re.compile('/activity/'))
    
    while moreData:
        print "Fetching page " + str(pageNum)
        reqData = createActivityPageData(pageNum)
        pgContents = fetchPage(URL_ACTIVITY_BASE, reqData)
        
        activities = BeautifulSoup(pgContents, parseOnlyThese=activityStrainer)
        
        #Find all links starting with "/activity"
        for activity in activities:
            for tup in activity.attrs:
                if tup[0] == 'href':
                    id = tup[1][len('/activity/'):]
                    activityData.append(id)
                    break
        
        # Determine if we are on the last page
        soup = BeautifulSoup(pgContents)
        pgCounters = soup.find("div", { "class" : "counterContainer" })
        counterSoup = BeautifulSoup(str(pgCounters))
        pageInfo = counterSoup.findAll("b")
        if (pageInfo[1] == pageInfo[2]):
            moreData = False
        
        pageNum = pageNum + 1
        
    return activityData

def handleArgs():
    p = argparse.ArgumentParser(prog='gcBkup',description="Utility for interacting with Garmin Connect")
    
    #p.add_option("--user", "-u", default="dummy")
    #p.add_option("--password", "-p", default="dummy")
    #p.add_option("--command", "-c", default="activity")
    #p.add_option("--debug", default="false")
    #options, arguments = p.parse_args()
    
    p.add_argument('--user','-u', default="dummy")
    p.add_argument('--password', '-p', default="dummy")
    p.add_argument('--debug', '-d', action="store_true")
    p.add_argument('--version', action="version", version='%(prog)s 0.1')
    p.add_argument('command', nargs='?', default='testlogin')
    
    args = p.parse_args()
    
    if args.debug:
        global DEBUG
        DEBUG = True
        createDebugFile(args)
    
    return args

def doMain():
    options = handleArgs()
    
    username = options.user
    password = options.password
    
    initCookieJar()
    
    if login(username, password):
        print "Logged in"
        
        if options.command == "testlogin":
            print "Credentials verified"
        elif options.command == "activity":
            activities = getActivityList()
            print len(activities)
        else:
            print "Command <" + options.command + "> is not understood, try --help to see help"
    else:
        print "Failed to login with the username and password supplied"

if __name__ == "__main__":
    doMain()
