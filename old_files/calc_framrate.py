import struct
import numpy as np


Clk=16e6
tickbuf = 1000

#hex values for certain commands
inttime_set = bytearray.fromhex("10 6C")
frametime_set = bytearray.fromhex("10 6E")

inttime = 12

ticks = int(inttime*Clk)
tickbyte = struct.pack("<i",ticks)
tickbyte = inttime_set + tickbyte
        
framerate = int((np.maximum(inttime,0.03333334))*Clk + tickbuf) # max rate of 30 Hz (one frame every 33ms).  
framebyte = struct.pack("<i",framerate) # up to 4 bytes in little endian
framebyte = frametime_set + framebyte

print(ticks)
print(framerate)

