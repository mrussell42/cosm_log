#!/usr/bin/python

import datetime
import time
import os
import subprocess
import sys
import math
import random
import pi_adc
import pi_cosm



if len(sys.argv)>1:
    avelen=int(sys.argv[1])
else:
    avelen=5*60

if len(sys.argv)>2:
    adcmode=int(sys.argv[2])
else:
    adcmode=0



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




def meas_temp(senseID,sense_type):
    # 12 bit number in range 0-4095
    adcval=pi_adc.readadc(senseID, SPICLK, SPIMOSI, SPIMISO, SPICS)
    #print adcval
    if sense_type==36:
        temperature=25.0+((3.3*(adcval/4095.0))-0.75)/(0.01) # 750mV at 25degC with 10mV/degC
    else:
        temperature=25.0+((3.3*(adcval/4095.0))-0.5)/(0.02) # 500mV at 25degC with 20mV/degC
    return temperature



# feed parameters
fID=open('cosmfeedID.txt')
home_ID=fID.read().strip()
fID.close()
fKEY=open('cosmkey.txt')
home_key=fKEY.read().rstrip()
fKEY.close()

print "Found feed ID  {:s}".format(home_ID)
print "Found feed key {:s}".format(home_key)


cpu_key = home_key
cpu_ID = 82576


# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 17
SPIMISO = 10
SPIMOSI = 9
SPICS = 11
# setup the ADC
pi_adc.adc_setup(SPICLK,SPIMISO,SPIMOSI,SPICS)


while adcmode:
    if adcmode>0:
        adcval=pi_adc.readadc(adcmode-1, SPICLK, SPIMOSI, SPIMISO, SPICS)
        time.sleep(0.1)
        print "adcmode on channel {:d} : {:d}".format(adcmode,adcval)
    else:
        adcval=0
        for i in range(1000):
            adcval+=pi_adc.readadc(-adcmode-1, SPICLK, SPIMOSI, SPIMISO, SPICS)
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
#    print cpu_ID
#    print cpu_key
#    print home_ID
#    print home_key
    print "submitting temps"
    submitdata(cpu_ID,cpu_key,testdatastring)
    submitdata(home_ID,home_key,homedatastring)
    
    fLOG=open('datalog.txt','a')
    fLOG.write(homedatastring)
    fLOG.close()


