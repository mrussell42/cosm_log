#!/usr/bin/python

#import eeml
import datetime
import time
#a=datetime.tzinfo()
import httplib
import os
import subprocess
import RPi.GPIO as GPIO
from sys import argv


import math

if len(argv)>1:
    avelen=int(argv[1])
else:
    avelen=5*60

if len(argv)>2:
    adcmode=int(argv[2])
else:
    adcmode=0

        



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
    try:
    
        conn = httplib.HTTPSConnection('api.cosm.com', timeout=10)
        feedpath='/v2/feeds/{:s}.csv'.format(str(feedno))
        print "updating feed: " + feedpath
        print "Key: " + key
        print "data: " + data
    
    
        conn.request('PUT',feedpath,data,{'X-ApiKey': key})
        conn.sock.settimeout(30)
        resp=conn.getresponse()
        resp.read()
        conn.close()
        print resp.status
    except :
        print "There was an error uploading\n"
        

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
        for i in range(14):
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

def meas_temp(senseID,sense_type):
    # 12 bit number in range 0-4095
    adcval=readadc(senseID, SPICLK, SPIMOSI, SPIMISO, SPICS)
    #print adcval
    if sense_type==36:
        temperature=25.0+((3.3*(adcval/4095.0))-0.75)/(0.01) # 750mV at 25degC with 10mV/degC
    else:
        temperature=25.0+((3.3*(adcval/4095.0))-0.5)/(0.02) # 500mV at 25degC with 20mV/degC
    return temperature



# feed parameters
testAPI_KEY = feed_key
testAPI_URL = 82576

#last_cpu=os.times()

#for j in range(48):

while adcmode:
    if adcmode>0:
        adcval=readadc(adcmode-1, SPICLK, SPIMOSI, SPIMISO, SPICS)
        time.sleep(0.1)
        print "adcmode on channel {:d} : {:d}".format(adcmode,adcval)
    else:
        adcval=0
        for i in range(1000):
            adcval+=readadc(-adcmode-1, SPICLK, SPIMOSI, SPIMISO, SPICS)
        print str(datetime.datetime.utcnow())+ " " + str(adcval/1000.0)

while True:
    # once an hour update the stream
    streamname=[]
    thetime=[]
    data=[]

    streamhome=[]
    timehome=[]
    datahome=[]
    for i in range(3):
        # Measure the cpu usage over the last minute
        #time.sleep(2)
        cpusum=0
        tempint=0
        tempext=0
        for count in range(avelen):
              cpusum+=cpuload(1)
              tempint+=meas_temp(1,36)
              tempext+=meas_temp(2,36)
        streamname.append('cpu')
        thetime.append(str(datetime.datetime.utcnow()))
        data.append(cpusum*100.0/avelen) # convert to a percent

        streamhome.append('tempinside')
        timehome.append(str(datetime.datetime.utcnow()))
        datahome.append("{:2.3f}".format(tempint/avelen))

        streamhome.append('tempoutside')
        timehome.append(str(datetime.datetime.utcnow()))
        datahome.append("{:2.3f}".format(tempext/avelen))

        print "{:s}  Temp Internal {:2.2f}  Temp External {:2.2f}   CPU Load {:2.1f}".format(thetime[i],tempint/avelen,tempext/avelen,cpusum*100.0/avelen)
        

        
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


