from __future__ import print_function

import os 
import sys
import glob 
import time
import dweepy
import datetime
import sqlite3
import RPi.GPIO as GPIO

from dotenv import load_dotenv, find_dotenv, get_key

 
os.system('modprobe w1-gpio') 
os.system('modprobe w1-therm')
 
#base_dir = '/sys/bus/w1/devices/'
base_dir = get_key( find_dotenv(), 'PROBE-BASEDIR' ).lower()
GPIO.setmode(GPIO.BCM)
GPIO.setup(7,GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_temp = {}
conn = None
curs = None

try:
    conn=sqlite3.connect('/home/pi/TempPi/temppi.db')
    curs = conn.cursor()
except:
    print ("No Database")

 
def read_temp_raw(device_file):
    f = open(device_file, 'r') 
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(device_file):
    lines = read_temp_raw( device_file )
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.1)
        lines = read_temp_raw( device_file ) 
    equals_pos = lines[1].find('t=') 
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:] 
        temp_c = float(temp_string) / 1000.0
        return temp_c
 
while True: 
	load_dotenv(find_dotenv())

	active = get_key( find_dotenv(), 'ACTIVE' ).lower()

	if active == 'true':
		probes = get_key( find_dotenv(), 'PROBE-DEVICES' )
		probes = probes.split('|')

		dweet_packet = {}
		probecnt = -1
		for probe in probes:
			probecnt += 1

			probe = str(probe)
			probe = probe.split(",")
			dev_folder = probe[0]
			dev_file = probe[1]
			batch = probe[2]
			active = probe[3].lower()
			broadcast = probe[4].lower()
			alwayswrite = probe[5].lower()
			correction = probe[6]
			try:
				dev_folder = glob.glob(base_dir + dev_folder)[0]
			except:
				print ("Device " + batch + " not readable : " + base_dir + " " + dev_folder)
				continue

			dev_file = dev_folder + dev_file

			temp_c = read_temp( dev_file )
			try:
				temp_c = temp_c + float(correction) or int(0)
			except:
				temp_c += 0
	
			temp_f = temp_c * 9.0 / 5.0 + 32.0

			print ("Dev: " + str(dev_file), end="" )
			print (" Nickname: " + str(batch), end="" )
			print (" Temp: " + str(temp_c), end="" )
			print (" Batch: " + str(batch), end="" )

			if curs and active == 'true' and ( last_temp.setdefault( batch, '') != '{:0.4f}'.format(temp_c) or  alwayswrite== 'true' ) :
				try: 
					curs.execute("INSERT INTO temppi (batchname, tempc, tempf, tstamp) VALUES(?, ?, ?, ?);", (batch, temp_c, temp_f, datetime.datetime.now() ) )
					conn.commit()
					last_temp[batch] = '{:0.4f}'.format(temp_c)
					print (" Logged temp in DB", end="")
				except sqlite3.Error as er:
					print (" Couldn't log temp into database: " + er.message, end="")
			if broadcast == 'true':
				dweet_packet[probecnt] = {'temp_f':temp_f, 'temp_c':temp_c, 'localtime':datetime.datetime.now().isoformat(), 'batch-id' : batch }	

			print ("")



	# End of active if statement

	if len(dweet_packet.keys()):
		try:
			dweepy.dweet_for( 'dymium-ferment-pi', dweet_packet )	
			print (" Dweeted", end="")
		except:
			print (" Couldn't log temp to dweetly",sys.exc_info()[0], end="")

	print ("")
	freq = get_key( find_dotenv(), 'POLL-FREQ' )
	freq = int(freq) or int(15)

	time.sleep(freq)
