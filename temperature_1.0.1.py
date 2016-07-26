import os 
import glob 
import time
import dweepy
import datetime
import sqlite3
from dotenv inport load_dotenv, find_dotenv

load_dotenv(find_dotenv())
 
os.system('modprobe w1-gpio') 
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0] 
device_file = device_folder + '/w1_slave'

conn = None
curs = None
try:
    conn=sqlite3.connect('temppi.db')
    curs = conn.cursor()
except error:
    print "No Database\n"

 
def read_temp_raw():
    f = open(device_file, 'r') 
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw() 
    equals_pos = lines[1].find('t=') 
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:] 
        temp_c = float(temp_string) / 1000.0
        return temp_c
 
while True: 
    temp_c = read_temp()
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    print ("Temp: " + str(temp_f) )
    if curs:
	try: 
	        curs.execute("""INSERT INTO temppi (batch-name, temp-c, temp-f) VALUES((?), (?), (?) )""", (dotenv.get_key('BATCH-id'), temp_c, temp_f ) )
	except error:
		print "Couldn't log temp into database\n"
    
    try:		
	dweepy.dweet_for('dymium-ferment-pi', {'temp_f':temp_f, 'temp_c':temp_c, 'localtime':datetime.datetime.now().isoformat() })	
	print "Dweeted"
    except error:
	print "Couldn't log temp to dweetly\n"

    time.sleep(10)
