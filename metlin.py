# @Time    : 2019/6/15 0:54
# @Email   : 772632967@qq.com
# @File    : metlin.py
# @Software: PyCharm

import requests
import multiprocessing
import time
from lxml import etree
from openpyxl import Workbook
from openpyxl import load_workbook
import pandas as pd

class ChemicalAnalysis(object):
    """
    从metlin.scripps.edu爬出数据的类
    """

    def __init__(self, masses):
        """
        初始化请求url和请求头
        """
        self.url = 'https://metlin.scripps.edu/batch_search_result.php'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
        }
        self.masses=masses
        self.params = {
            "masses": masses,
            "adducts": "M+H,M+NH4,M+Na",
            "ppm": "20",
            "modes": "1",
            "structure": "Y",
            "formVar": "M+H,M+NH4,M+Na",
            "AminoAcid": "remove",
            "drug": "remove",
            "toxinEPA": "remove",
        }
        self.data_list=self.main()

    def match(self, id,kind,mass,ppm,name, formula, img):
        """
        数据匹配
        :param id:
        :param name:
        :param formula:
        :param img:
        :return:
        """
        return {"id": id, 'kind':kind,"mass":mass,"ppm":ppm,"name": name, "formula": formula, 'img': f'https://metlin.scripps.edu/{img}'}

    def table_list(self, tree):
        """
        获取table
        :param tree:
        :return:
        """
        return tree.xpath('//table[@id="example"]')

    def get_data_list(self, tree):
        """
        解析主要页面数据
        :param tree:
        :return:
        """
        table_list=self.table_list(tree)

        if len(table_list) == 0 :
            print(f'{self.masses}查询完成,没有查到数据')
            return  [{"id": 'na', 'kind':'na',"mass":self.masses,"ppm":'na',"name": 'na', "formula": 'na', 'img': 'na'}]

        title_list = self.title_list()

        total_data_list = []
        for index, table in enumerate(table_list):
            id_list = table.xpath('.//tbody/tr/th/a/text()')
            ppm_list = table.xpath('.//tbody/tr/td[2]/text()')
            kind_list = [title_list[index] for i in range(len(id_list))]
            mass_list = [self.masses for i in range(len(id_list))]
            name_list = table.xpath('.//tbody/tr/td[3]/text()')
            formula_list = table.xpath('.//tbody/tr/td[4]/text()')
            img_list = table.xpath('.//tbody/tr/td[@id="molImg"]/a/@href')
            data_list = map(self.match, id_list,kind_list,mass_list,ppm_list,name_list, formula_list, img_list)
            total_data_list.extend(list(data_list))
        print(f'{self.masses}查询完成,查到数据')
        return total_data_list

    def title_list(self):
        return ['M+H','M+NH4','M+Na']


    def get_tree(self):
        page_text=requests.get(url=self.url, headers=self.headers, params=self.params).text
        return etree.HTML(page_text)

    def main(self):
        """
        主函数
        :return:
        """
        tree=self.get_tree()
        data_list=self.get_data_list(tree)

        return data_list


class Masses(object):

    def __init__(self,filename):
        self.sheet=load_workbook(filename=filename)['Sheet1']
        self.mass_list=self.get_masses()

    def get_masses(self):
        masses_list=[]
        for cell  in self.sheet['C']:
            if cell.value is not None and cell.value != '质荷比' :
                masses_list.append(cell.value)
        return masses_list




if __name__ == "__main__":


    mass_list=Masses(filename='META.xlsx').mass_list
    # for mass in mass_list:
    #     pool.apply_async(ChemicalAnalysis,(mass,))
    # pool.close()
    # pool.join()
    total_data=[]
    for mass in mass_list:
        chemical_data=ChemicalAnalysis(masses=mass).data_list
        total_data.extend(chemical_data)
        time.sleep(5)
    df=pd.DataFrame(total_data,dtype=str)
    df.to_excel('after.xlsx',encoding='utf-8')
