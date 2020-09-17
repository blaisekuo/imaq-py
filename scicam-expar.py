import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math
import time

from astropy.io import fits 

import os
import argparse
import sys

# variables for the imaq drivers
INTERFACE_ID = C.c_uint32
SESSION_ID = C.c_uint32
iid = INTERFACE_ID(0)
sid = SESSION_ID(0)

Clk=16e6
tickbuf = 1000
text = C.c_char_p(b'test')

# i switch off between the PIRT and image test icd, but they use the same interface string below
#lcp_cam = C.c_char_p('img0') 
#lcp_cam = 'img0'
lcp_cam = C.c_char_p(b'img0') 

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

    parser.add_argument('-p','--path', type=dir_path, help='path of the raw img files')
    parser.add_argument('-n','--name', type=str, help='name prefix of exposures')
    parser.add_argument('-s','--shots', type=int, help='number of exposures to take')
    parser.add_argument('-i','--inttime', type=float, help='integration time')
    return parser.parse_args()
    
def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def main():

    parsed_args = parse_arguments()

    datastore_path = parsed_args.path
    prefix = parsed_args.name
    shots = parsed_args.shots
    inttime = parsed_args.inttime

    #Find imaq dll drivers
    imaqlib_path = Cutil.find_library('imaq')
    imaq = C.windll.LoadLibrary(imaqlib_path)

    # setup the frame sizer
    width = 1280
    height = 1024


    #set up string for the frame grabber
    # use NI software to set the camera ICD file
    # i switch off between the PIRT and image test icd, but they use the same interface string below


    #hex values for certain commands
    #inttime_set = bytearray.fromhex("10 6C")
    #frametime_set = bytearray.fromhex("10 6E")


    #ticks = int(inttime*Clk)
    #tickbyte = struct.pack("<i",ticks)
    #tickbyte = inttime_set + tickbyte
            
    #framerate = int((np.maximum(inttime,0.03333334))*Clk + tickbuf) # max rate of 30 Hz (one frame every 33ms).  
    #framebyte = struct.pack("<i",framerate) # up to 4 bytes in little endian
    #framebyte = frametime_set + framebyte



    # open interface
    rval = imaq.imgInterfaceOpen(lcp_cam, C.byref(iid))


    # open session
    rval = imaq.imgSessionOpen(iid, C.byref(sid))


    # test lines to see the return error code
    #text = C.c_char_p(b'test')
    #imaq.imgShowError(rval, text)
    #print (text.value)

    # for the image test icd use C.c_unit8 and 1024x1024
    image = np.ndarray(shape=(height,width), dtype=C.c_uint16)


    # set up pointer for the buffer
    bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))


    for i in range(shots):
        for j in range(5):
            # take an image snap
            rval = imaq.imgSnap(sid, C.byref(bufAddr))


            #    close session
            rval = imaq.imgClose(sid, 1)
            rval = imaq.imgClose(iid, 1)


            #print(image.shape)
            print("writing frame: " + str(i) + " " + str(j))
            #print(image)

            #write the image to a fits file
            hdu = fits.PrimaryHDU(image)
            hdulist = fits.HDUList([hdu])
            hdulist.writeto(datastore_path + "/" + prefix +  '-' + str(inttime) + 's-' +  str(i) + '-' + str(j) + '.fits',overwrite=False)
            hdulist.close()

            time.sleep(inttime+0.5)
        time.sleep(25.0)

def maintest():
    parsed_args = parse_arguments()
    print(os.listdir(parsed_args.path))

if __name__ =="__main__":
    main()
