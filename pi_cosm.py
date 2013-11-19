#!/usr/bin/python



import httplib


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

