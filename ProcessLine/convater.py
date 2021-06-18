import datetime

def strtodatetime(s):
  return datetime.datetime.strptime(s, "%d.%m.%Y %H:%M:%S") if s != "" and s != None else None
# sfloat = lambda s: float(s.replace(",", ".")) if s != "" and s != None else None
# sint = lambda s: int(s) if s != "" and s != None else None

# Sayısal değerlerin içerisinde yer almasını istemediğimiz karakterler
strip_characters = [chr(10), chr(34), chr(45), chr(32), chr(104), chr(37), chr(63), "<", ">", "yetersiznumune"]

def sfloat(s):
    if s != None and s != "":
      s = s.replace(",", ".").strip(' \n\r\t%*')
      for ch in strip_characters:
        s = s.replace(ch, "")
      if s == "":
        return None
      return float(s)
    else:
      return None
      # sys.stderr.write(f"sfloat('{len(s)}'): '{e}'\n")

def sint(s):
  if s != None and s != "":
    return int(s.replace(" ", ""))
  else:
    return None
    # sys.stderr.write(f"sint('{s}'): '{e}'\n")
  