import serial
from time import sleep
from threading import Thread,currentThread,activeCount
from CircleBuffer import CircularBufferBase

EV3_UART_SEND_ACK_DELAY = 0.01 #10ms
    
EV3_UART_MODE_MAX =7
EV3_UART_MSG_TYPE_SYS   = 0x00
EV3_UART_MSG_TYPE_CMD   = 0x40
EV3_UART_MSG_TYPE_INFO  = 0x80
EV3_UART_MSG_TYPE_DATA  = 0xC0
    
EV3_UART_MSG_TYPE_MASK = 0xC0
EV3_UART_MSG_CMD_MASK   = 0x07

EV3_UART_CMD_TYPE       = 0x0
EV3_UART_CMD_MODES      = 0x1
EV3_UART_CMD_SPEED      = 0x2
EV3_UART_CMD_SELECT     = 0x3
EV3_UART_CMD_WRITE      = 0x4

EV3_UART_MAX_DATA_SIZE = 32
EV3_UART_MAX_MESSAGE_SIZE = EV3_UART_MAX_DATA_SIZE + 2
    
EV3_UART_SPEED_MIN = 2400
EV3_UART_SPEED_MID = 57600
EV3_UART_SPEED_MAX = 460800

EV3_UART_TYPE_ID_COLOR       = 29
EV3_UART_TYPE_ID_ULTRASONIC  = 30
EV3_UART_TYPE_ID_GYRO        = 32
EV3_UART_TYPE_ID_INFRARED    = 33
EV3_UART_TYPE_MAX = 101

	
EV3_UART_INFO_NAME	= 0x00
EV3_UART_INFO_RAW	= 0x01
EV3_UART_INFO_PCT	= 0x02
EV3_UART_INFO_SI	= 0x03
EV3_UART_INFO_UNITS	= 0x04
EV3_UART_INFO_FORMAT	= 0x80

EV3_UART_INFO_BIT_CMD_TYPE = 0
EV3_UART_INFO_BIT_CMD_MODES = 1
EV3_UART_INFO_BIT_CMD_SPEED = 2
EV3_UART_INFO_BIT_INFO_NAME = 3
EV3_UART_INFO_BIT_INFO_RAW = 4
EV3_UART_INFO_BIT_INFO_PCT = 5
EV3_UART_INFO_BIT_INFO_SI = 6
EV3_UART_INFO_BIT_INFO_UNITS =7
EV3_UART_INFO_BIT_INFO_FORMAT = 8
	
EV3_UART_INFO_FLAG_CMD_TYPE	= EV3_UART_INFO_BIT_CMD_TYPE
EV3_UART_INFO_FLAG_CMD_MODES	= EV3_UART_INFO_BIT_CMD_MODES
EV3_UART_INFO_FLAG_CMD_SPEED	= EV3_UART_INFO_BIT_CMD_SPEED
EV3_UART_INFO_FLAG_INFO_NAME	= EV3_UART_INFO_BIT_INFO_NAME
EV3_UART_INFO_FLAG_INFO_RAW	= EV3_UART_INFO_BIT_INFO_RAW
EV3_UART_INFO_FLAG_INFO_PCT	= EV3_UART_INFO_BIT_INFO_PCT
EV3_UART_INFO_FLAG_INFO_SI	= EV3_UART_INFO_BIT_INFO_SI
EV3_UART_INFO_FLAG_INFO_UNITS	= EV3_UART_INFO_BIT_INFO_UNITS
EV3_UART_INFO_FLAG_INFO_FORMAT	= EV3_UART_INFO_BIT_INFO_FORMAT

EV3_UART_INFO_FLAG_ALL_INFO	= EV3_UART_INFO_FLAG_INFO_NAME | EV3_UART_INFO_FLAG_INFO_RAW | EV3_UART_INFO_FLAG_INFO_PCT | EV3_UART_INFO_FLAG_INFO_SI | EV3_UART_INFO_FLAG_INFO_UNITS | EV3_UART_INFO_FLAG_INFO_FORMAT

EV3_UART_INFO_FLAG_REQUIRED	= EV3_UART_INFO_FLAG_CMD_TYPE | EV3_UART_INFO_FLAG_CMD_MODES | EV3_UART_INFO_FLAG_INFO_NAME | EV3_UART_INFO_FLAG_INFO_FORMAT

EV3_UART_DATA_8		= 0x00
EV3_UART_DATA_16	= 0x01
EV3_UART_DATA_32	= 0x02
EV3_UART_DATA_FLOAT	= 0x03

        
LEGO_SENSOR_DATA_U8 = 0x00
LEGO_SENSOR_DATA_S8 = 0x01
LEGO_SENSOR_DATA_U16 = 0x02
LEGO_SENSOR_DATA_S16 = 0x03
LEGO_SENSOR_DATA_S16_BE = 0x04
LEGO_SENSOR_DATA_S32 = 0x05
LEGO_SENSOR_DATA_S32_BE = 0x06
LEGO_SENSOR_DATA_FLOAT = 0x07
NUM_LEGO_SENSOR_DATA_TYPE = 0x08

	
EV3_UART_SYS_SYNC	= 0x0
EV3_UART_SYS_NACK	= 0x2
EV3_UART_SYS_ACK	= 0x4
EV3_UART_SYS_ESC	= 0x6

class SensorPort(object):
    def __init__(self):
        self.type_id = 0
        self.synced = False
        self.info_done = False
        self.last_err = ""
        self.raw_data = [] 
        self.data_rec = 0
        self.info_flags = 0 #info_flags Flags indicating what information has already been read from the sensor
        self.new_baud_rate = 2400
        self.sensor_mode = 0
        self.circ_buf = CircularBufferBase(1024)
        self.received_thread = Thread(target=self.uart_handle_rx_data)
        
        self.debug_thread = Thread(target = self.simulatethread)
        try:
            self.serialport = serial.Serial('/dev/ttyUSB0',EV3_UART_SPEED_MIN,timeout=0.5)
        except serial.serialutil.SerialException:
            print("cannot open ttyUSB0")
        print("serial debug")
        print("serial parity ",self.serialport.parity)
        print("serial stopbits ", self.serialport.stopbits)

    def ev3_uart_cmd_size(self, byte):
        return (1 << (((byte) >> 3) & 0x7))

    def ev3_uart_msg_size(self, header):
        if (header & EV3_UART_MSG_TYPE_MASK) == 0x00: #SYNC, NACK, ACK
            return 1
        size = self.ev3_uart_cmd_size(header)
        size += 2 #header and checksum 
        if ((header & EV3_UART_MSG_TYPE_MASK) == EV3_UART_MSG_TYPE_INFO):
            size = size + 1 #extra command byte
        return size

    def err_invalid_state(self):
        self.synced = False
        self.new_baud_rate = EV3_UART_SPEED_MIN

    def ev3_uart_send_ack(self,data):
        print("ev3_uart_send_ack")
        sleep(EV3_UART_SEND_ACK_DELAY) #sleep 10ms
        print("ev3_uart_send_ack data ", data)
        self.serialport.write(data)

    def uart_handle_rx_data(self):
        #print("uart_handle_rx_data start")
        #self.circ_buf.get_all()
        
        count = self.circ_buf.circ_count()
        print("ready to procee data %d" % count)
        '''
	 * To get in sync with the data stream from the sensor, we look
	 * for a valid TYPE command.
        '''
        while self.synced == False:
            if count < 3 :
                print("data count less than 3, return")
                return
            cmd_list = self.circ_buf.get_data(1)#only get one cmd, get_data help add tail
            cmd = cmd_list[0] 
            count = count -1
            if cmd != (EV3_UART_MSG_TYPE_CMD | EV3_UART_CMD_TYPE):
                continue
            index = self.circ_buf.get_tail() #get tail 
            oneelement = self.circ_buf.get_direct_element(index) #get one byte, not add tail
            if oneelement == 0  or  oneelement > EV3_UART_TYPE_MAX :
                continue
            sensortype = oneelement
            chksum = 0xFF ^ cmd ^ sensortype;
            twoelement = self.circ_buf.get_direct_element(index + 1)# get one byte, treate it as checksum
            #if twoelement is not equal to checksum, continue parse, tail will not add
            if twoelement != chksum :
                continue
            self.type_id = sensortype
            self.circ_buf.set_tail(2)
            self.synced = True
            count -= 2
        print("type is %d " % self.type_id)
        #self.circ_buf.get_all()
        if self.synced == False:
            return

        while count > 0:
            #Sometimes we get 0xFF after switching baud rates, so just ignore it
            element = self.circ_buf.get_element_without_tail()
            print("first element %x " % element)
            if element == 0xFF:
               self.circ_buf.add_tail()
               #fixme it should be move to CirculeBuffer
               if self.circ_buf.tail >= self.circ_buf.size:
                   self.circ_buf.tail = 0
               count = count -1
               continue
            #get message                
            element = self.circ_buf.get_element_without_tail()
            msg_size = self.ev3_uart_msg_size(element)
            #print("msg_size %d" % msg_size)
            if msg_size > EV3_UART_MAX_MESSAGE_SIZE :
                print("header is %x" % element)
                self.last_err = "Bad message size"
                self.err_invalid_state()
                return
            if msg_size > count:
                print("no more data, need read some")
                print("debug left: ",self.circ_buf.get_all())
                break;
						
            message = self.circ_buf.get_message(msg_size)
            print("message ",message)
            count -= msg_size
 
            msg_type = message[0] & EV3_UART_MSG_TYPE_MASK
            cmd = message[0] & EV3_UART_MSG_CMD_MASK
            mode = cmd
            if msg_size > 1:
                cmd2 = message[1]
            else:
                cmd2 = 0 #fix sys message only has 1 byte
            print("msg_type %x cmd %x mode %x cmd2 %x" % (msg_type,cmd,mode,cmd2))
            if msg_size > 1 :
                chksum = 0xFF
                for index in range(msg_size-1):
                    chksum ^= message[index]
                print("chksum : %d , actual %d " % (chksum, message[msg_size -1]))
                #The LEGO EV3 color sensor sends bad checksums for RGB-RAW data (mode 4)
                #The check here could be improved if someone can find a pattern.
                if chksum != message[msg_size - 1] and self.type_id != EV3_UART_TYPE_ID_COLOR and message[0] != 0xDC:
                    self.last_err = "Bad checksum."
                    if self.info_done:
                        print("Bad checksum info_done continue")
                        count = self.circ_buf.circ_cnt()
                        continue
                    else:
                        print("info done is false, bad check sum")
                        self.err_invalid_state()
                        return
                elif chksum != message[msg_size - 1] and self.type_id != EV3_UART_TYPE_ID_COLOR:
                    print("bad checksum ,just eat this message")
                    continue
            if msg_type == EV3_UART_MSG_TYPE_SYS:
                if cmd == EV3_UART_SYS_SYNC:
                    if (msg_size > 1) and ((cmd ^ cmd2) == 0xFF):
                        msg_size = msg_size + 1
                elif cmd == EV3_UART_SYS_ACK:
                    if self.num_modes == 0:
                        self.last_err = "Received ACK before all mode INFO."
                        self.err_invalid_state()
                        return
                    if (self.info_flags & EV3_UART_INFO_FLAG_REQUIRED) != EV3_UART_INFO_FLAG_REQUIRED:
                        print("did not receive all required info")
                        self.last_err = "Did not receive all required INFO."
                        self.err_invalid_state()
                        return
                    #fixme start another delay thread to send_ack_work
                    ret = self.serialport.write(bytes([EV3_UART_SYS_ACK]))
                    self.serialport.flush()
                    #send_thread = Thread(target=self.ev3_uart_send_ack,args=(EV3_UART_SYS_ACK,))
                    #send_thread.start()
                    print("send ack to sensor")
                    print("write %d bytes to sensor" % ret)
                    sleep(0.01)#sleep 10ms
                    self.serialport.baudrate = EV3_UART_SPEED_MID
                    print("change baudrate new baudrate %d " % self.serialport.baudrate) 
                    self.info_done = True
                    print('all data pase\033[1;35m info done \033[0m!')
                    return
                else:
                    pass
            elif msg_type == EV3_UART_MSG_TYPE_CMD:
                if cmd == EV3_UART_CMD_MODES:
                    #if (self.info_flags & EV3_UART_INFO_BIT_CMD_MODES) == EV3_UART_INFO_BIT_CMD_MODES:
                    #    self.last_err = "Received duplicate modes INFO."
                    #    self.err_invalid_state()
                    #    return
                    self.info_flags |= EV3_UART_INFO_BIT_CMD_MODES
                    if cmd2 > EV3_UART_MODE_MAX:
                        self.last_err = "Number of modes is out of range."
                        self.err_invalid_state()
                        return
                    self.num_modes = cmd2 + 1
                    if msg_size > 3:
                        self.num_view_modes = message[2] + 1
                    else:
                        self.num_view_modes = self.num_modes
                    print("num_modes: %d, num_view_modes:%d " % (self.num_modes,self.num_view_modes))
                elif cmd == EV3_UART_CMD_SPEED:
                    #if (self.info_flags & EV3_UART_INFO_BIT_CMD_SPEED) == EV3_UART_INFO_BIT_CMD_SPEED:
                    #    self.last_err = "Received duplicate speed INFO."
                    #    self.err_invalid_state()
                    #    return    
                    self.info_flags |= EV3_UART_INFO_BIT_CMD_SPEED
                    #there are 4 bytes to repsent speed, it is big endian .
                    speed = (message[1] & 0xFF) | (message[2] & 0xFF )<<8 | (message[3]&0xFF)<<16 | (message[4]&0xFF)<<24
                    print("new baud rate %d " % speed)
                    if speed < EV3_UART_SPEED_MIN or speed > EV3_UART_SPEED_MAX:
                        self.last_err = "Speed is out of range."
                        self.err_invalid_state()
                        return
                else:
                    self.last_err = "Unknown command."
                    self.err_invalid_state()
                    return
            elif msg_type == EV3_UART_MSG_TYPE_INFO:
                if cmd2 == EV3_UART_INFO_NAME:
                    print("cmd2 is EV3_UART_INFO_NAME")
                    self.info_flags &= ~EV3_UART_INFO_FLAG_ALL_INFO
                    #if (message[2] < 'A') or (message[2] > 'z'):
                    #message include int, use ascii to compare
                    if (message[2] < 65) or (message[2] > 122):
                        print("sensor name is not right")
                        self.last_err = "Invalid name INFO."
                        self.err_invalid_state()
                        return
                    self.sensor_name = message[2:(msg_size-1)]
                    name = []
                    for i in self.sensor_name:
                        if i != 0:
                            name.append(chr(i))
                    print("sensor name:", "".join(name))
                    self.sensor_mode = mode
                    self.info_flags |= EV3_UART_INFO_FLAG_INFO_NAME
                elif cmd2 == EV3_UART_INFO_RAW:
                    print("parse info message, cmd2 is EV3_UART_INFO_RAW")
                    print("mode is %d " % mode)
                    print("sensor_mode is %d " % self.sensor_mode)
                    if self.sensor_mode != mode:
                        self.last_err = "Received INFO for incorrect mode."
                        self.err_invalid_state()
                        return
                    #if (self.info_flags & EV3_UART_INFO_BIT_INFO_RAW) != EV3_UART_INFO_BIT_INFO_RAW:
                        #self.last_err = "Received duplicate raw scaling INFO."
                        #self.err_invalid_state()
                        #return
                    self.info_flags |= EV3_UART_INFO_BIT_INFO_RAW
                    #fixme treate it as big endian
                    self.raw_min = (message[2] & 0xFF) | (message[3] & 0xFF )<<8 | (message[4]&0xFF)<<16 | (message[5]&0xFF)<<24
                    self.raw_max = (message[6] & 0xFF) | (message[7] & 0xFF )<<8 | (message[8]&0xFF)<<16 | (message[9]&0xFF)<<24
                    print("raw_min %08x raw_max %08x" % (self.raw_min,self.raw_max))
                elif cmd2 == EV3_UART_INFO_PCT:
                    if self.sensor_mode != mode:
                        self.last_err = "Received INFO for incorrect mode."
                        self.err_invalid_state()
                        return
                    #if (self.info_flags & EV3_UART_INFO_BIT_INFO_PCT) != EV3_UART_INFO_BIT_INFO_PCT:
                    #    self.last_err = "Received duplicate percent scaling INFO."
                    #    self.err_invalid_state()
                    #    return
                    self.info_lags |= EV3_UART_INFO_BIT_INFO_PCT
                    #fixme treate it as big endian
                    self.pct_min = (message[2] & 0xFF) | (message[3] & 0xFF )<<8 | (message[4]&0xFF)<<16 | (message[5]&0xFF)<<24
                    self.pct_max = (message[6] & 0xFF) | (message[7] & 0xFF )<<8 | (message[8]&0xFF)<<16 | (message[9]&0xFF)<<24
                    print("pct_min %08x pct_max %08x" % (self.pct_min,self.pct_max))
                elif cmd2 == EV3_UART_INFO_SI:
                    if self.sensor_mode != mode:
                        self.last_err = "Received INFO for incorrect mode."
                        self.err_invalid_state()
                        return
                    #if (self.info_flags & EV3_UART_INFO_BIT_INFO_SI) != EV3_UART_INFO_BIT_INFO_SI:
                    #    self.last_err = "Received duplicate SI scaling INFO."
                    #    self.err_invalid_state()
                    #    return
                    self.info_flags |= EV3_UART_INFO_BIT_INFO_SI

                    #fixme treate it as big endian
                    self.si_min = (message[2] & 0xFF) | (message[3] & 0xFF )<<8 | (message[4]&0xFF)<<16 | (message[5]&0xFF)<<24
                    self.si_max = (message[6] & 0xFF) | (message[7] & 0xFF )<<8 | (message[8]&0xFF)<<16 | (message[9]&0xFF)<<24
                    print("si_min %08x si_max %08x" % (self.si_min,self.si_max))
                elif cmd2 == EV3_UART_INFO_UNITS:
                    if self.sensor_mode != mode:
                        self.last_err = "Received INFO for incorrect mode."
                        self.err_invalid_state()
                        return
                    #if (self.info_flags & EV3_UART_INFO_BIT_INFO_UNITS) != EV3_UART_INFO_BIT_INFO_UNITS:
                    #    self.last_err = "Received duplicate SI units INFO."
                    #    self.err_invalid_state()
                    #    return
                    self.info_flags |= EV3_UART_INFO_BIT_INFO_UNITS
                    self.units = message[2:msg_size-1]
                    print("units %s", self.units)
                elif cmd2 == EV3_UART_INFO_FORMAT:
                    if self.sensor_mode != mode:
                        self.last_err = "Received INFO for incorrect mode."
                        self.err_invalid_state()
                        return
                    #if (self.info_flags & EV3_UART_INFO_BIT_INFO_FORMAT) != EV3_UART_INFO_BIT_INFO_FORMAT:
                    #    self.last_err = "Received duplicate format INFO."
                    #    self.err_invalid_state()
                    #    return
                    self.info_flags |= EV3_UART_INFO_BIT_INFO_FORMAT
                    self.data_sets = message[2]
                    if (self.data_sets == 0):
                        self.last_err = "Invalid number of data sets."
                        self.err_invalid_state()
                        return
                    if msg_size < 7:
                        self.last_err = "Invalid format message size."
                        self.err_invalid_state()
                        return

                    if (self.info_flags & EV3_UART_INFO_FLAG_REQUIRED) != EV3_UART_INFO_FLAG_REQUIRED:
                        self.last_err = "Did not receive all required INFO."
                        self.err_invalid_state()
                        return
                    data_type = message[3]
                    if data_type == EV3_UART_DATA_8:
                        self.data_type = LEGO_SENSOR_DATA_S8
                    elif data_type == EV3_UART_DATA_16:
                        self.data_type = LEGO_SENSOR_DATA_S16
                    elif data_type == EV3_UART_DATA_32:
                        self.data_type = LEGO_SENSOR_DATA_S32
                    elif data_type == EV3_UART_DATA_FLOAT:
                        self.data_type = LEGO_SENSOR_DATA_FLOAT
                    else:
                        self.last_err = "Invalid data type."
                        self.err_invalid_state()
                        return
                    self.figures = message[4]
                    self.decimals = message[5]
                    #if (self.info_flags & EV3_UART_INFO_FLAG_INFO_RAW) == EV3_UART_INFO_FLAG_INFO_RAW:
                    #    self.raw_min = self.lego_sensor_ftoi(self.raw_min,0)
                    #    self.raw_max = self.lego_sensor_ftoi(self.raw_max,0)
                    #if (self.info_flags & EV3_UART_INFO_FLAG_INFO_PCT) == EV3_UART_INFO_FLAG_INFO_PCT:
                    #    self.pct_min = self.lego_sensor_ftoi(self.pct_min,0)
                    #    self.pct_max = self.lego_sensor_ftoi(self.pct_max,0)
                    #if (self.info_flags & EV3_UART_INFO_FLAG_INFO_SI) == EV3_UART_INFO_FLAG_INFO_SI:
                    #    self.si_min = self.lego_sensor_ftoi(self.si_min,0)
                    #    self.si_max = self.lego_sensor_ftoi(self.si_max,0)
                    #fixme, what does it means
                    #if self.mode > 0:
                    #    self.mode -= 1
            elif msg_type == EV3_UART_MSG_TYPE_DATA:
                print("now data enter")
                if not self.info_done:
                    self.last_err = "Received DATA before INFO was complete."
                    self.err_invalid_state()
                    return
                if mode > EV3_UART_MODE_MAX:
                    self.last_err = "Invalid mode received."
                    self.err_invalid_state()
                    return
                #fixme mode new mode?
                self.raw_data = message[1:msg_size-2]
                self.data_rec = 1
                pass
            else:
                pass

            

    def trans(self , s):
        return "b%s" % ''.join('\\x%.2x' % x for x in s)


    def simulatethread(self):
        print("simulate start")
        self.circ_buf.get_all()
        print("simulate end")
    def run(self):
        while True:
            if self.serialport.inWaiting() > 0:
                data = self.serialport.read(1024)
                data_count = len(data)
                print("read data from serail , count %d" % data_count)
                #print("debug, serial data ", self.trans(data))
                if self.received_thread.isAlive():
                    if data_count > self.circ_buf.circ_space():
                        print("thread is running, but count is too large, nothing to do")
                    else:
                        self.circ_buf.memcpy(data,data_count)
                    print("thread is alive")
                else:
                    if data_count > self.circ_buf.circ_space():
                        print("thread is not running , count is too large, don't copy data")
                    else:
                        #print("debug: ",data)
                        print("thread is not running, just copy data to circle buffer")
                        self.circ_buf.memcpy(data,data_count)
                    self.received_thread = None
                    self.received_thread = Thread(target=self.uart_handle_rx_data)
                    self.received_thread.start()


if __name__ == '__main__':
    sensorport = SensorPort()
    sensorport.run()
            
       
        
