#!/usr/bin/python

#import eeml
import datetime
import time
#a=datetime.tzinfo()
import httplib
import os
import subprocess
import RPi.GPIO as GPIO



import math

# parameters
fID=open('cosmfeedID.txt')
feed_url=fID.read().strip()
fID.close()
fKEY=open('cosmkey.txt')
feed_key=fKEY.read().rstrip()
fKEY.close()

print "Found feed ID  {:s}".format(feed_url)
print "Found feed key {:s}".format(feed_key)


def submitdata(feedno,key,data):
    
    conn = httplib.HTTPSConnection('api.cosm.com', timeout=10)
    feedpath='/v2/feeds/{:s}.csv'.format(str(feedno))
    print "updating feed: " + feedpath
    print "Key: " + key
    print "data: " + data
    
    
    conn.request('PUT',feedpath,data,{'X-ApiKey': key})
    conn.sock.settimeout(30)
    try:
        resp=conn.getresponse()
        resp.read()
    except (RuntimeError, TypeError, NameError):
        print "There was an error uploading {:s}\n".format(RuntimeError)
        
    conn.close()
    print resp.status

def builddatacsv(streamname,time,data):
    csvdata=[]
    for i in range(0,len(streamname)):
        csvdata += streamname[i] + ','
        csvdata += time[i] +','
        csvdata += str(data[i])+'\n'
    return ''.join(csvdata)
        

def cpuload(interval):
    cpu=os.times()
    #load=0
    loadcmd="mpstat 1 {:d} | tail -n1".format(interval)
    proc=subprocess.Popen(loadcmd, shell=True, stdout=subprocess.PIPE)
    loadout, err=proc.communicate()
    loadstr=loadout.split()
    load=(float(loadstr[2].strip('\%'))+float(loadstr[4].strip('\%')))/100
    #time.sleep(1)
    #print load/10
    return load


GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 17
SPIMISO = 10
SPIMOSI = 9
SPICS = 11

# set up the SPI interface pins
GPIO.setwarnings(False)        
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

import random

def meas_temp(senseID):
    temperature=0
    n=60
    for d in range(n):
        # 10 bit number in range 0-1023
        adcval=readadc(senseID, SPICLK, SPIMOSI, SPIMISO, SPICS)
        #print adcval
#adcval=232+random.randrange(50)
        temperature+=25.0+((3.3*(adcval/1023.0))-0.75)/(0.01) # 750mV at 25degC with 10mV/degC
        #print "{:2.2f} ".format(temperature/(float(d)+1.0))
        time.sleep(1)
    #print "Averaged {:2.2f}".format(temperature/float(n))
    return temperature/(float(n))



# feed parameters
testAPI_KEY = feed_key
testAPI_URL = 82576

#last_cpu=os.times()

#for j in range(48):
while True:
    # once an hour update the stream
    streamname=[]
    thetime=[]
    data=[]

    streamhome=[]
    timehome=[]
    datahome=[]
    for i in range(30):
        # Measure the cpu usage over the last minute
        #time.sleep(2)
        streamname.append('cpu')
        thetime.append(str(datetime.datetime.utcnow()))
        cpul=cpuload(2)
        data.append(cpul*100.0) # convert to a percent
        #print "{:s}  {:e}".format(thetime[i],data[i])
        
        streamhome.append('tempinside')
        timehome.append(str(datetime.datetime.utcnow()))
        tempintern=meas_temp(1)
        print "{:s}  Temp Internal {:2.2f}   CPU Load {:2.1f}".format(thetime[i],tempintern,data[i])
        
        datahome.append("{:2.3f}".format(tempintern))
        
        #print "{:s}  {:s} degC".format(timehome[i],datahome[i])

        
    homedatastring=builddatacsv(streamhome,timehome,datahome)
    testdatastring=builddatacsv(streamname,thetime,data)
        #print testdatastring
#    print testAPI_URL
#    print testAPI_KEY
#    print feed_url
#    print feed_key
    print "submitting temps"
    submitdata(testAPI_URL,testAPI_KEY,testdatastring)
    submitdata(feed_url,feed_key,homedatastring)
    
    fLOG=open('datalog.txt','a')
    fLOG.write(homedatastring)
    fLOG.close()


