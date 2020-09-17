import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math
import time
import crcmod
import struct


from astropy.io import fits 

import os
import argparse
import sys

# variables for the imaq drivers
INTERFACE_ID = C.c_uint32
SESSION_ID = C.c_uint32
iid = INTERFACE_ID(0)
sid = SESSION_ID(0)
# i switch off between the PIRT and image test icd, but they use the same interface string below
#lcp_cam = C.c_char_p('img0') 
#lcp_cam = 'img0'
lcp_cam = C.c_char_p(b'img0')

#variables for integration times
Clk=16e6
tickbuf = 1000
text = C.c_char_p(b'test')

# setup the frame sizer
width = 1280
height = 1024

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert Princeton IR Tech 1280 Scicam raw img files into fits')
    
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    parser.add_argument('-i','--inttime', type=float, help='set exposure time in seconds')
    parser.add_argument('-p','--path', type=dir_path, help='path of the raw img files')
    parser.add_argument('-n','--name', type=str, help='name prefix of exposures')
    parser.add_argument('-s','--shots', type=int, help='number of exposures to take')

    return parser.parse_args()


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def SerialSend(imaq,cmd2):

    print("Sending commands...")

    sreturn = C.create_string_buffer(30)
    sendsize = C.c_uint32(30)
    rsize = C.c_uint32(30)
    stimeout = C.c_uint32(50)
    #crc16 = crcmod.mkCrcFun(0x1755b, rev=False, initCrc=0xFFFF, xorOut=0x0000)
    crc16 = crcmod.mkCrcFun(0x1755B,initCrc=0,rev=False,xorOut=0xFFFF)

    

    cmd = cmd2
    cmd = cmd.replace(b'\x5c',b'\x5c\x5c').replace(b'\xff',b'\x5c\xff')
    print(cmd)
    cmd = b'\xff' + cmd
    cmd = b'\x00' + cmd



    crccalc = bytearray.fromhex(cmd[0:].hex())

    #a = hex(crc16(crccalc))
    a = crc16(crccalc)


    #crc=a[2:6]
    crc = "%04x" % a  # outputs a hex string of length 4 
    crc=bytes.fromhex(crc)

    cmd = cmd + crc
    cmd = cmd.replace(b'\x3e',b'\x5c\x3e')
    cmd = b'\x3e' + cmd + b'\x3e'

    print("Command to send to serial:", cmd.hex())

    sendcmd = C.create_string_buffer(bytes(cmd))
    sendsize.value = len(cmd)
    rval = imaq.imgSessionSerialFlush(sid)
    imaq.imgShowError(rval, text)
    print("buffer flushed: " + str(text.value))
    if rval != 0:
        print("Not connected to Scicam")

    
    
    rval = imaq.imgSessionSerialWrite(sid, C.byref(sendcmd), C.byref(sendsize), stimeout)
    imaq.imgShowError(rval, text)
    print("Sent: " + str(text.value))
    rval = imaq.imgSessionSerialReadBytes(sid, C.byref(sreturn), C.byref(rsize), stimeout)
    imaq.imgShowError(rval, text)
    print("Received: " + str(text.value))
    rsizeval = rsize.value
    ret = sreturn.raw

    

def takesnap(imaq,image):

    print("taking exposure")

    # set up pointer for the buffer
    bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))
    # take an image snap
    rval = imaq.imgSnap(sid, C.byref(bufAddr))


    # close session
    rval = imaq.imgClose(sid, 1)
    rval = imaq.imgClose(iid, 1)


    #return image

def savesnap(filename,image):
    #print(image.shape)
    print("writing frame: " + filename)
    #print(image)

    #write the image to a fits file
    hdu = fits.PrimaryHDU(image)
    hdulist = fits.HDUList([hdu])
    hdulist.writeto(filename,overwrite=False)
    hdulist.close()

def main():

    #Find imaq dll drivers
    imaqlib_path = Cutil.find_library('imaq')
    imaq = C.windll.LoadLibrary(imaqlib_path)



    #hex values for certain commands
    inttime_set = bytearray.fromhex("10 6C")
    frametime_set = bytearray.fromhex("10 6E")

    parsed_args = parse_arguments()
    datastore_path = parsed_args.path
    prefix = parsed_args.name
    shots = parsed_args.shots
    inttime = parsed_args.inttime



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

    SerialSend(imaq,tickbyte)
    time.sleep(0.5)
    SerialSend(imaq,framebyte)
    time.sleep(0.5)

    image = np.ndarray(shape=(height,width), dtype=C.c_uint16)

    for i in range(shots):

        print(i)
        takesnap(imaq,image)
        filename = datastore_path + "/" + prefix +  '-' + str(inttime) + 's-' +  str(i) + '.fits'
        savesnap(filename,image)

        time.sleep(inttime+0.5)


def maintest():
    parsed_args = parse_arguments()
    print(parsed_args.exposure)


if __name__ =="__main__":
    main()

