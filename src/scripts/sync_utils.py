'''
Created 30/09/2011
@author g3rg


sync_utils.py listusers
    list the users in the database
sync_utils.py adduser name
    add user 'name' to the database
sync_utils.py addwebaccount username type username password
    adds details of a web account to the user
sync_utils.py listwebaccounts username
    list the types of accounts linked to the given username
? sync_utils.py fetchsummary username account_type
    log into account_type and fetch history into summary table
? sync_utils.py listpendinguploads username account_type
    compare history files on garmin device with items in summary table and list those files that need to be uploaded

'''

import argparse
import sqlite3

DB_FILE = './sync.db'

def handleArgs():
    p = argparse.ArgumentParser(prog='gcBkup',description="Utility for interacting with Garmin Connect")

    p.add_argument('--debug', '-d', action="store_true", help="If set, will store cookies and fetched pages in text files")
    p.add_argument('--version', action="version", version='%(prog)s 0.1')
    p.add_argument('--verbose', action="store_true", help="Print out more messages during processing")
    p.add_argument('commands', nargs='+', default='listusers', help="Commands")
    
    args = p.parse_args()
    
    if args.debug:
        global DEBUG
        DEBUG = True
        createDebugFile(args)
    
    return args

def initDB():   
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS User (id INTEGER PRIMARY KEY, Username TEXT)')
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS WebAccount 
        (id INTEGER PRIMARY KEY, user_id INTEGER, account_type TEXT, account_username TEXT, 
        account_password TEXT)''')

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS History
        (id INTEGER PRIMARY KEY, user_id INTEGER, type TEXT, start_time TEXT, duration TEXT, distance TEXT, remote_id TEXT, file_name TEXT)
        ''')

    conn.commit()
    cursor.close()

def listUsers():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, Username FROM User ORDER BY Username')
    allusers = cursor.fetchall()
    print 'Users:'
    for user in allusers:
        print str(user[0]) + ' - ' + user[1]
    cursor.close()
    conn.close()

def addUser(arguments):
    username = arguments[1]

    print 'adding user: ' + arguments[1]

    if getUserId(username):
        print 'user already exists'
    else:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM User WHERE Username = ?', (arguments[1],))
        users = cursor.fetchall()
        if len(users) > 0:
            print 'user already exists'
        else:
            cursor.execute('INSERT INTO User VALUES(null, ?)', (arguments[1],))
            conn.commit()

        cursor.close()
        conn.close()

def getUserId(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM User WHERE Username = ?', (username,))
    users = cursor.fetchall()
    if len(users) == 1:
        user_id = users[0][0]
    else:
        user_id = None
    cursor.close()
    conn.close()

    return user_id

def addWebAccount(arguments):
    if len(arguments) < 5:
        print 'Not enough arguments for addwebaccount command: sync_username account_type account_username account_password'
    else:
        username = arguments[1]
        account_type = arguments[2]
        acc_username = arguments[3]
        acc_password = arguments[4]

        if account_type != 'garmin_connect' or account_type != 'test':
            print 'Account type <' + account_type + '> not supported'
            return

        user_id = getUserId(username)
        print user_id
        if user_id != None:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO WebAccount VALUES (NULL, ?, ?, ?, ?)',
                    (user_id, account_type, acc_username, acc_password))
            conn.commit()
            cursor.close()
            conn.close()
        else:
            print 'User <' + username + '> not found!'

def getQueryResults(sql, params):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()

    detached_results = []
    for row in results:
        detached_row = []
        for field in row:
            detached_row.append(field)
        detached_results.append(detached_row)

    cursor.close()
    conn.close()

    return detached_results

def execSql(sql, params):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close

def listWebAccounts(arguments):
    if len(arguments) < 2:
        print 'You didn''t provide a username'
        return

    user_id = getUserId(arguments[1])
    if user_id:
        results = getQueryResults('SELECT account_type FROM WebAccount WHERE user_id = ?', (user_id,))
        for row in results:
            print row[0]
    else:
        print 'User <' + arguments[1] + '> not found'

def getWebAccountDetails(user_id, account_type):
    return getQueryResults('SELECT id, account_type, account_username, account_password FROM WebAccount WHERE user_id = ? AND account_type = ?',
            (user_id, account_type))

def fetchSummaries(arguments):
    if len(arguments) < 3:
        print 'Not enough arguments for fetchsummary: username account_type'
        return
    user_id = getUserId(arguments[1])
    if user_id:
        account_type = arguments[2]
        account_details = getWebAccountDetails(user_id, account_type)
        if account_details:
            account_details = account_details[0]
            if account_details[1] == 'garmin_connect':
                pass
            else:
                print 'Account type <' + account_details[1] + '> not supported for summary fetching'
        else:
            print 'No account of type <' + account_type + '> found for user <' + arguments[1] + '>'
    else:
        print 'User <' + arguments[1] + '> not found'

def delWebAccount(arguments):
    if len(arguments) < 3:
        print 'Not enough arguments for delwebaccount: username account_type'
        return

    user_id = getUserId(arguments[1])
    if user_id:
        account_type = arguments[2]
        account_details = getWebAccountDetails(user_id, account_type)
        if account_details:
            account_details = account_details[0]
            id = account_details[0]
            execSql('DELETE FROM WebAccount WHERE user_id = ? AND id = ?', (user_id, account_details[0]))
            print 'Account <' + account_type + '> deleted for user <' + arguments[1] + '>'
        else:
            print 'No account of type <' + account_type + '> found for user <' + arguments[1] + '>'

    else:
        print 'User <' + arguments[1] + '> not found'

def doMain():
    options = handleArgs()

    initDB()

    if options.commands[0] == 'listusers':
        listUsers()
    elif options.commands[0] == 'adduser':
        addUser(options.commands)
    elif options.commands[0] == 'addwebaccount':
        addWebAccount(options.commands)
    elif options.commands[0] == 'delwebaccount':
        delWebAccount(options.commands)
    elif options.commands[0] == 'listwebaccounts':
        listWebAccounts(options.commands)
    elif options.commands[0] == 'fetchsummary':
        fetchSummaries(options.commands)
    else:
        print 'Unknown command: ' + options.commands[0]

if __name__ == '__main__':
    doMain()

