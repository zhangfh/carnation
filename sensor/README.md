Using Python 3.5.2
1.
   #sudo apt install python3-venv
   #pyvenv venv
   #source venv/bin/active

2. pyserial
   # pip install pyserial

   open serial, 2400, 8N1, timeout 0.5 second
   >>> import serial
   >>> ser = serial.Serial('/dev/ttyUSB0',2400,timeout=0.5)
	
   Error: could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
   Resolve:	
   #sudo usermod -aG dialout zhangfanghui
   #logout

   >>> import serial
   >>> ser = serial.Serial('/dev/ttyUSB0',2400,timeout=0.5)
   >>> print(ser.name)
       /dev/ttyUSB0
   >>> print(ser.port)
       /dev/ttyUSB0
   >>>data = ser.read(2048) #read 2048 bytes
   >>> data.count(0) #data type is bytes.
      posibble value: 805, 810, 794 意味着每次收到数据不超过1024
   >>> len(data)  # data.count(0) cause bug,^_^



