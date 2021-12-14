#!/Users/svallero/anaconda2/bin/python

from datetime import datetime
import calendar
import requests
import lxml.html as lh
import urllib.request
import ssl
import json
#import pandas as pd
#from datetime import datetime
#import calendar
#import sys

sites=["INFN-T1","INFN-BARI","INFN-CATANIA","TRIGRID-INFN-CATANIA","INFN-LNL-2","INFN-TORINO","INFN-TRIESTE"]
sites_final=["INFN-T1","INFN-BARI","INFN-CATANIA","INFN-LNL-2","INFN-TORINO","INFN-TRIESTE"]

def get_ms(month, year):
  format_time = '%Y-%m-%d %H:%M:%S'
  string = str(year)+"-"+str(month)+"-01 00:00:00"
  dt = datetime.strptime(string, format_time)
  ms = calendar.timegm(dt.timetuple())*1000
  return ms

# Timerange is calculated in ms from now
def get_range(month_start, month_stop, year):

  # Now in ms
  now_hour = datetime.now().replace(minute=00, second=00)
  #print (now_hour)
  now = calendar.timegm(now_hour.timetuple())*1000

  # Start in ms
  start = now - get_ms(month_start, year)

  # Stop in ms
  month_stop += 1
  if month_stop == 13:
    month_stop = 1
    year += 1

  stop = now - get_ms(month_stop, year)

  #print get_ms(month_start, year)
  #print get_ms(month_stop, year) 
  return [start, stop]

def make_url(month_start, month_stop, year, plot):
    timerange = get_range(month_start, month_stop, year)
  
    if year == 2021: 
      url="http://alimonitor.cern.ch/display?  annotation.enabled=true&imgsize=1024x600&interval.max="+str(timerange[1])+"&interval.min="+str(timerange[0])+"&page="+plot+"&plot_series=Bari_HTC&plot_series=CNAF&plot_series=CNAF-DUE&plot_series=Catania-VF&plot_series=Legnaro_HTC&plot_series=Torino&&plot_series=Torino-HTC&&plot_series=TriGrid_Catania&plot_series=Trieste"
    else:
      url="http://alimonitor.cern.ch/display?annotation.enabled=true&imgsize=1024x600&interval.max="+str(timerange[1])+"&interval.min="+str(timerange[0])+"&page="+plot+"&plot_series=Bari&plot_series=CNAF&plot_series=CNAF-DUE&plot_series=Catania-VF&plot_series=Legnaro&plot_series=Torino&plot_series=TriGrid_Catania&plot_series=Trieste&plot_series=Catania"

#    url="http://alimonitor.cern.ch/display?annotation.enabled=true&imgsize=1024x600&interval.max="+str(timerange[1])+"&interval.min="+str(timerange[0])+"&page="+plot+"&plot_series=Bari&plot_series=Bari_HTC&plot_series=CNAF&plot_series=CNAF-DUE&plot_series=Catania-VF&plot_series=Legnaro&&plot_series=Legnaro_HTC&plot_series=Torino&plot_series=TriGrid_Catania&plot_series=Trieste&plot_series=Catania"
    return url

def get_monalisa_values(month_start, month_stop, year, metric):
   url = make_url(month_start, month_stop, year, metric)
   #Create a handle, page, to handle the contents of the website
   page = requests.get(url)
   #Store the contents of the website under doc
   doc = lh.fromstring(page.content)

   #Parse data that are stored between <tr>..</tr> of HTML
   tbody = doc.xpath('//tbody')

   # For each row, store each first element (header) and and max value
   values = {}
   i=0
   for t in tbody[0]:
      i+=1
      t.xpath('//td')
      site = t[1].text_content().strip()
      value = t[2].text_content()
      #print(value)
      # cputimes are given with unit
      if 'M' in value:
          val = int(float(value.split()[0])*1000000)
          values[site] = val
      elif 'K' in value:
          val = int(float(value.split()[0])*1000)
          values[site] = val
      elif 'B' in value:
          val = int(float(value.split()[0])*1)
          values[site] = val  
      else:
          values[site] = int(value) 
       
   return values 

def merge_monalisa(values):
    time = {}
    print (values.keys() )
    try:
        time['CNAF'] = str(values['CNAF'] + values['CNAF-DUE']) 
    except: 
        time['CNAF'] = str(values['CNAF'])
        
    try:
        time['BARI'] = str(values['Bari_HTC'])
    except:
        time['BARI'] = str(values['Bari'])
    
    try:
        time['CATANIA'] = str(values['Catania'] + values['TriGrid_Catania'] + values['Catania-VF'])
    except:
        try:
            time['CATANIA'] = str(values['TriGrid_Catania']+ values['Catania'])
        except:
            try:
                time['CATANIA'] = str(values['TriGrid_Catania']+ values['Catania-VF'])
            except:
                try:
                    time['CATANIA'] = str(values['TriGrid_Catania'])
                except:
                    time['CATANIA'] = str(values['Catania-VF'])
    try:
        time['LEGNARO'] = str(values['Legnaro_HTC'])
    except:
        time['LEGNARO'] = str(values['Legnaro'])
     
    try:
        time['TORINO'] = str(values['Torino'] + values['Torino-HTC'])
    except:
        try:
            time['TORINO'] = str(values['Torino'])
        except:
            try:
                time['TORINO'] = str(values['Torino-HTC']) 
            except:
                time['TORINO'] = 1
        
    
    time['TRIESTE'] = str(values['Trieste'])

    return time

def read_write_egi(url, month, year, measurement):
    total = {}
    total["TRIGRID-INFN-CATANIA"]=0
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(url,context = ctx).read()
    data = json.loads(response)
    for d in data:
      if d["id"] in sites:
        total[d['id']] = d["Total"]
        #print total 
        #print d["id"], d["Total"]
    total["INFN-CATANIA"] += total["TRIGRID-INFN-CATANIA"]

    influx_url = 'http://localhost:8086/write?db=alice'
    timestamp = (get_ms(month, year)+(15*24*60*60*1000))*1000000
    for s in sites_final:
      #print s + " " + str(total[s]) 
      data = measurement+",site="+s+" egi="+str(total[s])+" "+str(timestamp)
      print(data)
      x = requests.post(influx_url, data = data)
      print(x)

def read_egi(url, month, year, measurement):
    total = {}
    total["TRIGRID-INFN-CATANIA"]=0
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(url,context = ctx).read()
    data = json.loads(response)
    for d in data:
      if d["id"] in sites:
        total[d['id']] = d["Total"]
        #print total 
        #print d["id"], d["Total"]
    total["INFN-CATANIA"] += total["TRIGRID-INFN-CATANIA"]    
    return total


def remap_egi(values):
    remapped = {}
    try:
        remapped['CNAF'] = values['INFN-T1']
    except:
         remapped['CNAF'] = 1
    try:        
        remapped['BARI'] = values['INFN-BARI']
    except:
        remapped['BARI'] = 1
    try:    
        remapped['CATANIA'] = values['INFN-CATANIA']
    except:
        remapped['CATANIA'] = 1
    try:    
        remapped['LEGNARO'] = values['INFN-LNL-2']
    except:
        remapped['LEGNARO'] =  1
    try:
        remapped['TORINO'] = values['INFN-TORINO']
    except: 
        remapped['TORINO'] = 1
    try:    
        remapped['TRIESTE'] = values['INFN-TRIESTE']
    except:   
        remapped['TRIESTE'] = 1
    return remapped
    
def write_influx(influx_url, month, year, metric, origin, time):
    timestamp = (get_ms(month, year)+(15*24*60*60*1000))*1000000
    for site in ['CNAF','BARI','CATANIA','LEGNARO','TORINO','TRIESTE']:
        data =  metric+",site="+site+" "+origin+"="+str(time[site])+" "+str(timestamp)
        x = requests.post(influx_url, data = data)
        if x.status_code != 204:
            print('Error writing data for month '+str(month)+' source '+str(origin))