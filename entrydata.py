import json
from enum import Enum
import uuid

__author__ = 'customtea (https://github.com/customtea/)'
__version__ = '1.0.0'


class CodeType(Enum):
    TEXT        = "text"
    CLASS       = "class"
    CLASS_FUNC  = "class_func"
    FUNCTION    = "function"


class CodeEntry():
    def __init__(self, etype: CodeType,filename: str, name:str) -> None:
        self.type = etype
        self.name = name
        self.arg = None
        self.ret = None
        self.bases = None
        self.decorator = None
        self.codes: list[str] = []
        self.filename = filename
        self.uuid = uuid.uuid4(),
    
    def __str__(self) -> str:
        d = {
            "name" : self.name,
            "type" : self.type.value,
        }
        return json.dumps(d)
    
    def json(self) -> str:
        d = {
            "id" : str(self.uuid[0]),
            "filename": self.filename,
            "name" : self.name,
            "codes" :   self.codes,
            "type" : self.type.value,
            "argument"   : self.arg,
            "return"   : self.ret,
            "super"     : self.bases,
            "decorator" : self.decorator,
            
        }
        return d
    
    def set_decorator(self, deco: list[str]):
        if len(deco) < 1:
            self.decorator = None
        else:
            self.decorator = deco
    
    def set_bases(self, bases: list[str]):
        if len(bases) < 1:
            self.bases = None
        else:
            self.bases = bases

    def set_args(self, arg: list[str]):
        if len(arg) < 1:
            self.arg = None
        else:
            self.arg = arg

    def set_return(self, ret: list[str]):
        if len(ret) < 1:
            self.ret = None
        else:
            self.ret = ret
    
    
    def add_codeline(self, text: str):
        self.codes.append(text)
    
    @classmethod
    def load_function(cls, filename:str, name:str, arg:list[str], ret:list[str]):
        c = cls(CodeType.FUNCTION, filename, name)
        c.set_args(arg)
        c.set_return(ret)
        return c

    @classmethod
    def load_class_function(cls, filename:str, name:str, arg:list[str], ret:list[str]):
        c = cls(CodeType.CLASS_FUNC, filename, name)
        c.set_args(arg)
        c.set_return(ret)
        return c

    @classmethod
    def load_class(cls, filename:str, name:str, bases:list[str]):
        c = cls(CodeType.CLASS, filename, name)
        c.set_bases(bases)
        return c
