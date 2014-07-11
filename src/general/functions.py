'''
Created on Feb 25, 2014

@author: Vincent Ketelaars
'''
import re

KB = 1024
MB = KB * 1024
GB = MB * 1024
TB = GB * 1024

"""
@return number of bytes
"""
def string_to_size(s):
    s = s.strip()
    m = re.match("\d+\.?\d*", s)
    num = 0
    if m is not None:
        num = float(m.group(0))
    mul = 0
    if s.find("KB") > 0:
        mul = KB
    elif s.find("MB") > 0:
        mul = MB
    elif s.find("GB") > 0:
        mul = GB
    elif s.find("TB") > 0:
        mul = TB
    return num * mul

def size_to_string(b):
    i = 0
    while b > 1024:
        b = b / 1024
        i += 1
    v = ["B","KB", "MB", "GB", "TB"]
    return "%d %s" % (b, v[i])