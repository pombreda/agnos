from struct import Struct as _Struct
from datetime import datetime, timedelta
from .utils import HeteroMap
import time


class Packer(object):
    __slots__ = []
    @classmethod
    def get_id(cls):
        return cls.ID
    def pack(self, obj, stream):
        raise NotImplementedError()
    def unpack(self, stream):
        raise NotImplementedError()

class PrimitivePacker(Packer):
    __slots__ = ["id", "struct"]
    def __init__(self, id, fmt):
        self.id = id
        self.struct = _Struct(fmt)
    def get_id(self):
        return self.id
    def pack(self, obj, stream):
        if obj is None:
            obj = 0
        stream.write(self.struct.pack(obj))
    def unpack(self, stream):
        data = stream.read(self.struct.size)
        return self.struct.unpack(data)[0]

Int8 = PrimitivePacker(1, "!b")
Int16 = PrimitivePacker(3, "!h")
Int32 = PrimitivePacker(4, "!l")
Int64 = PrimitivePacker(5, "!q")
Float = PrimitivePacker(6, "!d")

class Bool(Packer):
    ID = 2
    __slots__ = []
    @classmethod
    def pack(cls, obj, stream):
        if obj is None:
            obj = 0
        Int8.pack(int(obj), stream)
    @classmethod
    def unpack(cls, stream):
        return bool(Int8.unpack(stream))

class ObjRef(Packer):
    __slots__ = ["id", "storer", "loader"]
    def __init__(self, id, storer, loader):
        self.id = id
        self.storer = storer
        self.loader = loader
    def get_id(self):
        return self.id
    def pack(self, obj, stream):
        Int64.pack(self.storer(obj), stream)
    def unpack(self, stream):
        return self.loader(Int64.unpack(stream))

class Date(Packer):
    ID = 8
    EPOCH = datetime.fromordinal(1)
    t0 = time.time()
    UTC_DELTA = datetime.fromtimestamp(t0) - datetime.utcfromtimestamp(t0)

    __slots__ = []
    @classmethod
    def pack(cls, obj, stream):
        if isinstance(obj, datetime):
            if obj.tzinfo:
                time_utc = obj - obj.tzinfo.utcoffset(obj)
            else:
                # assume local time and convert to UTC
                time_utc = obj - cls.UTC_DELTA
        elif isinstance(obj, (int, long, float)):
            # assume time_t from unix epoch
            time_utc = datetime.utcfromtimestamp(obj)
        else:
            raise TypeError("cannot encode %r as a datetime object" % (obj,))
        delta = time_utc - cls.EPOCH
        microsecs = (delta.days * 86400 + delta.seconds) * 10**6 + delta.microseconds
        Int64.pack(microsecs, stream)
    @classmethod
    def unpack(cls, stream):
        microsecs = Int64.unpack(stream)
        return cls.EPOCH + timedelta(seconds = microsecs // 10**6, 
            microseconds = microsecs % 10**6)

class Buffer(Packer):
    ID = 7
    __slots__ = []
    @classmethod
    def pack(cls, obj, stream):
        if obj is None:
            obj = []
        Int32.pack(len(obj), stream)
        stream.write(obj)
    @classmethod
    def unpack(cls, stream):
        length = Int32.unpack(stream)
        return stream.read(length)

class Str(Packer):
    ID = 9
    __slots__ = []
    @classmethod
    def pack(cls, obj, stream):
        if obj is None:
            obj = ""
        Buffer.pack(obj.encode("utf-8"), stream)
    @classmethod
    def unpack(cls, stream):
        return Buffer.unpack(stream).decode("utf-8")

class ListOf(Packer):
    __slots__ = ["id", "type"]
    def __init__(self, id, type):
        self.id = id
        self.type = type
    def get_id(self):
        return self.id
    def pack(self, obj, stream):
        Int32.pack(len(obj), stream)
        for item in obj:
            self.type.pack(item, stream)
    def unpack(self, stream):
        length = Int32.unpack(stream)
        obj = []
        for i in xrange(length):
            obj.append(self.type.unpack(stream))
        return obj

list_of_int8 = ListOf(800, Int8)
list_of_bool = ListOf(801, Bool)
list_of_int16 = ListOf(802, Int16)
list_of_int32 = ListOf(803, Int32)
list_of_int64 = ListOf(804, Int64)
list_of_float = ListOf(805, Float)
list_of_buffer = ListOf(806, Buffer)
list_of_date = ListOf(807, Date)
list_of_str = ListOf(808, Str)

class MapOf(Packer):
    __slots__ = ["id", "keytype", "valtype"]
    def __init__(self, id, keytype, valtype):
        self.id = id
        self.keytype = keytype
        self.valtype = valtype
    def get_id(self):
        return self.id
    def pack(self, obj, stream):
        Int32.pack(len(obj), stream)
        for key, val in obj.iteritems():
            self.keytype.pack(key, stream)
            self.valtype.pack(val, stream)
    def unpack(self, stream):
        length = Int32.unpack(stream)
        obj = {}
        for i in xrange(length):
            k = self.keytype.unpack(stream)
            v = self.valtype.unpack(stream)
            obj[k] = v
        return obj

map_of_int32_int32 = MapOf(850, Int32, Int32)
map_of_int32_str = MapOf(851, Int32, Str)
map_of_str_int32 = MapOf(852, Str, Int32)
map_of_str_str = MapOf(853, Str, Str)

class HeteroMapPacker(Packer):
    BUILTIN_PACKERS_MAP = {
        1 : Int8, 2 : Bool, 3 : Int16, 4 : Int32, 5 : Int64,
        6 : Float, 7 : Buffer, 8 : Date, 9 : Str,
        800 : list_of_int8, 801 : list_of_bool, 802 : list_of_int16, 
        803 : list_of_int32, 804 : list_of_int64, 805 : list_of_float, 
        806 : list_of_buffer, 807 : list_of_date, 808 : list_of_str,
        850 : map_of_int32_int32, 851 : map_of_int32_str, 
        852 : map_of_str_int32, 853 : map_of_str_str, 
    }
    
    def __init__(self, id, packers_map):
        self.id = id
        self.packers_map = packers_map
    
    def get_id(self):
        return self.id
    
    def pack(self, obj, stream):
        Int32.pack(len(obj), stream)
        for key, keypacker, val, valpacker in obj.iter_fields():
            Int32.pack(keypacker.get_id(), stream)
            keypacker.pack(key, stream)
            Int32.pack(valpacker.get_id(), stream)
            valpacker.pack(val, stream)
    
    def unpack(self, stream):
        length = Int32.pack(len(obj), stream)
        map = HeteroMap()
        for i in xrange(length):
            keypid = Int32.unpack(stream)
            keypacker = self._get_packer(keypid)
            key = keypacker.unpack(stream)
            valpid = Int32.unpack(stream)
            valpacker = self._get_packer(valpid)
            val = valpacker.unpack(stream)
            map.add(key, keypacker, val, valpacker)
        return obj

    def _get_packer(self, id):
        if id == 998:
            return BuiltinHeteroMapPacker
        elif id in self.BUILTIN_PACKERS_MAP:
            return self.BUILTIN_PACKERS_MAP[id]
        else:
            return self.packers_map[id]


BuiltinHeteroMapPacker = HeteroMapPacker(998, {})


