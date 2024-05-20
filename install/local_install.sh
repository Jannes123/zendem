#! /usr/bin/env bash
#-*- coding: utf-8 -*-

## Setup environment variables according to the machine hostng the app.
## check current env vars cat /etc/environment
## JENV=jdev or JENV=jprod or JENV=jtesting

x=0
package_names=("libpq-dev" "postgresql" "postgresql-contrib" "python3-pip" "python3-dev")
while [[ $x -lt ${#package_names[@]} ]]
do
dpkg -s ${package_names[x]} | grep -E 'Status|Package' | tee grep "installed"
((x++))
done;

db_name="testshredder_dev"
psql_user_name="test_user_django_shredder"

if [ $JENV == "jprod" ]; then
	db_name="dbmeatshredder";
	psql_user_name="meatdjangouser";
fi

echo "Database name:"
echo $db_name
echo "Database USER-name"
echo $pqsl_user_name

function chatshredder_psql_setup(){
  # opening a connection remotely
  # psql -U doadmin -h production-sfo-test1-do-user-4866002-0.db.ondigitalocean.com -p 25060 -d defaultdb
  sudo -u postgres psql -c "\l"
  sudo -u postgres psql -c "create database $db_name"
  sudo -u postgres psql -c "CREATE USER $psql_user_name  WITH PASSWORD 'aofhti1gn6rfb5e'"
  sudo -u postgres psql -c "ALTER ROLE $psql_user_name SET client_encoding TO 'utf8'"
  sudo -u postgres psql -c "ALTER ROLE $psql_user_name SET default_transaction_isolation TO 'read committed'"
  sudo -u postgres psql -c "ALTER ROLE $psql_user_name SET timezone TO 'UTC+1'"
  sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $psql_user_name"
  sudo -u postgres psql -c "ALTER DATABASE $db_name OWNER TO $psql_user_name"
}
# add django app path permanently to venv
# sudo -u postgres psql

function venv_pip_setup(){
  python3  -m venv core
  source core/bin/activate
  pip install -r install/requirements.txt
  echo "venv core install script finished"
  echo "\n"
}

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

echo "Press Y to do psql setup.  Press n to skip."
read choicey
if [[ "${choicey}" == "Y" ]];
  then
  chatshredder_psql_setup
fi

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

echo "Press Y to setup pip venv requirements. Press n to skip"
read choicex
if [[ "${choicex}" == "Y" ]];
  then
  venv_pip_setup
fi


echo "end"
exit 0;
}
