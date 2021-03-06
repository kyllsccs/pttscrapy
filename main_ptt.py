import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd
import openpyxl

class FetchPtt():
    def __init__(self, path, page_list, timerange):
        self.path = path
        self.timerange = timerange
        self.page_list = page_list

    def page_link(path, n):
        response = requests.get(path)
        data_soup = BeautifulSoup(response.text, 'lxml')
        prev_link_part = data_soup.select('.btn-group.btn-group-paging a')
        page_link_list = [i.get('href') for i in prev_link_part]
        prev_page_link = f'https://www.ptt.cc{page_link_list[1]}'
        new_page_link = f'https://www.ptt.cc{page_link_list[3]}'
        bordername = page_link_list[3].replace('/bbs/','').replace('/index.html', '')
        page_num = int(''.join([x for x in prev_page_link if x.isdigit()]))
        # print(page_num + 1)
        page_count = [f'https://www.ptt.cc/bbs/{bordername}/index{page_num - i}.html' for i in range(n)]
        page_count.insert(0, new_page_link)
        print(page_count)
        return page_count
    # 送出請求給ptt web
    def ptt_response(path_list, timerange):
        save_data_list = []
        for j in path_list:
            response = requests.get(j)
            data_soup = BeautifulSoup(response.text, 'lxml')
            
            now_timestamp = int(time.time()) # 取出現在的timestamp

            article_bank = (i for i in data_soup.select('.r-ent')) # 做成generator
            for k in range(len(data_soup.select('.r-ent'))): # 每一個generator動作
                article_box = next(article_bank)
                if article_box.select_one('.title a') is not None:
                    timestamp_art = article_box.select_one('.title a').get('href')[14:24]
                    if now_timestamp - int(timestamp_art) <= timerange: # 判定掃描區間
                        link_art = 'https://www.ptt.cc{}'.format(article_box.select_one('.title a').get('href'))
                        author_art = article_box.select_one('.meta .author').get_text()
                        title_art = article_box.select_one('.title').get_text().replace('\n', '')
                        date_art = article_box.select_one('.meta .date').get_text()
                        article_array = [timestamp_art, date_art, author_art, title_art, link_art]
                        save_data_list.append(article_array)
                    else:
                        pass
                else:
                    print('Status : 此文已被刪除.')
        df = pd.DataFrame(save_data_list, columns = ['timeStamp', 'Date', 'Author', 'Title', 'Link'])
        print(df)
        df.to_excel('./test.xlsx', engine = 'openpyxl', index = None)


if __name__ == '__main__':
    path = 'https://www.ptt.cc/bbs/Wanted/index.html'
    a_list = FetchPtt.page_link(path, 120)
    FetchPtt.ptt_response(a_list, 864000)
