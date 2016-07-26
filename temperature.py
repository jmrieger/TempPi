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
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0] 
device_file = device_folder + '/w1_slave'
GPIO.setmode(GPIO.BCM)
GPIO.setup(7,GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_temp = ''
conn = None
curs = None

try:
    conn=sqlite3.connect('/home/pi/TempPi/temppi.db')
    curs = conn.cursor()
except:
    print "No Database\n"

 
def read_temp_raw(device_file):
    f = open(device_file, 'r') 
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(device_file):
    lines = read_temp_raw( device_file )
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
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
		batch = get_key( find_dotenv(), 'BATCH-ID' )

		probes = get_key( find_dotenv(), 'PROBE-DEVICES' )
		probes = probes.split('|')
		print probes
		for probe in probes:
			probe = str(probe)
			dev_folder = probe.split(",")[0]
			dev_file = probe.split(",")[1]
			dev_folder = glob.glob(base_dir + dev_folder)[0]
			dev_file = dev_folder + dev_file

			temp_c = read_temp( dev_file )
			temp_f = temp_c * 9.0 / 5.0 + 32.0

			print ("Dev: " + str(dev_file) )
			print ("Temp: " + str(temp_f) )
			print ("Batch: " + str(batch) )

			if curs and ( last_temp != '{:0.4f}'.format(temp_c) or get_key( find_dotenv(), 'ALWAYS-WRITE').lower() == 'true' ) :
				try: 
					curs.execute("INSERT INTO temppi (batchname, tempc, tempf, tstamp) VALUES(?, ?, ?, ?);", (batch, temp_c, temp_f, datetime.datetime.now() ) )
					conn.commit()
					last_temp = '{:0.4f}'.format(temp_c)
					print "Logged temp in DB"
				except sqlite3.Error as er:
					print "Couldn't log temp into database: " + er.message + "\n"

			try:		
				dweepy.dweet_for('dymium-ferment-pi', {'temp_f':temp_f, 'temp_c':temp_c, 'localtime':datetime.datetime.now().isoformat(), 'batch-id' : batch })	
				print "Dweeted"
			except:
				print ("Couldn't log temp to dweetly",sys.exc_info()[0])
				print "\n"



	# End of active if statement

	freq = get_key( find_dotenv(), 'POLL-FREQ' )
	freq = int(freq) or 15
	freq = int(freq)

	time.sleep(freq)
