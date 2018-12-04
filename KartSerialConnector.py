import serial
try:
    arduino_serial = serial.Serial('/dev/ttyUSB0', 9600)
    print('Arduino Port Open USB 0')
except:
    try:
        arduino_serial = serial.Serial('/dev/ttyUSB1', 9600)
        print('Arduino Port Open USB 1')
    except:
        print('Arduino Port Not Detected USB0 or USB1')
        
def readBatteryInformation():
    global arduino_serial
    try:
        return arduino_serial.readline()
    except:
        print('Cannot read Serial readline')
        return '0.00;0.00'.encode()

