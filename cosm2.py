# -*- coding:utf-8 -*-
"""
Created on 20 Sep 2012

@author: matthew.russell
"""



#import eeml
import datetime
import time
#a=datetime.tzinfo()
import httplib
import os
import subprocess

#import math

# parameters
API_KEY = 'PqhIzb_R767PMeBR8NsX97Y555eSAKxyQmRzTGRhcnc4ND0g'
API_URL = 76780

#pac = eeml.Cosm(API_URL, API_KEY)
#at = datetime.datetime.utcnow()

#pac._use_https=True
#print at
#for i in range(3,3000):
#pac.update([eeml.Data('1',34, unit=eeml.Unit('kg',type_='basicSI',symbol='kg'))])
    #at = datetime.datetime.utcnow()
    
    #pac.update(eeml.Data('Mass',80-(math.fmod(i,5)**2),at=at))
    #print pac.geteeml(False)
    #pac.put()
    #time.sleep(30)
    
#datastring= '10,' + str(at) + 'Z,56\n'+ 'Mass,' + str(at) + 'Z,55\n' 

#print datastring
def submitdata(feedno,key,data):
    
    conn = httplib.HTTPSConnection('api.cosm.com', timeout=10)
    feedpath='/v2/feeds/{:d}.csv'.format(feedno)
    print "updating feed: " + feedpath
    print "Key: " + key
    print "data: " + data
    
    
    conn.request('PUT',feedpath,data,{'X-ApiKey': key})
    conn.sock.settimeout(5.0)
    resp=conn.getresponse()
    resp.read()
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


# feed parameters

testAPI_KEY = 'CdUrvVUGJkZcDzeCJmSg_v-gyoqSAKxCR28xVUFhYjhoRT0g'
testAPI_URL = 82576

#last_cpu=os.times()

for j in range(48):
    # once an hour update the stream
    streamname=[]
    thetime=[]
    data=[]

    for i in range(60):
        # Measure the cpu usage over the last minute
        #time.sleep(2)
        streamname.append('cpu')
        thetime.append(str(datetime.datetime.utcnow()))
        cpul=cpuload(30)
        data.append(cpul*100.0) # convert to a percent
        print "{:s}  {:e}".format(thetime[i],data[i])


        testdatastring=builddatacsv(streamname,thetime,data)
        #print testdatastring

    submitdata(testAPI_URL,testAPI_KEY,testdatastring)

