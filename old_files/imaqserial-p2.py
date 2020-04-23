import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math
import time
import struct
import crcmod

from astropy.io import fits 

#Find imaq dll drivers
imaqlib_path = Cutil.find_library('imaq')
imaq = C.windll.LoadLibrary(imaqlib_path)


datastore_path="c:/cloudstor/datastore/imaqtest/"

# setup the frame sizer
width = 1280
height = 1024
Clk=16e6
tickbuf = 1000
text = C.c_char_p(b'test')

# variables for the imaq drivers
INTERFACE_ID = C.c_uint32
SESSION_ID = C.c_uint32
iid = INTERFACE_ID(0)
sid = SESSION_ID(0)

# i switch off between the PIRT and image test icd, but they use the same interface string below
#lcp_cam = C.c_char_p('img0') 
lcp_cam = 'img0'

#hex values for certain commands
inttime_set = bytearray.fromhex("10 6C")
frametime_set = bytearray.fromhex("10 6E")

inttime = 10

ticks = int(inttime*Clk)
tickbyte = struct.pack("<i",ticks)
tickbyte = inttime_set + tickbyte
        
framerate = int((np.maximum(inttime,0.03333334))*Clk + tickbuf) # max rate of 30 Hz (one frame every 33ms).  
framebyte = struct.pack("<i",framerate) # up to 4 bytes in little endian
framebyte = frametime_set + framebyte

# open interface
rval = imaq.imgInterfaceOpen(lcp_cam, C.byref(iid))


# open session
rval = imaq.imgSessionOpen(iid, C.byref(sid))

def SerialSend(cmd2):
    sreturn = C.create_string_buffer(30)
    sendsize = C.c_uint32(30)
    rsize = C.c_uint32(30)
    stimeout = C.c_uint32(50)
    crc16 = crcmod.mkCrcFun(0x1755b, rev=False, initCrc=0xFFFF, xorOut=0x0000)

    cmd = cmd2
    cmd = cmd.replace('\x5c','\x5c\x5c').replace('\xff','\x5c\xff')
    cmd = '\xff' + cmd
    cmd = '\x00' + cmd

    print cmd2
    print map(hex,cmd)

    crccalc = bytes(cmd[0:])

    print crccalc[0]

    a = crc16(crccalc[0])
    print(a)
    crccalc = bytes(cmd[1:])
    for d in crccalc:
        a = crc16(d,a)

    print(map(str,crccalc))
    print(a)
    crc = "".join(map(chr,divmod((a ^ 0xFFFF),256 )))
    crc = crc.replace('\x5c','\x5c\x5c')
    cmd = cmd + crc
 
    cmd = cmd.replace('\x3e','\x5c\x3e')
    cmd = '\x3e' + cmd + '\x3e'

    print "crc is:"
    print crc
    print map(str,crc)
    print "cmd is:"
    print map(hex,cmd)
    print map(str,cmd)
    print(str(cmd))
    print(bytes(cmd))
    print cmd


    print("Command to send to serial:", map(hex,cmd))
    print str(cmd)
    print len(cmd)
    sendcmd = C.create_string_buffer(bytes(cmd))
    sendsize.value = len(cmd)
    rval = imaq.imgSessionSerialFlush(sid)
    imaq.imgShowError(rval, text)
    print("buffer flushed: " + (text.value))
    if rval != 0:
        print("Not connected to Scicam")


    rval = imaq.imgSessionSerialWrite(sid, C.byref(sendcmd), C.byref(sendsize), stimeout)
    imaq.imgShowError(rval, text)
    print("Sent: " + (text.value))
    rval = imaq.imgSessionSerialReadBytes(sid, C.byref(sreturn), C.byref(rsize), stimeout)
    imaq.imgShowError(rval, text)
    print("Received: " + (text.value))
    rsizeval = rsize.value
    ret = sreturn.raw

    if ret[0] == '\x3e' and ret[rsizeval-1] == '\x3e':
        if ret[1] == '\xa0' or ret[1] == '\x20' or ret[1] == '\x00':
            crccalc = bytes(ret[1:rsizeval-3])
            a = crc16(crccalc[0])
            crccalc = str(ret[2:rsizeval-3]).replace('\x5c\x5c','\x5c').replace('\x5c\x3e','\x3e').replace('\x5c\xff','\xff')
            for d in crccalc:
                a = crc16(d,a)
                #print d, hex(a), hex(a ^ 0xFFFF)
                
            crc = "".join(map(chr,divmod((a ^ 0xFFFF),256 )))
            crcret = bytes(ret[rsizeval-3:rsizeval-1])
            #print crc, crcret
            if crc == crcret:
                print "good CRC"
                serial_ret = str(map("{0:>02x}".format,map(ord,crccalc[1:]))).translate(None,"[]',")
                print serial_ret
                return serial_ret
            else:
                print "bad CRC"
                return -3
        else:
            print "bad ack/nak/null"
            return -2
    else:
        print "incomplete packet?"
        return -1

SerialSend(tickbyte)
time.sleep(0.5)
SerialSend(framebyte)



image = np.ndarray(shape=(height,width), dtype=C.c_uint16)


# set up pointer for the buffer
bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))


# take an image snap
#rval = imaq.imgSnap(sid, C.byref(bufAddr))


# close session
#rval = imaq.imgClose(sid, 1)
#rval = imaq.imgClose(iid, 1)

#hdu = fits.PrimaryHDU(image)
#hdulist = fits.HDUList([hdu])
#hdulist.writeto(datastore_path + 'test-1s.fits',overwrite=True)
#hdulist.close()