#!/bin/bash
# This script was never finished! Started it to learn some shell scripting, but 
# then chose to continue the actual development in Python


ROOT_URL="http://connect.garmin.com/"
SIGN_IN_URL="https://connect.garmin.com/signin"

if [ -z $1 ]
then
       echo "The first parameter needs to be your Garmin Connect username"
       exit 1
fi

USERNAME=$1

read -s -p "Garmin Connect Password: " PASSWORD
echo

if [ -z $PASSWORD ]
then
       echo "Failed! You didn't enter your password!"
       exit 2
fi

if [ -z $PROXYURL ]
then
    read -s -p "Proxy URL (enter for none): " PROXYURL
    echo
fi

if [ -n $PROXYURL ] 
then
    if [ -z $PROXYUSER ]
    then
        read -s -p "Proxy username: " PROXYUSER
	    echo
    fi

    if [ -n  $PROXYUSER ]
    then
    	read -s -p "Proxy password: " PROXYPASS
    	echo
    fi
fi

PROXYDEETS=""

if [ -n "$PROXYURL" ]
then
	PROXYDEETS="-e http_proxy=$PROXYURL -e https_proxy=$PROXYURL "
fi
if [ -n "$PROXYUSER" ]
then
    PROXYDEETS="$PROXYDEETS --proxy-user=$PROXYUSER --proxy-password=$PROXYPASS"
fi

echo "LETS GET SOME DATA!"

if [ -a "activities_page" ]
then
    rm activities_page
fi

#LOGIN
wget -q --output-document=/dev/null --save-cookies cookies.txt --keep-session-cookies $PROXYDEETS http://connect.garmin.com/signin

LOGINDATA="login=login&login%3AloginUsernameField=$USERNAME&login%3Apassword=$PASSWORD&login%3AsignInButton=Sign+In&javax.faces.ViewState=j_id1"

wget -q --output-document=/dev/null --load-cookies cookies.txt --save-cookies cookies.txt --keep-session-cookies $PROXYDEETS --post-data $LOGINDATA https://connect.garmin.com/signin

wget -q --output-document=/dev/null --load-cookies cookies.txt $PROXYDEETS http://connect.garmin.com/user/username

#Get activities page
wget -q --output-document=/dev/null --load-cookies cookies.txt --save-cookies cookies.txt --keep-session-cookies $PROXYDEETS http://connect.garmin.com/activities

MOREDATA=0
PAGENUM=1
while [ $MOREDATA -eq  0 ]
do
    PAGEDATA="AJAXREQUEST=_viewRoot&activitiesForm=activitiesForm&activitiesForm%3AactivitiesGrid%3AAs=-1&javax.faces.ViewState=j_id2&ajaxSingle=activitiesForm%3ApageScroller&activitiesForm%3ApageScroller=$PAGENUM&AJAX%3AEVENTS_COUNT=1"
    #PAGEFILE="activities_page$PAGENUM"
    PAGEFILE="activities_page"
    echo "Getting page $PAGENUM"
    wget -q --output-document=$PAGEFILE --load-cookies cookies.txt --save-cookies cookies.txt --keep-session-cookies $PROXYDEETS --post-data $PAGEDATA http://connect.garmin.com/activities

    # Check if we are on the last page!
    grep "counterContainer" $PAGEFILE > tmp.txt
    THISPAGE=`awk '{print substr($6,4,index($6,"</")-4)}' tmp.txt`
    LASTPAGE=`awk '{print substr($8,4,index($8,"</")-4)}' tmp.txt`
    rm tmp.txt

    # search for /activity/xxxxxxxxx and store xxxxxxxx in a list for later retrieval
    grep "/activity/" $PAGEFILE > tmp.txt
    ACTCHUNK=`grep "/activty/" $PAGEFILE`

    # TODO LOOP THIS!

    INDX=`awk '{print (index($0, "/activity/")+10)}' tmp.txt`
    ENDX=`awk '{print index(substr($0,'$INDX'),"\"")}' tmp.txt`

    ACT1=`awk '{print substr($0, '$INDX', '$ENDX'-1)}' tmp.txt`

    # TODO Add to a list!
    echo First Activity is $ACT1

    # TODO END LOOP!

    #rm tmp.txt

    PAGENUM=`expr $PAGENUM + 1`
    if [ $PAGENUM -eq 2 ]
#    if [ $THISPAGE -eq $LASTPAGE ]
    then
        MOREDATA=1
    fi

done

echo "List Retrieved"
echo "Fetching TCX Files"
#connect.garmin.com/proxy/activity-service-1.0/tcx/activity/EVENT_ID?full=true

#if [ -a "activities_page" ]
#then
#    rm activities_page
#fi

