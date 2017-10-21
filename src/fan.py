"""
Python implementation of a fan controller based on HDD
and CPU temperature. This is a first draft implementation
so do not expect the most clean code. It's a simple "it works"
version.

Created by @marcusvb (GitLab & GitHub)

"""
from subprocess import Popen, PIPE, STDOUT
import time
import string

maxHddTemp = 53
maxCpuTemp = 80

highHddTemp = 49
highCpuTemp = 70

medHddTemp = 47
medCpuTemp = 60

semiHddTemp = 46
semiCpuTemp = 55

lowHddTemp = 45
lowCpuTemp = 50

sleepTime = 5
celcius = 'C'
floatDot = '.'
user = "root"
password = "calvin"
ip = "192.168.x.xx"

#Do a command and return the stdout of proccess
def sendcommand(cmdIn):
    p = Popen(cmdIn, shell=True, executable="/bin/bash", stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    return p.stdout.read()

#Do a ipmi command, setup for the default command.
def ipmicmd(cmdIn):
    return sendcommand("ipmitool -I lanplus -H " + ip +" -U " + user + " -P " + password + " " + cmdIn)

#Gets hdd temp from megacli and return the average of it
def gethddtemp():
    cmd = sendcommand('megacli -PDList -aALL | grep "Drive Temperature"')
    indexes = [pos for pos, char in enumerate(cmd) if char == celcius]
    hddtemperatures = []
    for loc in indexes:
        temp = cmd[int(loc) - 2] + cmd[int(loc) - 1]
        hddtemperatures.append(int(temp))

    #return the average hdd temperature
    return sum(hddtemperatures) / int(len(hddtemperatures))

#Gets the CPU temperture from lm-sensors, returns the average of it.
def getcputemp():
    cmd = sendcommand('sensors  -u | grep "input"')
    indexes = [pos for pos, char in enumerate(cmd) if char == floatDot]
    cputemperatures = []
    for loc in indexes:
        temp = cmd[int(loc) - 2] + cmd[int(loc) - 1]
        cputemperatures.append(int(temp))

    #return the average cpu temperature
    return sum(cputemperatures) / int(len(cputemperatures))

#Check if controller was in automode, if so we override to manual.
def checkstatus(status):
    if (status == 4):
        ipmicmd("raw 0x30 0x30 0x01 0x00")

#Main checking function which checks temperatures to the default set above.
def checktemps(status):
    avgHddT = gethddtemp()
    avgCpuT = getcputemp()

    if (avgHddT > maxHddTemp or avgCpuT > maxCpuTemp):
        if (status != 4):
            ipmicmd("raw 0x30 0x30 0x01 0x01")
            print("Setting to auto/loud mode, Server it too hot")
        status = 4

    elif(avgHddT > highHddTemp or avgCpuT > highCpuTemp):
        if (status != 3):
            checkstatus(status)
            ipmicmd("raw 0x30 0x30 0x02 0xff 0x20")
            print("Setting to 5000RPM, Server is hot")
        status = 3

    elif(avgHddT > medHddTemp or avgCpuT > medCpuTemp):
        if (status != 2):
            checkstatus(status)
            ipmicmd("raw 0x30 0x30 0x02 0xff 0x16")
            print("Setting to 3600RPM, Server is toasty")
        status = 2

    elif(avgHddT > semiHddTemp or avgCpuT > semiCpuTemp):
        if (status != 1):
            checkstatus(status)
            ipmicmd("raw 0x30 0x30 0x02 0xff 0x12")
            print("Setting to 3200RPM, Server is semi")
        status = 1

    else:
        checkstatus(status)
        if (status != 0):
            ipmicmd("raw 0x30 0x30 0x02 0xff 0x06")
            print("Setting to 1800 RPM, Server is cool")
        status = 0

    print("Cpu at: " + str(avgCpuT) + " celcius \n" + "Hdd at: " + str(avgHddT) +" celcius \n")
    return status

#Main running function.
def main():
    status = 999
    while True:
        time.sleep(sleepTime)
        status = checktemps(status)
        print("Sleeping for " + str(sleepTime))
if __name__ == '__main__':
    main()
