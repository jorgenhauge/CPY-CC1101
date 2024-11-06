from digitalio import DigitalInOut
import board
import busio
import time
import math
from adafruit_bus_device.spi_device import SPIDevice
from machine import Pin, SPI

import registers as regs


class CC1101:
    def __init__(
        self, spi, cs, gdo0, baudrate, frequency, syncword, offset=0
    ):  # optional frequency offset in Hz
        self.gdo0 = gdo0
        self.device = SPIDevice(spi, cs, baudrate=baudrate, polarity=0, phase=0)
        self.strobe(regs.SRES)  # reset

        self.setFrequency(frequency, offset)

        assert len(syncword) == 4
        self.writeSingleByte(regs.SYNC1, int(syncword[:2], 16))
        self.writeSingleByte(regs.SYNC0, int(syncword[2:], 16))

        self.writeBurst(regs.PATABLE, regs.PA_TABLE)
        self.strobe(regs.SFTX)  # flush TX FIFO
        self.strobe(regs.SFRX)  # flush RX FIFO

    def setFrequency(self, frequency, offset):
        frequency_hex = hex(int(frequency * (pow(2, 16) / 26000000) + offset))

        byte2 = (int(frequency_hex, 16) >> 16) & 0xFF
        byte1 = (int(frequency_hex) >> 8) & 0xFF
        byte0 = int(frequency_hex) & 0xFF
        self.writeSingleByte(regs.FREQ2, byte2)
        self.writeSingleByte(regs.FREQ1, byte1)
        self.writeSingleByte(regs.FREQ0, byte0)

    def getSampleRate(self, freq_xosc=26000000):
        drate_mantissa = self.readSingleByte(regs.MDMCFG3)
        drate_exponent = self.readSingleByte(regs.MDMCFG4) & 0xF
        sample_rate = (256 + drate_mantissa) * pow(2, drate_exponent - 28) * freq_xosc
        return sample_rate

    def setSampleRate_4000(self):
        self.writeSingleByte(regs.MDMCFG3, 0x43)

    # TODO: Implement set sample rate function
    def setSampleRate(self):
        pass

    def setupRX(self):
        self.writeSingleByte(regs.IOCFG2, 0x29)
        self.writeSingleByte(regs.IOCFG1, 0x2E)
        self.writeSingleByte(regs.IOCFG0, 0x06)
        self.writeSingleByte(regs.FIFOTHR, 0x47)
        self.writeSingleByte(regs.PKTCTRL1, 0x00)
        self.writeSingleByte(regs.PKTCTRL0, 0x00)
        self.writeSingleByte(regs.ADDR, 0x00)
        self.writeSingleByte(regs.CHANNR, 0x00)
        self.writeSingleByte(regs.FSCTRL1, 0x08)
        self.writeSingleByte(regs.FSCTRL0, 0x00)
        self.writeSingleByte(regs.MDMCFG4, 0xF7)
        self.writeSingleByte(regs.MDMCFG3, 0x10)
        self.writeSingleByte(regs.MDMCFG2, 0x32)
        self.writeSingleByte(regs.MDMCFG1, 0x22)
        self.writeSingleByte(regs.MDMCFG0, 0xF8)
        self.writeSingleByte(regs.DEVIATN, 0x00)
        self.writeSingleByte(regs.MCSM2, 0x07)
        self.writeSingleByte(regs.MCSM1, 0x30)
        self.writeSingleByte(regs.MCSM0, 0x18)
        self.writeSingleByte(regs.FOCCFG, 0x16)
        self.writeSingleByte(regs.BSCFG, 0x6C)
        self.writeSingleByte(regs.AGCCTRL2, 0x06)
        self.writeSingleByte(regs.AGCCTRL1, 0x00)
        self.writeSingleByte(regs.AGCCTRL0, 0x95)
        self.writeSingleByte(regs.WOREVT1, 0x87)
        self.writeSingleByte(regs.WOREVT0, 0x6B)
        self.writeSingleByte(regs.WORCTRL, 0xFB)
        self.writeSingleByte(regs.FREND1, 0xB6)
        self.writeSingleByte(regs.FREND0, 0x11)
        self.writeSingleByte(regs.FSCAL3, 0xE9)
        self.writeSingleByte(regs.FSCAL2, 0x2A)
        self.writeSingleByte(regs.FSCAL1, 0x00)
        self.writeSingleByte(regs.FSCAL0, 0x1F)
        self.writeSingleByte(regs.RCCTRL1, 0x41)
        self.writeSingleByte(regs.RCCTRL0, 0x00)
        self.writeSingleByte(regs.FSTEST, 0x59)
        self.writeSingleByte(regs.PTEST, 0x7F)
        self.writeSingleByte(regs.AGCTEST, 0x3F)
        self.writeSingleByte(regs.TEST2, 0x81)
        self.writeSingleByte(regs.TEST1, 0x35)
        self.writeSingleByte(regs.TEST0, 0x09)

    def setupTX(self):
        self.writeSingleByte(regs.IOCFG2, 0x29)
        self.writeSingleByte(regs.IOCFG1, 0x2E)
        self.writeSingleByte(regs.IOCFG0, 0x06)
        self.writeSingleByte(regs.FIFOTHR, 0x47)
        self.writeSingleByte(regs.PKTCTRL1, 0x00)
        self.writeSingleByte(regs.PKTCTRL0, 0x00)
        self.writeSingleByte(regs.ADDR, 0x00)
        self.writeSingleByte(regs.CHANNR, 0x00)
        self.writeSingleByte(regs.FSCTRL1, 0x06)
        self.writeSingleByte(regs.FSCTRL0, 0x00)
        self.writeSingleByte(regs.MDMCFG4, 0xE7)
        self.writeSingleByte(regs.MDMCFG3, 0x10)
        self.writeSingleByte(
            regs.MDMCFG2, 0x30
        )  # . 32 would be 16/16 sync word bits .#
        self.writeSingleByte(regs.MDMCFG1, 0x22)
        self.writeSingleByte(regs.MDMCFG0, 0xF8)
        self.writeSingleByte(regs.DEVIATN, 0x15)
        self.writeSingleByte(regs.MCSM2, 0x07)
        self.writeSingleByte(regs.MCSM1, 0x20)
        self.writeSingleByte(regs.MCSM0, 0x18)
        self.writeSingleByte(regs.FOCCFG, 0x14)
        self.writeSingleByte(regs.BSCFG, 0x6C)
        self.writeSingleByte(regs.AGCCTRL2, 0x03)
        self.writeSingleByte(regs.AGCCTRL1, 0x00)
        self.writeSingleByte(regs.AGCCTRL0, 0x92)
        self.writeSingleByte(regs.WOREVT1, 0x87)
        self.writeSingleByte(regs.WOREVT0, 0x6B)
        self.writeSingleByte(regs.WORCTRL, 0xFB)
        self.writeSingleByte(regs.FREND1, 0x56)
        self.writeSingleByte(regs.FREND0, 0x11)
        self.writeSingleByte(regs.FSCAL3, 0xE9)
        self.writeSingleByte(regs.FSCAL2, 0x2A)
        self.writeSingleByte(regs.FSCAL1, 0x00)
        self.writeSingleByte(regs.FSCAL0, 0x1F)
        self.writeSingleByte(regs.RCCTRL1, 0x41)
        self.writeSingleByte(regs.RCCTRL0, 0x00)
        self.writeSingleByte(regs.FSTEST, 0x59)
        self.writeSingleByte(regs.PTEST, 0x7F)
        self.writeSingleByte(regs.AGCTEST, 0x3F)
        self.writeSingleByte(regs.TEST2, 0x81)
        self.writeSingleByte(regs.TEST1, 0x35)
        self.writeSingleByte(regs.TEST0, 0x0B)

    def writeSingleByte(self, address, byte_data):
        databuffer = bytearray([regs.WRITE_SINGLE_BYTE | address, byte_data])
        with self.device as d:
            d.write(databuffer)

    def readSingleByte(self, address):
        databuffer = bytearray([regs.READ_SINGLE_BYTE | address, 0x00])

        with self.device as d:
            d.write(databuffer, end=1)
            d.readinto(databuffer, end=2)
        return databuffer[0]

    def readBurst(self, start_address, length):
        databuffer = []
        ret = bytearray(length + 1)

        for x in range(length + 1):
            addr = (start_address + (x * 8)) | regs.READ_BURST
            databuffer.append(addr)

        with self.device as d:
            d.write_readinto(bytearray(databuffer), ret)
        return ret

    def writeBurst(self, address, data):
        temp = list(data)
        temp.insert(0, (regs.WRITE_BURST | address))
        with self.device as d:
            d.write(bytearray(temp))

    def strobe(self, address):
        databuffer = bytearray([address, 0x00])
        with self.device as d:
            d.write(databuffer, end=1)
            d.readinto(databuffer, end=2)
        return databuffer

    def setupCheck(self):
        self.strobe(regs.SFRX)
        self.strobe(regs.SRX)
        print("ready to detect data")

    def receiveData(self, length):
        self.writeSingleByte(regs.PKTLEN, length)
        self.strobe(regs.SRX)
        print("waiting for data")

        while not self.gdo0.value:
            pass
        # detected rising edge

        while self.gdo0.value:
            pass
        # detected falling edge

        data_len = length  # +2 # add 2 status bytes
        data = self.readBurst(regs.RXFIFO, data_len)
        dataStr = "".join(
            list(map(lambda x: "{0:0>8}".format(x[2:]), list(map(bin, data))))
        )
        newStr = dataStr[8:]
        print("Data: ", newStr)
        self.strobe(regs.SIDLE)
        while self.readSingleByte(regs.MARCSTATE) != 0x01:
            pass
        self.strobe(regs.SFRX)
        return newStr

    def sendData(self, bitstring, syncword):
        print("TXBYTES before sendData:", self.readSingleByte(regs.TXBYTES))
        paddingLen = math.floor((512 - 16 - len(bitstring)) / 8)  # 16 Bits sync word
        bitstring = (
            paddingLen * "10101010"
            + "{0:0>16}".format(bin(int(syncword, 16))[2:])
            + bitstring
        )

        # print("the bitstring is", len(bitstring), "bits long")

        data = []
        for i in range(0, len(bitstring) / 8):
            data.append(int(bitstring[i * 8 : i * 8 + 8], 2))

        self.writeSingleByte(regs.PKTLEN, len(data))

        self.strobe(regs.SIDLE)
        while (
            self.readSingleByte(regs.MARCSTATE) & 0x1F != 0x01
        ):  # wait for CC to enter idle state
            pass
        self.strobe(regs.SFTX)  # flush TX FIFO
        time.sleep(0.05)

        # print(''.join(list(map(lambda x: "{0:0>8}".format(str(bin(x)[2:])), data))))
        # print("Sending packet of", len(data), "bytes")
        # print("Data in TXFIFO:\n", self.readBurst(TXFIFO, 64), "\nTXBYTES:", self.readSingleByte(TXBYTES))
        self.writeBurst(regs.TXFIFO, data)
        # print("Data in TXFIFO:\n", self.readBurst(TXFIFO, 64), "\nTXBYTES:", self.readSingleByte(TXBYTES))
        self.strobe(regs.STX)

        remaining_bytes = self.readSingleByte(regs.TXBYTES) & 0x7F
        while remaining_bytes != 0:
            time.sleep(0.1)
            print(
                "Waiting until all bytes are transmited, remaining bytes: %d"
                % remaining_bytes
            )
            remaining_bytes = self.readSingleByte(regs.TXBYTES) & 0x7F

        self.strobe(regs.SFTX)
        self.strobe(regs.SFRX)
        time.sleep(0.05)

        if (self.readSingleByte(regs.TXBYTES) & 0x7F) == 0:
            print("Packet sent!\n\n")
            return True

        else:
            print(self.readSingleByte(regs.TXBYTES) & 0x7F)
            return False
