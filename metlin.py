# @Time    : 2019/6/15 0:54
# @Author  : liyonghan
# @Email   : 772632967@qq.com
# @File    : metlin.py
# @Software: PyCharm

import requests

from lxml import etree


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
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
        }
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

    def match(self, id, name, formula, img):
        """
        数据匹配
        :param id:
        :param name:
        :param formula:
        :param img:
        :return:
        """
        return {"id": id, "name": name, "formula": formula, 'img': img}

    def table_list(self, tree):
        """
        获取table
        :param tree:
        :return:
        """
        return tree.xpath('//table[@id="example"]')

    def data_list(self, tree):
        """
        解析主要页面数据
        :param tree:
        :return:
        """
        total_data_list = []
        for index, table in enumerate(self.table_list(tree)):
            id_list = table.xpath('.//tbody/tr/th/a/text()')
            name_list = table.xpath('.//tbody/tr/td[3]/text()')
            formula_list = table.xpath('.//tbody/tr/td[4]/text()')
            img_list = table.xpath('.//tbody/tr/td[@id="molImg"]/a/@href')
            data_list = map(self.match, id_list, name_list, formula_list, img_list)
            total_data_list.append(list(data_list))
        return total_data_list

    def title_list(self,tree):
        return tree.xpath('//div//b[1]/text()')


    def get_tree(self):
        page_text=requests.get(url=self.url, headers=self.headers, params=self.params).text
        return etree.HTML(page_text)

    def main(self):
        """
        主函数
        :return:
        """
        tree=self.get_tree()
        data_list=self.data_list(tree)
        title_list=self.title_list(tree)
        print(data_list)
        print(title_list)



if __name__ == "__main__":
    ca = ChemicalAnalysis(masses='456.2834')
    ca.main()
