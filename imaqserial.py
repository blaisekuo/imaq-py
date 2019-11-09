import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math
import struct
import crcmod

from astropy.io import fits 

#Find imaq dll drivers
imaqlib_path = Cutil.find_library('imaq')
imaq = C.windll.LoadLibrary(imaqlib_path)

# setup the frame sizer
width = 1280
height = 1024
Clk=16e6
tickbuf = 1000

# variables for the imaq drivers
INTERFACE_ID = C.c_uint32
SESSION_ID = C.c_uint32
iid = INTERFACE_ID(0)
sid = SESSION_ID(0)

# i switch off between the PIRT and image test icd, but they use the same interface string below
lcp_cam = C.c_char_p(b'img0') 

#hex values for certain commands
inttime_set = bytearray.fromhex("10 6C")
frametime_set = bytearray.fromhex("10 6E")

inttime = 1

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

sreturn = C.create_string_buffer(30)

sendsize = C.c_uint32(30)

rsize = C.c_uint32(30)

stimeout = C.c_uint32(50)

crc16 = crcmod.mkCrcFun(0x1755b, rev=False, initCrc=0xFFFF, xorOut=0x0000)

cmd = tickbyte

# add escape chars to \xff, \x5c

cmd = cmd.replace(b'\x5c',b'\x5c\x5c').replace(b'\xff',b'\x5c\xff')
# start commands with '\xff'
cmd = b'\xff' + cmd
# start commands with acknaknull '\x00'  No file transfer commands implemented yet. 
cmd = b'\x00' + cmd

# compute CRC16 code
crccalc = bytes(cmd[0:])
#print(crccalc[1])
a = crc16(bytearray(crccalc[0]))
crccalc = bytes(cmd[1:])
for d in crccalc:
    a = crc16(bytearray(d),a)

# add crc16 to cmd
crc = "".join(map(chr,divmod((a ^ 0xFFFF),256 )))
print(crc)
crc = crc.replace('\x5c','\x5c\x5c')
cmd = cmd + crc
# add escape chars to \x3e
cmd = cmd.replace(b'\x3e',b'\x5c\x3e')
# start and end each command with \x3E
cmd = b'\x3e' + cmd + b'\x3e'

print("Command to send to serial:", map(hex,cmd))
#print str(cmd) , len(cmd)
#print "setting c buffer str"
sendcmd = C.create_string_buffer(str(cmd))
#print "setting c buffer len"
sendsize.value = len(cmd)
#print self.sendcmd.raw, self.sendsize.value

# check if sid is open
#print "flushing seral buffer"
rval = imaq.imgSessionSerialFlush(sid)
imaq.imgShowError(rval, text)
print("buffer flushed: " + (text.value))
if rval != 0:
    print("Not connected to Scicam")
    #return -4


#print size.value
rval = imaq.imgSessionSerialWrite(sid, C.byref(sendcmd), C.byref(sendsize), stimeout)
#rval = 0
imaq.imgShowError(rval, text)
print("Sent: " + (text.value))
#time.sleep(0.25)
# the read command looks for specific termination char which is not defined for scicam
#self.imaq.imgSessionSerialRead(self.sid, C.byref(cmd), C.byref(size), stimeout)
# just read in bytes, let it timeout since none of my responses will be too large.
# I could do while loop... but this is fine for now.  
rval = imaq.imgSessionSerialReadBytes(sid, C.byref(sreturn), C.byref(rsize), stimeout)
imaq.imgShowError(rval, text)
print("Received: " + (text.value))
rsizeval = rsize.value
ret = sreturn.raw
#print ret, rsizeval
#for i in self.sreturn: print hex(ord(i))
# Error check
if ret[0] == b'\x3e' and ret[rsizeval-1] == b'\x3e':
    if ret[1] == b'\xa0' or ret[1] == b'\x20' or ret[1] == b'\x00':
        crccalc = bytes(ret[1:rsizeval-3])
        a = crc16(bytearray(crccalc[0]))
        crccalc = str(ret[2:rsizeval-3]).replace(b'\x5c\x5c',b'\x5c').replace(b'\x5c\x3e',b'\x3e').replace(b'\x5c\xff',b'\xff')
        for d in crccalc:
            a = crc16(bytearray(d),a)
            #print d, hex(a), hex(a ^ 0xFFFF)
            
        crc = "".join(map(chr,divmod((a ^ 0xFFFF),256 )))
        crcret = bytes(ret[rsizeval-3:rsizeval-1])
        #print crc, crcret
        if crc == crcret:
            print("good CRC")
            serial_ret = str(map("{0:>02x}".format,map(ord,crccalc[1:]))).translate(None,"[]',")
            print(serial_ret)
            #return serial_ret
        else:
            print("bad CRC")
            #return -3
    else:
        print("bad ack/nak/null")
        #return -2
else:
    print("incomplete packet?")
    #return -1