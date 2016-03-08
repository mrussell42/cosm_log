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
import RPi.GPIO as GPIO
from numpy import abs

# 1st arg average length
# 2nd arg display adc values

if len(sys.argv)>1:
    avelen=float(sys.argv[1])
else:
    avelen=5*60

if len(sys.argv)>2:
    adcmode=int(sys.argv[2])
else:
    adcmode=0



def cpuload(interval):
    cpu=os.times()
    #print "Measuring CPU load with interval {:d}".format(interval)
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


def logelec(timestamp,meterval,kW):
    eleclogstr='{:s},{:f},{:f}\n'.format(str(timestamp),meterval,kW)
    print eleclogstr

    streamhome.append('electricity')
    timehome.append(str(timestamp))
    datahome.append("{:2.3f}".format(meterval))
    streamhome.append('power')
    timehome.append(str(timestamp))
    datahome.append("{:2.4f}".format(kW))


    elecLOG=open(elecfilename,'a')
    elecLOG.write(eleclogstr)
    elecLOG.close()

def elecpulsecallback(ch_num):
    # Get the last count
    # If the count > 100 write the time to a file.
    global lastelecmeter
    global lasteleclogtime
    global elecmeter
    global lasttimestamp
    timestamp=datetime.datetime.utcnow()
    deltat=timestamp-lasttimestamp
    #print "Elec Pulse  lastelecmeter {:f}".format(timestamp,lastelecmeter),
    #elecpulse+=1
    elecmeter+=1.0/elecpulseperkWh
    print "{:s}   elecmeter {:f}".format(str(timestamp),elecmeter),
    kWh=elecmeter-lastelecmeter
    dt=float(deltat.seconds+(deltat.microseconds/1000000.0))
    print "dt  {:f}".format(dt),
    print "  kWh {:f}   kW {:f}   count {:1.0f}".format(kWh,(1.0/elecpulseperkWh)*(3600.0/dt),(kWh*elecpulseperkWh))
    if (kWh*elecpulseperkWh)>elecpulselimit:
        interval=timestamp-lasteleclogtime
        if interval.seconds>30:
            logdt=float(interval.seconds+(interval.microseconds/1000000.0))
            kWold=(kWh)*(3600.0/float(interval.seconds))
            kW=(kWh)*(3600.0/logdt)
            print "Average {:f} ({:f}) kW in the last {:f} ({:f}) sec ".format(kW,kWold,logdt,interval.seconds)
            logelec(timestamp,elecmeter,kW)
            lastelecmeter=elecmeter
            lasteleclogtime=timestamp
    lasttimestamp=timestamp


def photo_setup(PHOTOIN):
    print "Setting up photosensor on {:d}".format(PHOTOIN)
    GPIO.setup(PHOTOIN, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
    GPIO.remove_event_detect(PHOTOIN)
    GPIO.add_event_detect(PHOTOIN, GPIO.RISING, callback=elecpulsecallback, bouncetime=200)


def temp_from_adc(adc,sensor_type):
    if sensor_type == 36:
        temperature=25.0+((3.3*(adcval/4095.0))-0.75)/(0.01) # 750mV at 25degC with 10mV/degC
    elif sensor_type == 37:
        temperature=25.0+((3.3*(adcval/4095.0))-0.5)/(0.02) # 500mV at 25degC with 20mV/degC
    else:
        raise Exception('Bad sensor_type')

    return temperature
def main()
    elecfilename='elecmeter'
    lasteleclog=os.popen("tail -n 1 %s" % elecfilename).read()
    lasteleclogtimestr=lasteleclog.split(',')
    #lasteleclogtime=datetime.datetime.strptime(lasteleclogtimestr[0],'%Y-%m-%d %H:%M:%S.%f')
    lasteleclogtime=datetime.datetime.utcnow()
    lastelecmeter=float(lasteleclogtimestr[1])
    lasttimestamp=datetime.datetime.utcnow()
    # feed parameters
    fID=open('cosmfeedID.txt')
    home_ID=fID.read().strip()
    fID.close()
    fKEY=open('cosmkey.txt')
    home_key=fKEY.read().rstrip()
    fKEY.close()

    print "Found feed ID  {:s}".format(home_ID)
    print "Found feed key {:s}".format(home_key)

    print "Loaded previous eletricity meter values {:s}  {:f}".format(str(lasteleclogtime),lastelecmeter)
    print "as logged {:s}".format(lasteleclog)

    elecpulse=0
    elecmeter=lastelecmeter# get this from the last in the elecmeter file
    elecpulseperkWh=800.0 # how many pulses of light for 1kWh
    elecresolution=0.0125 # kWh
    elecpulselimit=elecresolution*elecpulseperkWh


    # change these as desired - they're the pins connected from the
    # SPI port on the ADC to the Cobbler
    SPICLK = 17
    SPIMISO = 10
    SPIMOSI = 9
    SPICS = 11
    #  GPIO for the Photo sensor
    PHOTOIN=14


    # feed parameters
    streamhome=[]
    timehome=[]
    datahome=[]
    unsubmitted="" # unsubmitted data
    fID=open('cosmfeedID.txt')
    home_ID=fID.read().strip()
    fID.close()
    fKEY=open('cosmkey.txt')
    home_key=fKEY.read().rstrip()
    fKEY.close()


    SPI_conf = {'SPICLK':17, 'SPIMISO':10, 'SPIMOSI':9, 'SPICS':11}
    pi_adc.adc_setup(SPI_conf)

    GPIO.setmode(GPIO.BCM)
    elecinterupt = 15

    # setup the ADC
    pi_adc.adc_setup(SPICLK,SPIMISO,SPIMOSI,SPICS)
    # setup the Phototransistor input
    photo_setup(PHOTOIN)

    while adcmode:
        # adcmode is positive, read the value every 0.1 sec from the adc,
        # scale to both types of thermometer for checking
        if adcmode>0:
            adcval=pi_adc.readadc(adcmode-1, SPICLK, SPIMOSI, SPIMISO, SPICS)
            time.sleep(0.1)
            temperature36=temp_from_adc(adcval,36)
            temperature37=temp_from_adc(adcval,37)
            print "adcmode on channel {:d} : {:d} {:2.2f}degC  {:2.2f}degC".format(adcmode,adcval,temperature36,temperature37)

        # adcmode is negative, read the channel as fast as possible and average
        # 1000 values
        else:
            adcval=0
            for i in range(1000):
                #adcval+=pi_adc.readadc(-adcmode-1, SPICLK, SPIMOSI, SPIMISO, SPICS)
                adcval+=meastemp(abs(adcmode)-1,36)

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
            cpu_sum=0
            temp_int=0
            temp_ext=0
            for count in range(int(avelen)):
                cpu_sum+=cpuload(1)
                #print "Averaging loop tick"
                #time.sleep(3)
                temp_int+=meas_temp(1,37)
                temp_ext+=meas_temp(2,36)
            temp_int = temp_int_sum/avelen
            temp_ext = temp_ext_sum/avelen
            cpu = cpu_sum *100.0/ avelen



            timenow = datetime.datetime.utcnow()
            #streamname.append('cpu')
            #thetime.append(str(datetime.datetime.utcnow()))
            #data.append(cpusum*100.0/avelen) # convert to a percent
            streamd.append('{:s},{:s},{:1.1f}\n'.format('cpu',timenow,cpu))
            streamh.append('{:s},{:s},{:2.3f}\n'.format('tempinside',timenow,temp_int))
            #streamhome.append('tempinside')
            #timehome.append(str(datetime.datetime.utcnow()))
            #datahome.append("{:2.3f}".format(tempint/avelen))

            if tempext>-20:
                # if the temperature is less than -20C outside then there
                # is probably an error with the ADC measurement so we don't log it.
                #streamhome.append('tempoutside')
                #timehome.append(str(datetime.datetime.utcnow()))
                #datahome.append("{:2.3f}".format(tempext/avelen))
                streamh.append('{:s},{:s},{:2.3f}\n'.format('tempoutside',timenow,temp_ext)


    homedatastring=pi_cosm.builddatacsv(streamhome,timehome,datahome)
    testdatastring=pi_cosm.builddatacsv(streamname,thetime,data)
        #print testdatastring
#    print cpu_ID
#    print cpu_key
#    print home_ID
#    print home_key
    print "submitting temps"
#    pi_cosm.submitdata(cpu_ID,cpu_key,testdatastring)
    response=pi_cosm.submitdata(home_ID,home_key,unsubmitted+homedatastring)

    if response==200:
        unsubmitted=""
        print "Unsubmitted empty"
    else:
        unsubmitted+=homedatastring
        print "These values have not been submitted"
        print unsubmitted

    fLOG=open('datalog.txt','a')
    fLOG.write(homedatastring)
    fLOG.close()

            print "{:s} Temp Internal {:2.2f} ".format(timenow,temp_int),
            print "  Temp External {:2.2f}   CPU Load {:2.1f}%".format(temp_ext,cpu)



        #homedatastring=pi_cosm.builddatacsv(streamhome,timehome,datahome)
        testdatastring=pi_cosm.builddatacsv(streamname,thetime,data)
        homedatastring="".join(streamh)
        testdatastring="".join(streamd)

        print "submitting temps"
        pi_cosm.submitdata(cpu_ID,cpu_key,testdatastring)
        pi_cosm.submitdata(home_ID,home_key,homedatastring)

        fLOG=open('datalog.txt','a')
        fLOG.write(homedatastring)
        fLOG.close()

if __name__ == "__main__":
    main()
