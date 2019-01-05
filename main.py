import os
import re
import sys

r = re.compile("M[14][1-5]{0,1}[AB]{0,1}-POD[\d](-\d+){3}")

def isHostDown(uptime, downtime, host):
    if downtime > uptime:
        print(host + ': Down') 

def parseCritical(miner):
    if miner['Service'] == 'FAN':
        miner['Status'] = "Fan Stopped"
    elif miner['Service'] == 'HashRate':
        if miner['Status'].find("HashRate: 0"):
            miner['Status'] = "HashRate 0"
    print(miner['Hostname'] + " :" + miner['Status'])

def findCritical(line, miner):
    if line.find("host_name") >= 0:
        miner['Hostname'] = line.split("=")[1]
    elif line.find("service_description") >= 0:
        miner['Service'] = line.split("=")[1]
    elif line.find("last_time_ok") >= 0:
        miner['Uptime'] = int(line.split("=")[1])
    elif line.find("last_time_critical") >= 0:
        miner['Downtime'] =  int(line.split("=")[1])
    elif line.find("plugin_output=CRITICAL"):
        miner['Status'] = line.split("=")[1]
        return True
    return False

def parseFile(filename):
    miner = {}
    isParsingHost = False
    isParsingService = False
    uptime = 0
    downtime = 0
    try:
        f = open(filename, 'r')
    except:
        return -1

    for line in f.readlines():
        line = line.rstrip()
        if re.match("^(\w+) \{$", line):
            #miner is found
            if line.find("host") >= 0:
                isParsingService = False
                isParsingHost = True
                continue
            #miner's service is found
            elif line.find("service") >= 0:
                isParsingHost = False
                isParsingService = True
                continue
            else: #not other than host or service
                isParsingService = False
                isParsingHost = False
                continue
        if isParsingHost == True and isParsingService == False:
            if line.find("host_name") >= 0:
                temp = r.search(line)
                if temp != None:
                    hostname = temp.group(0)
                else:
                    isParsingService = False
                    isParsingHost = False
                    continue
            elif line.find("last_time_up") >= 0:
                uptime = int(line.split("=")[1])
            elif line.find("last_time_down") >= 0:
                downtime = int(line.split("=")[1])
                isHostDown(uptime, downtime, hostname)
        elif isParsingHost == False and isParsingService == True:
            if findCritical(line, miner) == True:
                parseCritical(miner)
            else:
                continue

if __name__ == '__main__':
    parseFile(os.path.expanduser('~/Downloads/data.dat'))


