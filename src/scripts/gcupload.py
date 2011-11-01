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

from xml.sax import parse
from xml.sax import ContentHandler


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


def handleArgs():
    p = argparse.ArgumentParser(prog='gcupload',description="Utility for uploading data from Garmin 705 to Garmin Connect")
    
    p.add_argument('--user','-u', required=True, help="Your Garmin Connect username")
    p.add_argument('--password', '-p', required=True, help="Your Garmin Connect password")
    p.add_argument('--debug', '-d', action="store_true", help="If set, will store cookies and fetched pages in text files")
    p.add_argument('--version', action="version", version='%(prog)s 0.1')
    p.add_argument('--verbose', action="store_true", help="Print out more messages during processing")
    
    args = p.parse_args()
    
    if args.debug:
        global DEBUG
        DEBUG = True
        createDebugFile(args)
    
    return args

class GarminDeviceHandler(ContentHandler):
    '''
    SAX Content handler for parsing GarminDevice.xml
    '''

    def __init__(self):    
        self.inModelInfo = False
        self.inDescription = False
        self.description = ''

    def startElement(self, name, attrs):
        if name == 'Model':
            self.inModelInfo = True
        if name == 'Description' and self.inModelInfo:
            self.inDescription = True

    def endElement(self, name):
        if name == 'Model':
            self.inModelInfo = False
        elif name =='Description':
            self.inDescription = False

    def characters(self, char):
        if self.inDescription:
            self.description = (self.description + char)


def findGarminDevices():
    paths = {}
    # TODO Check OS and implement windows drive search as well
    # under linux - look for /media/*/garmin/GarminDevice.xml
    allpaths = os.listdir('/media/')
    for path in allpaths:
        if os.path.isdir('/media/' + os.path.sep + path):
            if os.path.isdir('/media/' + os.path.sep + path + os.path.sep + 'garmin'):
                if os.path.exists('/media/' + os.path.sep + path + os.path.sep + 'garmin' + os.path.sep + 'GarminDevice.xml'):
                    handler = GarminDeviceHandler()
                    parse('/media/' + os.path.sep + path + os.path.sep + 'garmin' + os.path.sep + 'GarminDevice.xml', handler)
                    deviceName = handler.description
                    paths[deviceName] = '/media' + os.path.sep + path
                    
    return paths

def revCmp(x,y):
    v = cmp(x,y)
    if v == 0:
        return v
    if v < 0:
        return 1
    if v > 0:
        return -1


class ActivityInfo(Object):
    def __init__(self):
        self.start_time = None
        self.duration = 0
        self.distance = 0

def getActivityInfo():
    
    # start time, duration (time), distance, 
    
    return

def doMain():
    options = handleArgs()

    # Find garmin device

    devices = findGarminDevices()
    device = None
    if len(devices) > 1:
        #TODO Choose devices
        print 'Need to choose devices!'
    elif len(devices) == 1:
        device = devices.keys()[0]

    if device:
        path = devices[device]
        print 'Searching for files on <' + device + '> in <' + path + '>'

        # Find data files
        historyPath = path + os.path.sep + 'Garmin' + os.path.sep + 'History'
        
        l = os.listdir(historyPath)
        l.sort(revCmp)

        # Get already uploaded activity information
        activities = getActivityInfo()


        for filename in l:
            if filename[len(filename)-4:] == '.tcx':
                # check if its been uploaded already?

                # if not upload!
            
        
        # login
        username = options.user
        password = options.password

        # upload

    
if __name__ == "__main__":
    doMain()
