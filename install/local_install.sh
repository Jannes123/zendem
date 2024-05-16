#! /usr/bin/env bash
#-*- coding: utf-8 -*-
# sudo apt install python3-pip python3-dev
# sudo apt install libpq-dev postgresql postgresql-contrib

# add django app path permanently to venv
# sudo -u postgres psql
# could not change directory to "/home/edna": Permission denied
# psql (14.9 (Ubuntu 14.9-0ubuntu0.22.04.1), server 13.7 (Ubuntu 13.7-0ubuntu0.21.10.1))
# Type "help" for help.
#
#postgres=# CREATE DATABASE shredder;
#CREATE DATABASE
#postgres=# CREATE USER meatshredder WITH PASSWORD 'aofhti1gn6rfb5e';
#CREATE ROLE
#postgres=# ALTER ROLE meatshredder SET client_encoding TO 'utf8';
#ALTER ROLE
#postgres=# ALTER ROLE meatshredder SET default_transaction_isolation TO 'read committed';
#postgres=# ALTER ROLE meatshredder SET timezone TO 'UTC+1';
#ALTER ROLE
#postgres=# GRANT ALL PRIVILEGES ON DATABASE shredder TO meatshredder;
#GRANT
# ALTER DATABASE shredder OWNER TO meatshredder;
#postgres=# \q
#sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib

echo "Install script"
echo "\n"
##
# BASH menu script that checks:
#   - Memory usage
#   - CPU load
#   - Number of TCP connections
#   - Kernel version
#
server_name=$(hostname)

function memory_check() {
    echo ""
	echo "Memory usage on ${server_name} is: "
	free -h
	echo ""
}

function cpu_check() {
    echo ""
	echo "CPU load on ${server_name} is: "
    echo ""
	uptime
    echo ""
}

function tcp_check() {
    echo ""
	echo "TCP connections on ${server_name}: "
    echo ""
	cat  /proc/net/tcp | wc -l
    echo ""
}

function kernel_check() {
    echo ""
	echo "Kernel version on ${server_name} is: "
	echo ""
	uname -r
    echo ""
}

function all_checks() {
	memory_check
	cpu_check
	tcp_check
	kernel_check
}
echo "Press Y to migrate without changing anything else. Press n to skip"
read choicex
if [[ "${choicex}" == "Y" ]];
  then
  python3 ../sendemdj/manage.py makemigrations
  python3 ../sendemdj/manage.py makemigrations sendemauth
  python3 ../sendemdj/manage.py migrate
  python3 ../sendemdj/manage.py migrate sendemauth
fi

echo "Press Y to do system checks.  Press n to skip."
read choicey
if [[ "${choicey}" == "Y" ]];
  then
  all_checks
fi

echo "end"
exit 0;