
class CircularBufferBase(object):
    def __init__(self,size):
        """ initialization"""
        self.head = 0
        self.tail = 0
        self._data = []
        self.size = size

    def circ_count(self):
        """return count in buffer"""
        return (self.head - self.tail ) & (self.size -1)

    def circ_space(self):
        """ Return space available, 0..size-1.  We always leave one free char
            as a completely full buffer has head == tail, which is the same as
            empty """
        return (self.tail - (self.head + 1)) & (self.size -1)

    def circ_count_to_end(self):
        """Return count up to the end of the buffer.  Carefully avoid 
           accessing head and tail more than once, so they can change
           underneath us without returning inconsistent results.
        """
        end = self.size - self.tail
        n  = (self.head + end) & (self.size - 1)
        if n < end :
            return n
        else:
            return end
    def circ_space_to_end(self):
        """ Return space available up to the end of the buffer. """
        end = self.size - 1 - self.head
        n = (end + self.tail) & (self.size -1)
        if n <= end:
            return n
        else:
            return end + 1
    def memcpy(self,data,count):
        left_space = self.circ_space_to_end()
        if count > left_space:
            self._data[self.head:] = data[0:left_space]
            self._data[0:(count - left_space)] = data[left_space:count - left_space]
            self.head = count - left_space
        else:
            self._data[self.head:] = data[0:count]
            self.head = self.head + count


    def get_all(self):
        count = self.circ_count()
        for index in range(count):
            cmd = self._data[(self.tail + index) % self.size]
            #if cmd >= 32 and cmd < 127:
                #print("%c " % cmd, end=' ')
            #else:
                #print("0x%02x " % cmd, end=' ')
            print("0x%02x " % cmd, end=' ')
            if (index+1) % 16 == 0:
                print("")
        print("(%d)" % count)

    def get_data(self,count):
        command = []
        for index in range(count):
            cmd = self._data[self.tail]
            command.append(cmd)
            self.tail = self.tail + 1
            if self.tail >= self.size:
                self.tail = 0
        return command
    def get_element_without_tail(self):
        #because get_data already add tail, so it isn't add tail now
        return self._data[(self.tail)]

    def get_direct_element(self,index):
        return self._data[index]

    def get_tail(self):
        return self.tail
 
    def set_tail(self,value):
        for i in range(value):
            self.tail = self.tail + 1
            if self.tail >= self.size:
                self.tail = 0

    def add_tail(self):
        self.tail = (self.tail + 1 ) % self.size

    def get_message(self, msg_size):
        size_to_end = self.circ_count_to_end()
        message = []
        if msg_size > size_to_end :
            for index in range(size_to_end):
                message.append(self._data[self.tail + index])
            for index in range(msg_size - size_to_end):
                message.append(self._data[index])
            self.tail = msg_size - size_to_end
        else:
            for index in range(msg_size):
                message.append(self._data[self.tail + index])
            self.tail = self.tail + msg_size   
            if self.tail >= self.size:
                self.tail = 0
        return message



if __name__ == '__main__':

    print("run test for CircularBufferBase")
    cir = CircularBufferBase(1024)
    print("get real data in buffer %d" % cir.circ_count())
    print("get space in buffer %d" % cir.circ_space())
    print("get count to end %d" % cir.circ_count_to_end())
    print("get space to end %d" % cir.circ_space_to_end())
    d=bytes([1,2,3,4,5,6])
    print("test data: d ", d)
    print("copy d to circular buffer")
    cir.memcpy(d,len(d)) 
    print("debug data")
    cir.get_all()
    print("debug")
    print("get real data in buffer %d" % cir.circ_count())
    print("get space in buffer %d" % cir.circ_space())
    print("get count to end %d" % cir.circ_count_to_end())
    print("get space to end %d" % cir.circ_space_to_end())
    new_data = cir.get_data(2)
    print("get 2 of data ", new_data)
    new_data = cir.get_data(2)
    print("get next 2 of data ", new_data)
    new_data = cir.get_data(2)
    print("get next 2 of data ", new_data)
    print("here data is end")
    new_data = cir.get_data(2)
    print("get next 2 of data ", new_data)





class CircularBuffer(object):
    def __init__(self, size):
        """initialization"""
        self.index= 0
        self.size= size
        self.tail=0
        self._data = []

    def record(self, value):
        """append an element"""
        if len(self._data) == self.size:
            self._data[self.index]= value
        else:
            self._data.append(value)
        self.index= (self.index + 1) % self.size

    def __getitem__(self, key):
        """get element by index like a regular array"""
        if self.tail == self.index:
            return None
        else:
            value = self._data[key]
            self.tail = (self.tail + 1) % self.size
            return value

    def __repr__(self):
        """return string representation"""
        return self._data.__repr__() + ' (' + str(len(self._data))+' items)'

    def get_all(self):
        """return a list of all the elements"""
        return(self._data)

    def memcpy(self, contents):
        for value in contents:
            self.record(value)

