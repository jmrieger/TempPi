#!/bin/bash

# Perform basic updates on the RPI
echo -n "Would you like to run apt-get update and apt-get upgrade? (Recommended: Y) [Y/n]:"
read update
if [ ${update,,} == 'y' ]; then
	sudo apt-get update
	sudo apt-get upgrade
fi

# Install our standard dev tools
sudo apt-get -y install sqlite3 

# Install the dweet.io interface, dotenv interface
pip install -U dweepy tweepy python-dotenv

# Copy our .env vile
echo -n "Would you like to import the default .env file? [Y/n]:"
read defaultEnv

if [ ${defaultEnv,,} == 'y' ]; then
	mv .envexample .env
fi

# Initialize our SQLite3 database
echo -n "Would you like to import a default database? (Please only choose 'No' if you are updating TempPi.) [Y/n]:"
read database
if [ ${database,,} == 'y' ]; then
	sqlite3 temppi.db < install-db.sql
fi

# Install our daemon - determine if we're on upstart or systemd.  If other, fail, and suggest contribution to the Git project
initSystem=$(stat /proc/1/exe)
toInstallSystem=""
if echo ${initSystem,,} | grep -q "systemd"; then
	echo -n "Raspberry Pi default init system, systemd, detected. Do you want to install the TempPi startup service for systemd? (Y recommended, any non-'n' answer treated as 'Y') [Y/n]:"
	read in0
	if [ "${in0,,}" != "n" ]; then
		echo "Installing systemd"
		toInstallSystem="systemd"
	fi
	
elif echo ${initSystem,,} | grep -q ""; then
	echo -n "Startup init system detected. Do you want to install the TempPi startup service for upstart? (Y recommended, any non-'n' answer treated as 'Y') [Y/n]:"
	read in0
	if [ "${in0,,}" != "n" ]; then
		toInstallSystem="upstart"
	fi
else
	echo "Non-standard Raspberry Pi init system detected.  Manual installation of the TempPi service will be required."
fi

if [ "$toInstallSystem" == "systemd" ]; then
	echo "Creating systemd startup service..."
	mycwd=$(pwd)
	cat temppi.systemd.inst | sed -e"s#{homeDir}#${mycwd}#g" > /lib/systemd/system/temppi.service
	systemctl enable temppi.service
	systemctl start temppi.service
	echo "Done!"
elif [ "$toInstallSystem" == "upstart"]; then
	echo "Creating upstart service..."
	mycwd=$(pwd)
	cat temppi.upstart.inst | sed -e"s#{homeDir}#${mycwd}#g" > /etc/init/temppi.conf
	echo "Done!"
fi

echo -n "Would you like to clean up installation files? 'Y' to remove files, 'H' to hide the files, and 'N' to keep the files as they exist (N is default) [Y/h/N]:"
read cleanup
if [ ${cleanup,,} == "y" ]; then
	rm install.bash
	rm install-db.sql
	rm temppi.upstart.inst
	rm temppi.systemd.init
	rm install.bash
elif [ ${cleanup,,} == "h" ]; then
	mv install.bash .install.bash
	mv install-db.sql .install-db.sql
	mv temppi.upstart.inst .temppi.upstart.inst
	mv temppi.systemd.inst .temppi.systemd.inst
	mv install.bash .install.bash
fi

# We'll need to reboot the Pi after install, since upstart requires it...
if [ "$toInstallSystem" == "upstart" ]; then
	sudo shutdown -r now
fi

echo "Done installing! Be sure to update your .env file, and have fun!"
