#!/bin/bash

ROOT_URL="http://connect.garmin.com/"

read -s -p "Proxy URL (enter for none): " PROXYURL
echo
if [ -n $PROXYURL ] 
then
	read -s -p "Proxy username: " PROXYUSER
	echo
	read -s -p "Proxy password: " PROXYPASS
	echo

	PROXYDEETS="-e http_proxy=$PROXYURL -e https_proxy=$PROXYURL --proxy-user=$PROXYUSER --proxy-password=$PROXYPASS"
else
	PROXYDEETS=""
fi

wget --save-cookies cookies.txt --keep-session-cookies $PROXYDEETS https://connect.garmin.com/signin
