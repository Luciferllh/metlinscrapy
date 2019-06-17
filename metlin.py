# @Time    : 2019/6/15 0:54
# @Email   : 772632967@qq.com
# @File    : metlin.py
# @Software: PyCharm

import requests
import time
import pandas as pd
import random

from lxml import etree
from fake_useragent import UserAgent



from word import WordMass
from excel import ExcelMass
from cookie import COOKIE


class ChemicalAnalysis(object):
    """
    从metlin.scripps.edu爬出数据的类
    """

    def __init__(self, masses,adducts,cookie):
        """
        初始化请求url和请求头
        """
        self.url = 'https://metlin.scripps.edu/batch_search_result.php'
        self.headers = {
            'User-Agent': UserAgent().random,
            'cookie':cookie
        }
        self.masses=masses
        self.adducts=adducts
        self.params = {
            "masses": self.masses,
            "adducts": self.adducts,
            "ppm": "20",
            "modes": "1",
            "structure": "Y",
            "formVar": self.adducts,
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
            print(f'{self.masses} {self.adducts}查询完成,没有查到数据')
            return  [{"id": 'na', 'kind':self.adducts,"mass":self.masses,"ppm":'na',"name": 'na', "formula": 'na', 'img': 'na'}]

        total_data_list = []
        for index, table in enumerate(table_list):
            id_list = table.xpath('.//tbody/tr/th/a/text()')
            ppm_list = table.xpath('.//tbody/tr/td[2]/text()')
            kind_list = [self.adducts for i in range(len(id_list))]
            mass_list = [self.masses for i in range(len(id_list))]
            name_list = table.xpath('.//tbody/tr/td[3]/text()')
            formula_list = table.xpath('.//tbody/tr/td[4]/text()')
            img_list = table.xpath('.//tbody/tr/td[@id="molImg"]/a/@href')
            data_list = map(self.match, id_list,kind_list,mass_list,ppm_list,name_list, formula_list, img_list)
            total_data_list.extend(list(data_list))
        print(f'{self.masses} {self.adducts}查询完成,查到数据')
        return total_data_list

    # def title_list(self,tree):
    #     return tree.xpath('//div//b[1]/text()')


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


if __name__ == "__main__":
    # ChemicalAnalysis(masses=325.1192,adducts='M+NH4')
    path='只存在A367-HADV.docx'
    if path.endswith('xlsx'):
        mass_list=ExcelMass(path=path).mass_list
    else:
        mass_list=WordMass(path=path).mass_list
    total_data=[]
    adducts_list=['M+H','M+NH4','M+Na']
    for mass in mass_list:
        for adducts in adducts_list:
            chemical_data=ChemicalAnalysis(masses=mass,adducts=adducts,cookie=COOKIE).data_list
            total_data.extend(chemical_data)
            time.sleep(random.uniform(5,8))
    df=pd.DataFrame(total_data,dtype=str)
    df.to_excel(f'{path}+.xlsx',encoding='utf-8')
