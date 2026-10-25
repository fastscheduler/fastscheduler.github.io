import io
BS = chr(92)
print('BS Eldorado:', [BS])
s = 'a' + BS + 's' + 'b'
print('concat ok:', s)
import re
print('re test:', re.findall('a', 'a'))
