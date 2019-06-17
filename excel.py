# @Time    : 2019/6/17 14:23
# @Email   : 772632967@qq.com
# @File    : excel.py
# @Software: PyCharm

from openpyxl import load_workbook



class ExcelMass(object):
    """
    提取Excel文件中的mass

    """
    def __init__(self,path):
        self.sheet=load_workbook(filename=path)['Sheet1']
        self.mass_list=self.get_masses()

    def get_masses(self):
        masses_list=[]
        for cell  in self.sheet['C']:
            if cell.value is not None and cell.value != '质荷比' :
                masses_list.append(cell.value)
        return masses_list
