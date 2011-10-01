'''
Created 30/09/2011
@author g3rg
'''

import urllib2
import cookielib

import optparse

ROOT_URL = "http://connect.garmin.com/"
SIGN_IN_URL_1="http://connect.garmin.com/signin"
SIGN_IN_URL_2 = "https://connect.garmin.com/signin"

DEBUG = False

cookieJar = None

def debugWrite(str, filename):
    if DEBUG:
        output = open(filename, "w")
        output.write(str)
        output.close()

def debugFetch(handle, filename):
    if DEBUG:
        pgContents = handle.read()
        debugWrite(pgContents, filename)
        
def initCookieJar():
    global cookieJar
    cookieJar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    urllib2.install_opener(opener)
        
def login(username, password):    
        
    headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    req = urllib2.Request(SIGN_IN_URL_1, None, headers)
    pgFile = urllib2.urlopen(req)
    debugFetch(pgFile, "signin1.html")

    reqData = "login=login&login%3AloginUsernameField=" + username +"&login%3Apassword=" + password + "&login%3AsignInButton=Sign+In&javax.faces.ViewState=j_id1"
    req = urllib2.Request("https://connect.garmin.com/signin", reqData, headers)
    pgFile = urllib2.urlopen(req)
    debugFetch(pgFile, "signin2.html")
    
    req = urllib2.Request("http://connect.garmin.com/user/username", headers=headers)
    pgFile = urllib2.urlopen(req)
    pgContents = pgFile.read()
    debugWrite(pgContents, "username.txt")
    
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

def getActivityList():
    #Get activities page
    print "http://connect.garmin.com/activities"

    
    
def handleArgs():
    p = optparse.OptionParser()
    p.add_option("--user", "-u", default="dummy")
    p.add_option("--password", "-p", default="dummy")
    p.add_option("--command", "-c", default="activity")
    p.add_option("--debug", default="false")
    options, arguments = p.parse_args()
    
    if options.debug == "true":
        global DEBUG
        DEBUG = True
    
    return options

def doMain():
    options = handleArgs()
    
    username = options.user
    password = options.password
    
    initCookieJar()
    
    if login(username, password):
        print "Logged in"
        
        if options.command == "activity":
            getActivityList()
        else:
            print "Command <" + options.command + "> is not understood, try --help to see help"
    else:
        print "Failed to login with the username and password supplied"

if __name__ == "__main__":
    doMain()
