#! /usr/bin/env bash
#-*- coding: utf-8 -*-

for x in 1 2 3 4 5 6 7 8 9;
do
	echo "(($x*4))"
	echo
done


#
#echo "what is your name?"
#read name
#
#echo "what is your age?"
#read age
#
#echo " $name you are $age years old!"
#
#echo "\n"
#
##in console:
##twitter="Elon"
##export twitter
## now
#
#echo $twitter
#
#if [$age > 10]; then
#	echo "you are old"
#else
#	echo "you are young"
#
#fi;
#echo "end"


#curl -c cooker.txt -i -v -X GET -H 'Accept: application/json' 'http://127.0.0.1:8000/sendem-rest-auth/api-general/login/'
#cat cooker.txt
#now do script thats scrapin csrfmiddlewaretokewn from http form not csrf from headers because rest framework uses the iron.


#cat cooker.txt
#curl -b cooker.txt -i -v -X POST -d username=greenpen\@gmail.com\&password=bubble456 -H 'Accept: application/json' 'http://127.0.0.1:8000/sendem-rest-auth/api-general/login/'
#CSRF EXemot login?? 
hostname="127.0.0.1:8000"
username="tester@gmail.com"
password="jannes123"
firstname="joe"
lastname="grass"
# do get on login url to get csrf middleware token.  this is for standard rest
# which does not facilitate login without website use.boring!!!!.
curl -X GET -H 'Accept: application/json' -H 'Content-Type: application/json' \
-H "Authorization: Bearer 5O0fexNESf79SlpddGYbigELu5Yvo5N0zE7qqWXnjHeq7CpA6UKVbRKJAd5g0k65" \
--data '{\"username\":\"{$username}\",\"password\":\"{$password}\"}' \
"http://{$hostname}/sendem-rest-auth/api-general/login/" | grep 'csrfmiddlewaretoken*'
# try to login
curl -i -v -b cooker.txt -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
-H "Authorization: Bearer 5O0fexNESf79SlpddGYbigELu5Yvo5N0zE7qqWXnjHeq7CpA6UKVbRKJAd5g0k65" \
--data '{\"username\":\"{$username}\",\"password\":\"{$password}\",\"csrfmiddlewaretoken\":\"dU6NN0yCUcNyJkuRrmJgE0RUDpNHty7h5ziGinRh5m9UAMvzo3GWUeb92edYC0La\"}' \
"http://{$hostname}/sendem-rest-auth/api-general/login/"

TOKEN=$(curl -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
-H "Authorization: Bearer C4GQWCGPxD7FFEr5TEf3ySBQbO4i8qme3xwZNb0W8iDROa9ocHxgHTbGnzyTz21v" \
--data '{\"username\":\"{$username}\",\"password\":\"{$password}\"}' \
"http://{$hostname}/sendem-rest-auth/api-general/login/" | grep 'csrfmiddlewaretoken*')
echo "$TOKEN"
