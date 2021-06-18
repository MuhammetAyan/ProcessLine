from os import error
import pickle
from enum import Enum
from typing import Callable, Dict, List

class ProcessError(ValueError):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ProcessIOType(Enum):
    Csv = 0
    Pickle = 1

class Layer:
    
    def __init__(self, run: callable, *args: list):
        self._run: callable = run
        self.args: list = args
        self._before: Callable = None
    
    def __call__(self):
        args = [self._before]
        args.extend(self.args)
        return self._run(*args)

class ProcessInput:

    def __init__(self, filename:str, type: ProcessIOType) -> None:
        self._filename = filename
        self._type = type
        self._generator = None
        self._gen_args = []
        self._fs = None
        self._canRead = False
        self.header = None
        self.attributes = {}
        if type == ProcessIOType.Csv:
            self.attributes = {"split-char": ",", "has-header": True, "skip-wrong-rows": True, "convert-list": None}
        elif type == ProcessIOType.Pickle:
            self.attributes = {"has-header": True}
    
    def load(self) -> None:
        if self._type == ProcessIOType.Csv:
            self._fs = open(self._filename, mode="r", encoding="utf-8")
            self._generator = self._csv_row_parser
            self._gen_args = []
        elif self._type == ProcessIOType.Pickle:
            self._fs = open(self._filename, "rb")
            self._generator = self._pickle_generator
            self._gen_args = []
        
        self._canRead = True
        if self.attributes["has-header"]:
            self.header = self._generator(*self._gen_args).__next__()

    def _csv_row_parser(self) -> list:
        while True:
            row = self._fs.readline()
            if self.attributes["skip-wrong-rows"] and row == "":
                break
            _row = row.split(self.attributes["split-char"])
            _row[-1] = _row[-1].rstrip("\n")
            yield _row
    
    def _pickle_generator(self) -> list:
        while True:
            try:
                row = pickle.load(self._fs)
                yield row
            except EOFError:
                self._canRead = False
                break

    
    def read(self) -> object:
        try:
            if self.attributes["convert-list"] == None:
                for row in self._generator(*self._gen_args):
                    yield row
            else:
                for row in self._generator(*self._gen_args):
                    for i in range(len(row)):
                        row[i] = self.attributes["convert-list"][i](row[i])
                    yield row
        except:
            self._canRead = False

    def canRead(self) -> bool:
        return self._canRead
    
    def close(self) -> None:
        if self._type == ProcessIOType.Csv:
            self._fs.close()
        elif self._type == ProcessIOType.Pickle:
            self._fs.close()

class ProcessOutput:
    
    def __init__(self, filename:str, type: ProcessIOType) -> None:
        self._filename = filename
        self._type = type
        self._writer = None
        self._wr_args = []
        self._fs = None
        self._canWrite = False
        self.attributes = {}
        if type == ProcessIOType.Csv:
            self.attributes = {"split-char": ",", "has-header": True, "convert-list": None}
        elif type == ProcessIOType.Pickle:
            self.attributes = {"has-header": True}
    
    def begin(self, header) -> None:
        if self._type == ProcessIOType.Csv:
            self._fs = open(self._filename, mode="w", encoding="utf-8")
            self._writer = self._csv_row_editor
            self._wr_args = []
        elif self._type == ProcessIOType.Pickle:
            self._fs = open(self._filename, "wb")
            self._writer = pickle.dump
            self._wr_args = [self._fs]
        
        self._canWrite = True
        if self.attributes["has-header"]:
            self._write(header, True)
    
    def _csv_row_editor(self, row: list)-> None:
        _row = [str(col) if col is not None else "" for col in row]
        self._fs.write(self.attributes["split-char"].join(_row) + "\n")
    
    def write(self, row: object) -> None:
        return self._write(row)

    def _write(self, row: object, isHeader=False) -> None:
        if not self._canWrite: return False
        try:
            if not isHeader:
                for i in range(len(row)):
                    row[i] = self.attributes["convert-list"][i](row[i])
            params = [row]
            params.extend(self._wr_args)
            self._writer(*params)
            return True
        except Exception as e:
            self._canWrite = False
            raise ProcessError("ProcessOutput writing error: " + str(e))
    
    def canWrite(self) -> bool:
        return self._canWrite
    
    def close(self) -> None:
        if self._type == ProcessIOType.Csv:
            self._fs.close()
        elif self._type == ProcessIOType.Pickle:
            self._fs.close()

class Process:

    def __init__(self, In: ProcessInput, Out: ProcessOutput = None):
        self._input = In
        self._output = Out
        self.Layers: List[Layer] = []

    def start(self) -> None:
        self._input.load()
        header = self._input.header
        if self._output is not None:
            if self._output.attributes["has-header"]:
                self._output.begin(header)
            else:
                self._output.begin()
    
    def canProcess(self) -> bool:
        if self._output is not None:
            return self._input.canRead() and self._output.canWrite()
        else:
            return self._input.canRead()
    
    def process(self):
        if not self.canProcess():
            raise ProcessError("Process not executable! Look at input and output.")
        index = 0
        layer_chain = self._input.read()
        while index < len(self.Layers):
            layer = self.Layers[index]
            layer._before = layer_chain
            layer_chain = layer()
            index += 1
        for row in layer_chain:
            if self._output is not None:
                yield row, self._output.write(row)
            else:
                yield row, True

    def close(self) -> None:
        self._input.close()
        if self._output is not None:
            self._output.close()

class Merging:

    def __init__(self, processList: List[Process], output: ProcessOutput) -> None:
        self._processes = processList
        self._output = output
        self._mapping = []
        self._all_header = None

    
    def start(self) -> None:
        for process in self._processes:
            process.start()
        self._output.begin()
        self._mapping = []
        self._all_header = None
    
    def canMerge(self) -> bool:
        for process in self._processes:
            if not process.canProcess():
                return False
        return self._output.canWrite()
    
    @staticmethod
    def _extend(source: list, target :list):
        list_index = []
        for t_item in target:
            if not t_item in source:
                list_index.append(len(source))
                source.append(t_item)
            else:
                list_index.append(source.index(t_item))
        return list_index
    
    @staticmethod
    def _mapRow(row:list, mapp:list, header_len:int) -> list:
        new_row = [None for i in range(header_len)]
        for i in range(len(mapp)):
            new_row[mapp[i]] = row[i]
        return new_row
    
    def get_header(self) -> list:
        return self._all_header

    def merge(self) -> None:
        if not self.canMerge(): raise ProcessError("Merging class not executable!")
        gens = [] # all processes of generators
        all_header = []
        mapping: Dict[list] = {}
        #All Headers scan and mapping
        for process in self._processes:
            gens.append(process.process())
            for row, _ in gens[-1]:        
                p_header = row
                mapping[process] = Merging._extend(all_header, p_header)
                break
        yield all_header, self._output.write(all_header)
            # print("Sütunlar:", all_header)
            # print("Sütun sayısı:", len(all_header))
            # print("map:", mapping)
        for i in range(len(self._processes)):
            process = self._processes[i]
            gen = gens[i]
            for row, _ in gen:
                _row = Merging._mapRow(row=row, mapp=mapping[process], header_len=len(all_header))
                yield _row, self._output.write(_row)


    def close(self) -> None:
        for process in self._processes:
            process.close()
        self._output.close()
        