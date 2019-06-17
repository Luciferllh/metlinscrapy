# @Time    : 2019/6/17 15:21
# @Email   : 772632967@qq.com
# @File    : test.py
# @Software: PyCharm
import re
a='(157.0305 - 157.0368 daltons): 0 Metabolites [M+Na]+'
f='.*: (?P<count>\d+).*(?P<kind>M\+H|M\+NH4|M\+Na)'
g=re.search(f,a).group('count')
h=re.search(f,a).group('kind')
print(g,h)
