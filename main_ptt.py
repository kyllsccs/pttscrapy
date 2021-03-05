import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd

class FetchPtt():
    def __init__(self, path, page_list, timerange):
        self.path = path
        self.timerange = timerange
        self.page_list = page_list

    def page_link(path):
        response = requests.get(path)
        data_soup = BeautifulSoup(response.text, 'lxml')
        prev_link_part = data_soup.select('.btn-group.btn-group-paging a')
        page_link_list = [i.get('href') for i in prev_link_part]
        prev_page_link = f'https://www.ptt.cc{page_link_list[1]}'
        new_page_link = f'https://www.ptt.cc{page_link_list[3]}'
        page_list = [prev_page_link, new_page_link]
        # print(page_list)
        return page_list
    # 送出請求給ptt web
    def ptt_response(path_list, timerange):
        for j in path_list:
            save_data_list = []
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


if __name__ == '__main__':
    path = 'https://www.ptt.cc/bbs/C_Chat/index.html'
    a_list = FetchPtt.page_link(path)
    FetchPtt.ptt_response(a_list, 3600)
