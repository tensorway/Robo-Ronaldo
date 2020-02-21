import time
import serial
               
ser = serial.Serial(            
     port='/dev/ttyS0',
     baudrate = 115200,
     parity=serial.PARITY_NONE,
     stopbits=serial.STOPBITS_ONE,
     bytesize=serial.EIGHTBITS,
     timeout=1
)

def send_byte(x):
    #print(x)
    b = x.to_bytes(1, byteorder = 'big')
    ser.write(b)

def set_moving_angle(angle, speed):
    angle = int(angle)
    int_speed = (int)(speed * 1000)
    a1 = int_speed >> 8
    a2 = int_speed - (a1 << 8)
    a3 = angle >> 8
    a4 = angle - (a3 << 8)
    #print(a1, a2, a3, a4)
    
    ser.write(b'm')
    ser.write(b'u')
    ser.write(b'u')
    ser.write(b'u')
    send_byte(a3)
    send_byte(a4)
    send_byte(a1)
    send_byte(a2)
    
def pause():
    ser.write(b'm')
    ser.write(b'p')
    ser.write(b'p')
    ser.write(b'p')
    
    ser.write(b'p')
    ser.write(b'p')
    ser.write(b'p')
    ser.write(b'p')
    
def start():
    ser.write(b'm')
    ser.write(b's')
    ser.write(b's')
    ser.write(b's')
    
    ser.write(b's')
    ser.write(b's')
    ser.write(b's')
    ser.write(b's')
   
def kick():
    ser.write(b'm')
    ser.write(b'k')
    ser.write(b'k')
    ser.write(b'k')
    
    ser.write(b'k')
    ser.write(b'k')
    ser.write(b'k')
    ser.write(b'k')
    
def set_orientation(angle = 0):
    ser.write(b'm')
    ser.write(b'o')
    ser.write(b'o')
    ser.write(b'o')
    
    angle = int(angle)
    a3 = angle >> 8
    a4 = angle - (a3 << 8)
    #print(a1, a2, a3, a4)
    
    send_byte(a3)
    send_byte(a4)
    ser.write(b'o')
    ser.write(b'o')    
  
    