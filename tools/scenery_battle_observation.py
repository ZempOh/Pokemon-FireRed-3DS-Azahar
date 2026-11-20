"""A battle ending is not by itself a rendered return to the field."""
import re
def progress(text):
 states=list(re.finditer(r'telemetry .*connected=true.*inBattle=(true|false)',text))
 battles=[m for m in states if m[1]=='true']
 if not battles:return False,False
 # A reset followed by loading Continue is not a completed battle. Party size
 # stays positive after a legitimate whiteout, even when every member fainted.
 if re.search(r'telemetry .*connected=true.*party=0\b.*inBattle=false',text[battles[0].end():]):
  return True,False
 after=text[battles[-1].end():]
 fields=re.findall(r'scenery crc=[0-9a-f]+ rendered=(\d+)/\d+ blocked=[0-9a-f]+ scene=(\d+)',after)
 # A trainer victory can briefly show the field before a second story scene.
 # Require the current field to remain rendered across consecutive samples.
 return True,bool(states[-1][1]=='false' and len(fields)>=2 and
                  all(int(count)>0 and scene=='0' for count,scene in fields[-2:]))
