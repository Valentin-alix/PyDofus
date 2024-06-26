import base64
import math
import struct
from zlib import decompress


class ByteArray(bytearray):
    INT_SIZE: int = 32

    SHORT_SIZE: int = 16

    SHORT_MIN_VALUE: int = -32768

    SHORT_MAX_VALUE: int = 32767

    UNSIGNED_SHORT_MAX_VALUE: int = 65536

    CHUNK_BIT_SIZE: int = 7

    MAX_ENCODING_LENGTH: int = math.ceil(INT_SIZE / CHUNK_BIT_SIZE)

    MASK_10000000: int = 128

    MASK_01111111: int = 127

    def __init__(self, *args, **kwrgs):
        super().__init__(*args, **kwrgs)
        self.position = 0

    @classmethod
    def from_bytes(cls, b: bytes) -> "ByteArray":
        r = cls()
        r.writeByteArray(b)
        r.position = 0
        return r

    @classmethod
    def from_int8Array(cls, arr: list[int]):
        r = cls()
        for i in arr:
            r.writeByte(i, signed=True)
        r.position = 0
        return r

    def __add__(self, b) -> "ByteArray":
        return ByteArray(super().__add__(b))

    @property
    def length(self):
        return len(self)

    @length.setter
    def length(self, val):
        del self[val:]

    def __str__(self):
        return base64.b64encode(self).decode("utf")

    def remaining(self):
        return len(self) - self.position

    def hex(self):
        return self.hex()

    @classmethod
    def fromhex(cls, hex):
        return cls(bytearray.fromhex(hex))

    def verif(self, l):
        if len(self) < self.position + l:
            raise IndexError(self.position, l, len(self))

    def read(self, l):
        if l == 0:
            return ByteArray()
        self.verif(l)
        pos = self.position
        self.position += l
        return ByteArray(self[pos : pos + l])

    def write(self, l):
        self += l

    def uncompress(self):
        self = bytearray(decompress(self))

    def readBoolean(self) -> bool:
        ans = self.read(1)
        r = struct.unpack("?", ans)[0]
        return r

    def writeBoolean(self, b):
        if b:
            self += b"\x01"
        else:
            self += b"\x00"

    def readByte(self):
        return int.from_bytes(self.read(1), "big", signed=True)

    def writeByte(self, b, signed=True):
        try:
            self += b.to_bytes(1, "big", signed=signed)
        except OverflowError:
            self += b.to_bytes(1, "big", signed=not signed)

    def readByteArray(self):
        lon = self.readVarInt()
        return self.read(lon)

    def readDouble(self):
        return struct.unpack("!d", self.read(8))[0]

    def writeDouble(self, d):
        self += struct.pack("!d", d)

    def readFloat(self):
        return struct.unpack("!f", self.read(4))[0]

    def writeFloat(self, f):
        self += struct.pack("!f", f)

    def readInt(self):
        return int.from_bytes(self.read(4), "big", signed=True)

    def writeInt(self, i):
        self += i.to_bytes(4, "big", signed=True)

    def readShort(self):
        return int.from_bytes(self.read(2), "big", signed=True)

    def writeShort(self, s):
        self += s.to_bytes(2, "big", signed=True)

    def readUTF(self):
        lon = self.readUnsignedShort()
        return self.read(lon).decode()

    def writeUTF(self, ch: str):
        dat = ch.encode()
        self.writeUnsignedShort(len(dat))
        self += dat

    def readUnsignedByte(self):
        return int.from_bytes(self.read(1), "big")

    def writeUnsignedByte(self, b):
        self += b.to_bytes(1, "big")

    def readUnsignedInt(self):
        return int.from_bytes(self.read(4), "big")

    def writeUnsignedInt(self, ui):
        self += ui.to_bytes(4, "big")

    def readUnsignedShort(self):
        return int.from_bytes(self.read(2), "big")

    def writeUnsignedShort(self, us):
        self += us.to_bytes(2, "big")

    def readBytes(self, offset=0, len=None):
        self.position += offset
        return self.read(len)

    def readUTFBytes(self, len):
        return self.read(len).decode()

    def _writeVar(self, i):
        if not i:
            self.writeUnsignedByte(0)
        while i:
            b = i & 0b01111111
            i >>= 7
            if i:
                b |= 0b10000000
            self.writeUnsignedByte(b)

    def readVarInt(self):
        shift = 0
        result = 0
        while True:
            i = self.readByte()
            result |= (i & 0x7F) << shift
            shift += 7
            if not (i & 0x80):
                break
        if result > 2147483647:
            result = result - 4294967295 - 1
        return result

    def writeVarInt(self, i):
        assert i.bit_length() <= 32
        self._writeVar(i)

    def readVarUhInt(self):
        return self.readVarInt()

    def writeVarUhInt(self, i):
        self.writeVarInt(i)

    def readVarLong(self):
        ans = 0
        for i in range(0, 64, 7):
            b = self.readUnsignedByte()
            ans += (b & 0b01111111) << i
            if not b & 0b10000000:
                return ans
        raise Exception("Too much data")

    def writeVarLong(self, i):
        assert i.bit_length() <= 64
        self._writeVar(i)

    def readVarUhLong(self):
        return self.readVarLong()

    def writeVarUhLong(self, i):
        self.writeVarLong(i)

    def readVarShort(self):
        b = 0
        value = 0
        offset = 0
        hasNext = False
        while offset < self.SHORT_SIZE:
            b = self.readByte()
            hasNext = (b & self.MASK_10000000) == self.MASK_10000000
            if offset > 0:
                value += (b & self.MASK_01111111) << offset
            else:
                value += b & self.MASK_01111111
            offset += self.CHUNK_BIT_SIZE
            if not hasNext:
                if value > self.SHORT_MAX_VALUE:
                    value -= self.UNSIGNED_SHORT_MAX_VALUE
                return value
        raise ValueError("Too much data")

    def writeVarShort(self, i):
        assert i.bit_length() <= 16
        self._writeVar(i)

    def readVarUhShort(self) -> int:
        return self.readVarShort()

    def writeVarUhShort(self, i):
        self.writeVarShort(i)

    def to_int8Arr(ba: bytearray) -> list[int]:
        ret = []
        for i in range(len(ba)):
            ret.append(int.from_bytes(ba[i : i + 1], "big", signed=True))
        return ret

    @staticmethod
    def from_int8Arr(int_arr: list[int]) -> bytearray:
        res = ByteArray()
        for nbr in int_arr:
            res += nbr.to_bytes(1, "big", signed=True)
        return res

    def writeByteArray(self, ba, offset=0, size=None):
        if not size:
            size = len(ba)
        if self.position + size < len(self):
            self[self.position : self.position + size] = ba[offset : offset + size]
        else:
            chunck_size = len(self) - self.position
            self[self.position :] = ba[offset : offset + chunck_size]
            self += ba[offset + chunck_size : offset + size]
        self.position += size

    def trim(self):
        del self[: self.position]
        self.position = 0
