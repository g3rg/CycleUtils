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

COOKIEFILE = "./cookies.txt"
DEBUG = False

def debugWrite(str, filename):
    if DEBUG:
        output = open(filename, "w")
        output.write(str)
        output.close()

def debugFetch(handle, filename):
    if DEBUG:
        pgContents = handle.read()
        debugWrite(pgContents, filename)
        
def login(username, password):    
    cookieJar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    urllib2.install_opener(opener)
        
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
        print username_returned
    except:
        username_returned = ""    
   
    if DEBUG:
        cookieJar.save("cookies.txt", ignore_discard=True)
    
    return username == username_returned

def handleArgs():
    p = optparse.OptionParser()
    p.add_option("--user", "-u", default="dummy")
    p.add_option("--password", "-p", default="dummy")
    options, arguments = p.parse_args()
    return options

def doMain():
    options = handleArgs()
    
    username = options.user
    password = options.password
    
    if login(username, password):
        print "Logged in"
    else:
        print "Failed to login with username and password supplied"
    
    print "Done!"

if __name__ == "__main__":
    doMain()
