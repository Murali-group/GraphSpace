from datetime import datetime

from enum import Enum


class DataType(Enum):
    BOOL = 1
    LONG = 2
    DOUBLE = 3
    STRING = 4
    DICT = 5
    DATETIME = 6
    GEOPOINT = 7
    UNKNOWN = 8

    def __str__(self):
        return {
            DataType.BOOL: "bool",
            DataType.LONG: "long",
            DataType.DOUBLE: "double",
            DataType.STRING: "string",
            DataType.DICT: "object",
            DataType.DATETIME: "datetime",
            DataType.GEOPOINT: "geopoint",
            DataType.UNKNOWN: ""
        }.get(self, "")

    @staticmethod
    def equatable():
        return [DataType.BOOL, DataType.LONG, DataType.DOUBLE, DataType.STRING, DataType.UNKNOWN]

    @staticmethod
    def comparable():
        return [DataType.LONG, DataType.DOUBLE, DataType.DATETIME]

    @staticmethod
    def baseTypes():
        return [DataType.BOOL, DataType.LONG, DataType.DOUBLE, DataType.STRING, DataType.DATETIME]

    @staticmethod
    def fromStr(typeStr):
        return {
            "bool": DataType.BOOL,
            "long": DataType.LONG,
            "double": DataType.DOUBLE,
            "string": DataType.STRING,
            "object": DataType.DICT,
            "datetime": DataType.DATETIME,
            "geopoint": DataType.GEOPOINT,
            "": DataType.UNKNOWN
        }.get(typeStr, DataType.UNKNOWN)

    def prefix(self):
        return "" if self == DataType.UNKNOWN else str(self) + "_"

    @staticmethod
    def dateToStr(value, data_type):
        return value.isoformat() if data_type == DataType.DATETIME else value

    @staticmethod
    def isGeoPoint(value):
        return len(value.keys()) == 2 and 'lat' in value and 'lon' in value

    @staticmethod
    def typeForDictValue(value):
        if DataType.isGeoPoint(value):
            return DataType.GEOPOINT
        return DataType.DICT

    @staticmethod
    def forValue(value):
        """
        Dict and list handled separately because dict creation tries to execute their handlers while initialization
        """
        try:
            if isinstance(value, dict):
                return DataType.typeForDictValue(value)
            elif isinstance(value, list):
                return DataType.forValue(value[0])
            else:
                return {
                    bool: DataType.BOOL,
                    int: DataType.DOUBLE,
                    long: DataType.DOUBLE,
                    float: DataType.DOUBLE,
                    str: DataType.STRING,
                    unicode: DataType.STRING,
                    datetime: DataType.DATETIME
                }[type(value)]
        except Exception:
            return DataType.UNKNOWN

    @staticmethod
    def attributeNameFromKey(key):
        for value_type in DataType:
            if key.startswith(value_type.prefix()):
                return key[len(value_type.prefix()):]
        return key

    @staticmethod
    def dataTypeFromKey(key):
        for value_type in DataType:
            if key.startswith(value_type.prefix()):
                return value_type
        return DataType.UNKNOWN

    @staticmethod
    def reverseMapDictionaryKeys(datapoint_dict):
        if datapoint_dict:
            return {DataType.attributeNameFromKey(k): v for k, v in datapoint_dict.items()}
        return datapoint_dict