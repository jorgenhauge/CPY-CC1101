from digitalio import DigitalInOut
import board
import busio
import time
from adafruit_bus_device.spi_device import SPIDevice
import registers as regs


def writeSingleByte(address, byte_data):
    databuffer = bytearray([regs.WRITE_SINGLE_BYTE | address, byte_data])
    with device as d:
        d.write(databuffer)


def readSingleByte(address):
    databuffer = bytearray([regs.READ_SINGLE_BYTE | address, 0x00])

    with device as d:
        d.write(databuffer, end=1)
        d.readinto(databuffer, end=2)
    return databuffer[0]


def readBurst(start_address, length):
    databuffer = []
    ret = bytearray(length + 1)

    for x in range(length + 1):
        addr = (start_address + (x * 8)) | regs.READ_BURST
        databuffer.append(addr)

    with device as d:
        d.write_readinto(bytearray(databuffer), ret)
    return ret


def writeBurst(address, data):
    data.insert(0, (regs.WRITE_BURST | address))
    with device as d:
        d.write(bytearray(data))


def strobe(address):
    databuffer = bytearray([address, 0x00])
    with device as d:
        d.write(databuffer, end=1)
        d.readinto(databuffer, end=2)
    return databuffer


mySPI = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.D9)
gdo0 = DigitalInOut(board.D10)
device = SPIDevice(mySPI, cs, baudrate=50000, polarity=0, phase=0)
strobe(regs.SRES)

writeSingleByte(regs.IOCFG2, 0x29)
writeSingleByte(regs.IOCFG1, 0x2E)
writeSingleByte(regs.IOCFG0, 0x06)
writeSingleByte(regs.FIFOTHR, 0x47)
writeSingleByte(regs.SYNC1, 0x66)
writeSingleByte(regs.SYNC0, 0x6A)
writeSingleByte(regs.PKTLEN, 0x15)
writeSingleByte(regs.PKTCTRL1, 0x04)
writeSingleByte(regs.PKTCTRL0, 0x04)
writeSingleByte(regs.ADDR, 0x00)
writeSingleByte(regs.CHANNR, 0x00)
writeSingleByte(regs.FSCTRL1, 0x06)
writeSingleByte(regs.FSCTRL0, 0x00)
writeSingleByte(
    regs.FREQ2, 0x10
)  # . 0x10 <- 434.4 (theory) # 0x10 <- exactly on 434.4 (measured) .#
writeSingleByte(
    regs.FREQ1, 0xB5
)  # . 0xB5 <- 434.4 (theory) # 0xB5 <- exactly on 434.4 (measured) .#
writeSingleByte(
    regs.FREQ0, 0xA9
)  # . 0x2B <- 434.4 (theory) # 0xA9 <- exactly on 434.4 (measured) .#
writeSingleByte(regs.MDMCFG4, 0x87)
writeSingleByte(regs.MDMCFG3, 0x10)
writeSingleByte(regs.MDMCFG2, 0x32)
writeSingleByte(regs.MDMCFG1, 0x22)
writeSingleByte(regs.MDMCFG0, 0xF8)
writeSingleByte(regs.DEVIATN, 0x00)
writeSingleByte(regs.MCSM2, 0x07)
writeSingleByte(regs.MCSM1, 0x30)
writeSingleByte(regs.MCSM0, 0x18)
writeSingleByte(regs.FOCCFG, 0x16)
writeSingleByte(regs.BSCFG, 0x6C)
writeSingleByte(regs.AGCCTRL2, 0x04)
writeSingleByte(regs.AGCCTRL1, 0x00)
writeSingleByte(regs.AGCCTRL0, 0x91)
writeSingleByte(regs.WOREVT1, 0x87)
writeSingleByte(regs.WOREVT0, 0x6B)
writeSingleByte(regs.WORCTRL, 0xFB)
writeSingleByte(regs.FREND1, 0x56)
writeSingleByte(regs.FREND0, 0x11)
writeSingleByte(regs.FSCAL3, 0xE9)
writeSingleByte(regs.FSCAL2, 0x2A)
writeSingleByte(regs.FSCAL1, 0x00)
writeSingleByte(regs.FSCAL0, 0x1F)
writeSingleByte(regs.RCCTRL1, 0x41)
writeSingleByte(regs.RCCTRL0, 0x00)
writeSingleByte(regs.FSTEST, 0x59)
writeSingleByte(regs.PTEST, 0x7F)
writeSingleByte(regs.AGCTEST, 0x3F)
writeSingleByte(regs.TEST2, 0x81)
writeSingleByte(regs.TEST1, 0x35)
writeSingleByte(regs.TEST0, 0x09)

writeBurst(regs.PATABLE, regs.PA_TABLE)

strobe(regs.SRX)

print("waiting for data")

while not gdo0.value:
    pass
# detected rising edge

while gdo0.value:
    pass
# detected falling edge

data_len = 0x17  # PKTLEN is programmed to 0x17, add 2 status bytes
data = readBurst(regs.RXFIFO, data_len)
dataStr = "".join(list(map(lambda x: "{0:0>8}".format(x[2:]), list(map(bin, data)))))
newStr = dataStr[8:]
print("Data: ", newStr)
