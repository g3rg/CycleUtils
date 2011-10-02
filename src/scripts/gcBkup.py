'''
Created 30/09/2011
@author g3rg
'''

import urllib2
import cookielib
import datetime
import argparse
import re
import os

from BeautifulSoup import BeautifulSoup, SoupStrainer

URL_ROOT = "http://connect.garmin.com/"
URL_ROOT_HTTPS = "https://connect.garmin.com/"
URL_SIGN_IN_HTTP = URL_ROOT + "signin"
URL_SIGN_IN_HTTPS = URL_ROOT_HTTPS + "signin"
URL_USERNAME = URL_ROOT + "/user/username"
URL_ACTIVITY_BASE = URL_ROOT + "activities"
URL_TCX_BASE = URL_ROOT + "/proxy/activity-service-1.0/tcx/activity/"
URL_TCX_SUFFIX = "?full=true"

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

def makeActivityPath(id):
    return "activity_tcx" + os.path.sep + id + ".tcx"

def fetchActivitiesTCX(activities):
    if not os.path.isdir("activity_tcx"):
        os.mkdir("activity_tcx")
    
    for activity in activities:
        tcx = fetchPage(URL_TCX_BASE + str(activity) + URL_TCX_SUFFIX)
        f = open(makeActivityPath(str(activity)), "w")
        f.write(tcx)
        f.close

def indexTCX():
    if not os.path.isdir("activity_tcx"):
        print "No activity directory, please download your activities first"
    else:
        for filename in os.listdir("activity_tcx"):
            soup = BeautifulSoup(open("activity_tcx" + os.path.sep + filename, "r").read())
            print str(len(soup.findAll("Activity"))) + " activities found"

def getActivityList(update=False):
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
            if moreData:
                for tup in activity.attrs:
                    if tup[0] == 'href':
                        id = tup[1][len('/activity/'):]
                        activityData.append(id)
                        if update and os.path.exists(makeActivityPath(id)):
                            moreData = False
                        break
            else:
                break
                
        
        # Determine if we are on the last page
        if moreData:
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
    
    p.add_argument('--user','-u', required=True, help="Your Garmin Connect username")
    p.add_argument('--password', '-p', required=True, help="Your Garmin Connect password")
    p.add_argument('--debug', '-d', action="store_true", help="If set, will store cookies and fetched pages in text files")
    p.add_argument('--version', action="version", version='%(prog)s 0.1')
    p.add_argument('--verbose', action="store_true", help="Print out more messages during processing")
    p.add_argument('command', nargs='?', default='testlogin', choices={'testlogin', 'activity_ids', 'fetch_all_tcx', 
                'update_tcx', 'index_tcx'}, help="What do you want to do with Garmin Connect?")
    
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
        elif options.command == "activity_ids":
            activities = getActivityList()
            for activity in activities:
                print str(activity)
                
        elif options.command == "fetch_all_tcx":
            activities = getActivityList()
            fetchActivitiesTCX(activities)
            
        elif options.command == "update_tcx":
            activities = getActivityList(True)
            fetchActivitiesTCX(activities)
            
        elif options.command == "index_tcx":
            indexTCX()
        else:
            print "Command <" + options.command + "> is not understood, try --help to see help"
    else:
        print "Failed to login with the username and password supplied"

if __name__ == "__main__":
    doMain()
