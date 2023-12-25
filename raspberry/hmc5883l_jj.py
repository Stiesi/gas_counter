#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :

# HMC5888L Magnetometer (Digital Compass) wrapper class
# Based on https://bitbucket.org/thinkbowl/i2clibraries/src/14683feb0f96,
# but uses smbus rather than quick2wire and sets some different init
# params.

import smbus2 as smbus
import math
import time
import sys
import random

global timetochange,x,y,z 
class hmc_dummy:
    def __init__(self,min=-1000,max=1000):
        self.min=min
        self.max=max
        self.latest_datum = (0,0,0)
        self.latest_nonecount=0
        self.timetochange = time.time()+random.randint(3,10)
        self.xyz=(0,0,0)


        
    def randomvalues(self):
        return random.uniform(self.min,self.max)
        
    def safeaxes(self):
        now = time.time()
        if self.timetochange<now:
            self.timetochange = now+random.randint(3,10)
            x,y,z=self.axes()            
            self.latest_datum = (x,y,z)
            self.latest_nonecount=0
        else:
            x,y,z=self.latest_datum
            self.latest_nonecount+=1
        return x,y,z,self.latest_nonecount

    def axes(self):
        x=self.randomvalues()
        y=self.randomvalues()
        z=self.randomvalues()
        return (x,y,z)

class hmc5883l:

    __scales = {
        0.88: [0, 0.73],
        1.30: [1, 0.92],
        1.90: [2, 1.22],
        2.50: [3, 1.52],
        4.00: [4, 2.27],
        4.70: [5, 2.56],
        5.60: [6, 3.03],
        8.10: [7, 4.35],
    }

    def __init__(self, port=1, address=0x1e, gauss=1.3, declination=(0,0)):
        self.bus = smbus.SMBus(port)
        self.address = address

        (degrees, minutes) = declination
        self.__declDegrees = degrees
        self.__declMinutes = minutes
        self.__declination = (degrees + minutes / 60) * math.pi / 180

        (reg, self.__scale) = self.__scales[gauss]
        self.bus.write_byte_data(self.address, 0x00, 0x70) # 8 Average, 15 Hz, normal measurement
        self.bus.write_byte_data(self.address, 0x01, reg << 5) # Scale
        self.bus.write_byte_data(self.address, 0x02, 0x00) # Continuous measurement
        self.latest_datum = (0,0,0)
        self.latest_nonecount=0

    def declination(self):
        return (self.__declDegrees, self.__declMinutes)

    def twos_complement(self, val, len):
        # Convert twos compliment to integer
        if (val & (1 << len - 1)):
            val = val - (1<<len)
        return val

    def __convert(self, data, offset):
        val = self.twos_complement(data[offset] << 8 | data[offset+1], 16)
        if val == -4096: return None
        return round(val * self.__scale, 4)

    def safeaxes(self):
        x,y,z = self.axes()
        if None in (x,y,z):
            self.latest_nonecount+=1
            x,y,z=self.latest_datum
        else:
            self.latest=(x,y,z)
            self.latest_nonecount=0
        return (x,y,z,self.latest_nonecount)



    def axes(self,pout=False):
        data = self.bus.read_i2c_block_data(self.address, 0x00,16)
        #print(data)
        #print (map(hex, data))
        x = self.__convert(data, 3)
        y = self.__convert(data, 7)
        z = self.__convert(data, 5)
        if pout:
            if y is not None:
                print(' %.2f, %.2f, %.2f'%(x,y,z),end='\r')
            else:
                print('error:',data)
        return (x,y,z)

    def heading(self):
        (x, y, z) = self.axes()
        headingRad = math.atan2(y, x)
        headingRad += self.__declination

        # Correct for reversed heading
        if headingRad < 0:
            headingRad += 2 * math.pi

        # Check for wrap and compensate
        elif headingRad > 2 * math.pi:
            headingRad -= 2 * math.pi

        # Convert to degrees from radians
        headingDeg = headingRad * 180 / math.pi
        return headingDeg
    
    def magmag(self):
        (x, y, z) = self.axes()
        mag = math.sqrt(x*x+y*y+z*z)
        return mag

    def degrees(self, headingDeg):
        degrees = math.floor(headingDeg)
        minutes = round((headingDeg - degrees) * 60)
        return (degrees, minutes)

    def __str__(self):
        (x, y, z) = self.safeaxes()
        return "Axis X: " + str(x) + "\n" \
               "Axis Y: " + str(y) + "\n" \
               "Axis Z: " + str(z) + "\n" \
               "Declination: " + self.degrees(self.declination()) + "\n" \
               "Heading: " + self.degrees(self.heading()) + "\n"

if __name__ == "__main__":
    if 1:
        # http://magnetic-declination.com/Great%20Britain%20(UK)/Harrogate#
        try:
            compass = hmc5883l(gauss = 4.7, declination = (-2,5))
        except:
            compass = hmc_dummy()

        while True:
    #        sys.stdout.write("\rHeading: " + str(compass.degrees(compass.heading())) + "    \n")
            (x,y,z,nonecount)=compass.safeaxes()
            if compass.latest_nonecount==0:
                mag = math.sqrt(x*x+y*y+z*z)
                print(f"\rcomps: {x,y,z} > Mag:{mag}",end="\r")
            else:
                print("\rError in reading from hmc")
                print(x,y,z)
            time.sleep(1.0)
