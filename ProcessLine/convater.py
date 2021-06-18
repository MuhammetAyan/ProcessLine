import datetime as dt

class ConvaterInput:

  def __init__(self) -> None:
      self.datetime_format = "%d-%m-%Y %H:%M:%S"
      self.date_format = "%d-%m-%Y"
      self.strip_characters = [' ', '\n', '\t', '\r']

  def _clean(self, s: str)-> str:
    if type(s) == str:
      for ch in self.strip_characters:
        s = s.replace(ch, "")
    return s
    
  def datetime(self, s: str) -> dt.datetime:
    s = self._clean(s)
    return dt.datetime.strptime(s, self.datetime_format) if s != "" and s != None else None
  
  def float(self, s: str) -> float:
    s = self._clean(s)
    if s != None and s != "":
      s = s.replace(",", ".")
      return float(s)
    else:
      return None
  
  def int(self, s: str) -> int:
    s = self._clean(s)
    if s != None and s != "":
      s = s.replace(",", ".")
      return int(s)
    else:
      return None

  def bool(self, s: str) -> bool:
    s = self._clean(s)
    if s != None and s != "":
      if s.lower() in ["yes", "true", "y", "t", "1", "+"]:
        return True
      elif s.lower() == ["no", "false", "n", "f", "0", "-"]:
        return False
      else:
        return bool(s)
    else:
      return None
  
class ConvaterOutput:

  def __init__(self) -> None:
      self.datetime_format = "%d-%m-%Y %H:%M:%S"
      self.date_format = "%d-%m-%Y"
    
  def datetime(self, s: dt.datetime) -> str:
    if s == None: return ""
    return s.strftime(self.datetime_format)
  
  def number(self, s: float) -> float:
    if s == None: return ""
    return str(s)
  
  def bool(self, s: bool) -> str:
    if s == None: return ""
    return str(s)