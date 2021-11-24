# protobuf 到 C# 类型的转换
type_dict = {
    "string": "string",
    "int32": "int",
    "uint32": "uint",
    "int64": "long",
    "uint64": "ulong",
    "bool": "bool",
    "float32": "float",
    "float64": "double",
    "bytes": "byte[]",
    "enum": "int",
}

# C# 类型到Any的转换
type_to_any = {
    "string": "string",
    "int": "int32",
    "uint": "int32",
    "long": "int64",
    "ulong": "int64",
    "bool": "bool",
    "float": "float32",
    "double": "float64",
    "byte[]": "bytes",
}

type_default_value = {
    "string": '""',
    "int32": "0",
    "uint32": "0",
    "int64": "0",
    "uint64": "0",
    "bool": "false",
    "float32": "0",
    "float64": "0",
    "bytes": "new byte[0]",
    "enum": "0",
}


