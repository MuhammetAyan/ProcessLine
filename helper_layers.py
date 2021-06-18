from typing import Callable
from .convater import *
import os


def colPrint(lyr, col_index: int = None):
    for row in lyr:
        if col_index is None:
            print(row)
        else:
            print(row[col_index])
        yield row

def SatirSay(lyr):
    i = 0
    for row in lyr:
        i += 1
        print(f"{i}. Satır")
        yield row

def SatirdaDur(lyr, i: int):
    x = 0
    for row in lyr:
        if x == i:
            break
        yield row
        x += 1

def EgerSay(lyr, kosul: Callable, rapor_metni: str):
    isHeader = True
    count = 0
    for row in lyr:
        if isHeader:
            isHeader = False
            yield row
            continue
        else:
            if kosul(row):
                count += 1
            yield row
    print(rapor_metni + ": ", count)

def Filter(lyr, kosul: Callable):
    isHeader = True
    for row in lyr:
        if isHeader:
            isHeader = False
            yield row
            continue
        else:
            if kosul(row):
                yield row

def PrintSelect(lyr, func: Callable):
    isHeader = True
    for row in lyr:
        if isHeader:
            isHeader = False
            yield row
            continue
        else:
            print(func(row))
            yield row

def Line(lyr, processEnd: bool = True, length: int = 100, chr: str = "-"):
    for row in lyr:
        if not processEnd:
            print(chr * length)
        yield row
    if processEnd:
        print(chr * length)

def TypeTahmin(lyr):
    def typeName(T):
        if len(str(T).split("'")) > 1:
            return str(T).split("'")[1]
        else:
            return str(T).split(" ")[1]
    isHeader = True
    header = []
    types = []
    test = [int, float, sint, sfloat, strtodatetime, str]
    for row in lyr:
        if isHeader:
            isHeader = False
            header = row
            for col in row:
                types.append({})
            yield row
            continue
        else:
            for i in range(len(row)):
                if row[i] is None:
                    if dict(types[i]).keys().__contains__("None"):
                        types[i]["None"] += 1
                    else:
                        types[i]["None"] = 1
                elif row[i] == "":
                    if dict(types[i]).keys().__contains__("Empty"):
                        types[i]["Empty"] += 1
                    else:
                        types[i]["Empty"] = 1
                else:
                    for parser in test:
                        try:
                            parser(row[i])
                            if dict(types[i]).keys().__contains__(typeName(parser)):
                                types[i][typeName(parser)] += 1
                            else:
                                types[i][typeName(parser)] = 1
                        except:
                            pass
            yield row
    print("Sütun tip tahminleri:")
    for i in range(len(header)):
        print(header[i] + ":", types[i])


def Debug(lyr):
    isBreak = False
    isEval = True
    isDebugMode = True
    i = -1
    print("DEBUG Modu aktif")
    print("""ÖZEL KOMUTLAR:
row     Okunan veri
*       Eval ve Exec modları arası geçiş
end     İtaratür okumayı sonlandırır.
<boş>   Bir sonraki itaratüre geçer.
cls     Konsolu temizler.
i       İteratür indisini döndürür.
cancel  Okunan veriyi iptal eder.
ok      Debug moddan çıkar.

filter  filtreyi sıfırlar.(exec mod)
filter (kosul)  Koşula uyan satıra kadar tüm verileri durmadan geçer.(Exec mod)

>>=     Değer okuma modu (eval)
>>>     Atama modu (exec)
""")
    scope = {"filter": None}
    for row in lyr:
        if not isDebugMode:
            yield row
            continue
        i += 1
        scope["row"] = row
        scope["i"] = i
        if scope["filter"] is not None and not scope["filter"](row, i):
            yield row
            continue
        while True:
            isCanceled = False
            try:
                if isEval:
                    cmd = input(f"{i}>>=")
                    if cmd.strip() == "*":
                        isEval = not isEval
                        continue
                    elif cmd.strip() == "cls":
                        os.system("cls")
                        continue
                    elif cmd.strip() == "ok":
                        isDebugMode = False
                        break
                    elif cmd.strip() == "cancel":
                        isCanceled = True
                        break
                    elif cmd.strip() == "end":
                        isBreak = True
                        break
                    elif cmd.strip() == "": break
                    print(eval(cmd, scope))
                else:
                    cmd = input(f"{i}>>>")
                    if cmd.strip() == "*":
                        isEval = not isEval
                        continue
                    elif cmd.strip() == "cls":
                        os.system("cls")
                        continue
                    elif cmd.strip() == "ok":
                        isDebugMode = False
                        break
                    elif cmd.strip() == "cancel":
                        isCanceled = True
                        continue
                    elif cmd.strip() == "end":
                        isBreak = True
                        break
                    elif cmd.strip().startswith("filter"):
                        if cmd.strip() == "filter":
                            scope["filter"] = None
                        elif cmd.strip().startswith("filter "):
                            scope["filter"] = eval("lambda row, i: " + cmd.strip()[7:], scope)
                            print("lambda row, i: " + cmd.strip()[7:])
                            continue
                            
                    elif cmd.strip() == "": break
                    exec(cmd, scope)
            except Exception as e:
                print("HATA:", e)
        if isBreak: break
        if not isCanceled:
            yield row