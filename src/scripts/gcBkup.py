'''
Created 30/09/2011
@author g3rg
'''

import urllib

def doMain():
    fHandle = urllib.urlretrieve("http://www.google.com", "tmp.txt")
    
    print "Done!"

if __name__ == "__main__":
    doMain()
