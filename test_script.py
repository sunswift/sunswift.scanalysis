DEF_DATAACQUIRELENGTH=60
DEF_CHUNKSEPERATOR='C' 
DEF_CHUNKSEPERATORDIGIT=ord(DEF_CHUNKSEPERATOR)
DEF_CHUNKLENGTH=15
DEF_CHECKSUMBYTEINDEX=DEF_CHUNKLENGTH-1 #Last byte in chunk/packet is index

# A serial data stream is composed of multiple chunks of serial data
# For e.g. C-------14 bytes-------C-------14 bytes-------C-------14 bytes------- ..., where C-------14 bytes------- is a single serial data chunk
class SerialDataStream:

    openedSerialPort=0 
    openedSerialPortData=''
    charsToRemove=[]
    serialPortDataLength = 0   

    #Set data source - serial port
    def __init__(self):
        #self.openedSerialPort=serialPort
        self.openedSerialPortData='Cdddddddddddd{+CabcdefgCabcdeCfghCabcdefghijklCabcdefgr'
        self.removeChars()
        self.updateSerialPortDataLength()

    #Get new port data
    def getNewPortData(self, serialPortDataLength=DEF_DATAACQUIRELENGTH):
        #openedSerialPortData=serial.read(serialPortDataLength)
        self.openedSerialPortData='defCabcdefgC\\ab//cdeCfghCabcdefghijklCabcdefgr'
        self.removeChars() 
        self.updateSerialPortDataLength()
    
    #remove any characters not required 
    def removeChars(self):
        for char in self.charsToRemove:
            #print("b:" + char + ":" + self.openedSerialPortData)
            self.openedSerialPortData=self.openedSerialPortData.replace(char, '')
            #print("a:" + char + ":" + self.openedSerialPortData)
            
    #Get the last piece of the chunk from the previous port data and 
    #combine with this
    def getNextPortData(self):        
        lastChunk=self.getLastChunkData()        
        self.getNewPortData()
        self.openedSerialPortData=lastChunk.dataChunk+self.openedSerialPortData
        self.removeChars() 
        self.updateSerialPortDataLength()

    #Get length of data in the serial data
    def updateSerialPortDataLength(self):
        self.serialPortDataLength = len(self.openedSerialPortData)
 
    #Get the data in the last chunk
    def getLastChunkData(self):
        lastChunkStartIndex= self.openedSerialPortData.rfind(DEF_CHUNKSEPERATOR)    
        return SerialDataChunk(self.openedSerialPortData[lastChunkStartIndex:])

    #Get the chunks except last chunk if incomplete. To be processed in next iteration
    def getChunksExceptIncompleteLastChunk(self):
        chunksDataList=self.openedSerialPortData.split(DEF_CHUNKSEPERATOR)         
        numChunks=len(chunksDataList)
        
        #transform to serial data chunks. Split creates empty strings if DEF_SEPERATOR is in beginning. We do not want that.
        chunksList=[]
        for dataList in chunksDataList:
            if(dataList != ''):
                chunksList.append(SerialDataChunk(dataList))
            else:
                numChunks=numChunks-1

        #remove last chunk, if incomplete from testing here and append when next serial port data received
        numCompleteChunks=numChunks
        if(chunksList[numChunks-1].isChunkIncomplete()):
            numCompleteChunks=numChunks-1           

        chunksList=chunksList[:numCompleteChunks]        

        #Reappend initial DEF_CHUNKSEPERATOR
        for i in range(0, numCompleteChunks):
            chunksList[i].dataChunk = DEF_CHUNKSEPERATOR + chunksList[i].dataChunk
        return chunksList        

# A smaller chunk of the serial data
class SerialDataChunk:
    dataChunk=''
    chunkLength=0

    def __init__(self, dataChunk):
        self.chunkLength=len(dataChunk)
        self.dataChunk = dataChunk

    #Is Last Chunk incomplete? If yes, prepend to the next stream for processing
    def isChunkIncomplete(self):
        return (self.chunkLength < DEF_CHUNKLENGTH)

    #Chunk valid if it is the right length and also the checksum is correct 
    def isChunkValid(self):
        return (self.__isChunkCorrectLength() & self.__isChecksumCorrect())

    # Print chunk characters    
    def printChunk(self):
        print(self.dataChunk)
        
    #Print characters in hex/digit form
    def printChunkDigit(self):
        self.chunkLength = len(self.dataChunk)
        for i in range(0, self.chunkLength):
            print(ord(self.dataChunk[i]))

    #Get ID of the CAN message received
    def getRXID(self):
        return ord(self.dataChunk[1]) << 24 | ord(self.dataChunk[2]) << 16 | ord(self.dataChunk[3]) << 8 | ord(self.dataChunk[4])

    #Get Data of the CAN message received
    def getRXData(self):
        dataAsDigits=[]
        data = self.dataChunk[5:self.getRXLength()]               
        for byte in data:
            dataAsDigits.append(ord(byte))
        return dataAsDigits

    #Get length of the data in the CAN message 
    def getRXLength(self):
        return ord(self.dataChunk[13])
    
    #Get the checksum of the serialised CAN message - Not the CRC Checksum of CAN
    def __getRXCheckSum(self):
        return ord(self.dataChunk[DEF_CHECKSUMBYTEINDEX])

    #checksum match? Check if the length is correct before 
    #applying 
    def __isChecksumCorrect(self):
        calculatedChksum=0;
        calculatedChksum=self.__getChecksum();    
        
        #Check the calculated checksum against packet checksum 
        if(calculatedChksum == -1): 
            #Packet is too short in length
            return False
        elif(calculatedChksum == self.__getRXCheckSum()):
            return True
        else:
            return False
    
    #calculate checksum
    def __getChecksum(self):
        chksum=0;
        try: 
            #Calculate checksum
            for i in range(1, DEF_CHECKSUMBYTEINDEX):
                chksum = chksum + ord(self.dataChunk[i])                        
                print(self.dataChunk[i] + ' ' + ' %d' %ord(self.dataChunk[i]))
                if chksum > 255:
                    chksum -= 256; 
            return chksum
        except(IndexError):
            return -1

    def __isChunkCorrectLength(self):
        self.chunkLength = len(self.dataChunk)
        return (self.chunkLength == DEF_CHUNKLENGTH) 

o=SerialDataStream()
chunksList=o.getChunksExceptIncompleteLastChunk()
for item in chunksList:
    item.printChunk()
print(chunksList[0].isChunkValid())
print(chunksList[0].getRXID())
print(chunksList[0].getRXData())
print(chunksList[0].getRXLength())

print('-------')
o.getNextPortData()
chunksList=o.getChunksExceptIncompleteLastChunk()
for item in chunksList:
    item.printChunk()

#print('-------')
#o.getNextPortData()
#chunksList=o.getChunksExceptIncompleteLastChunk()
#for item in chunksList:
#    item.printChunk()

