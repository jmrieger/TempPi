#!/bin/bash

# Perform basic updates on the RPI
sudo apt-get update
sudo apt-get upgrade

# Install our standard dev tools
sudo apt-get -y install sqlite3 upstart

# Install the dweet.io interface, dotenv interface
pip install -U dweepy python-dotenv

# Copy our .env vile
mv .envexample .env

# Initialize our SQLite3 database
sqlite3 temppi.db
sqlite3 temppi.db < install-db.sql

# Install our daemon
sudo mv temppi.conf /etc/init

# We'll need to reboot the Pi after install, since upstart requires it...
sudo shutdown -r now
