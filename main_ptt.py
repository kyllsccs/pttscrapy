import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd
import openpyxl
import sqlite3

class FetchPtt():
    def __init__(self, path, n, timerange):
        # 設定全局參數
        self.path = path
        self.n = n
        self.timerange = timerange*60
        self.bname = path.replace('https://www.ptt.cc/bbs/', '').replace('/index.html', '')
        self.cookies = {'over18':'1'}

    # 取出需要爬取的頁數
    def page_link(self):
        response = requests.get(self.path, cookies = self.cookies)
        data_soup = BeautifulSoup(response.text, 'html.parser')
        prev_link_part = data_soup.select('.btn-group.btn-group-paging a')
        page_link_list = [i.get('href') for i in prev_link_part]
        prev_page_link = f'https://www.ptt.cc{page_link_list[1]}'
        new_page_link = f'https://www.ptt.cc{page_link_list[3]}'
        bordername = page_link_list[3].replace('/bbs/','').replace('/index.html', '')
        page_num = int(''.join([x for x in prev_page_link if x.isdigit()]))
        page_count = [f'https://www.ptt.cc/bbs/{bordername}/index{page_num - i}.html' for i in range(self.n)]
        page_count.insert(0, new_page_link)
        # print(page_count)
        return page_count
    # 送出請求給ptt web
    def ptt_response(self, path_list):
        save_data_list = []
        now_timestamp = int(time.time()) # 取出現在的timestamp
        time_x = now_timestamp - self.timerange*3 # 監控區間, 設定的3倍, 避免重複
        # print(time_x)
        # print(now_timestamp - time_x)

        delete_counter = 0
        data_exist = 0
        write_num = 0

        # =============叫出資料庫時間區間============
        DB_file = './0000A1_pttdata.db'
        con = sqlite3.connect(DB_file)
        cur = con.cursor()
        data_bank = cur.execute(f'SELECT PostNumb FROM PTTDATA WHERE PostTims>{now_timestamp-self.timerange*20} AND PostBord=\'{self.bname}\';')
        datas_list = [i[0] for i in data_bank]
        # print(datas_list)
        con.close()

        compare_box = []
        for j in path_list:
            response = requests.get(j, cookies = self.cookies)
            data_soup = BeautifulSoup(response.text, 'html.parser')
            article_bank = (i for i in data_soup.select('.r-ent')) # 做成generator

            for k in range(len(data_soup.select('.r-ent'))): # 每一個generator動作
                article_box = next(article_bank)
                if article_box.select_one('.title a') is not None:
                    timestamp_art_1 = article_box.select_one('.title a').get('href').replace(f'/bbs/{self.bname}/', '')[0:-10]
                    timestamp_art = '{}'.format(''.join([i for i in timestamp_art_1 if i.isdigit()]))
                    author_art = article_box.select_one('.meta .author').get_text()
                    post_num = f'{self.bname[0:1].upper()}{author_art[0:2].upper()}{timestamp_art}'
                    if post_num in compare_box:
                        pass
                    else:
                        if f'{self.bname[0:1].upper()}{author_art[0:2].upper()}{int(timestamp_art)}' in datas_list:
                            # 不要去抓取到重複timeStamp
                            data_exist += 1
                        else:
                            if now_timestamp - int(timestamp_art) <= self.timerange: # 判定掃描區間
                                link_art = 'https://www.ptt.cc{}'.format(article_box.select_one('.title a').get('href'))
                                title_art = article_box.select_one('.title').get_text().replace('\n', '')
                                date_art = article_box.select_one('.meta .date').get_text()
                                article_array = [post_num, int(timestamp_art), self.bname, date_art.replace('/','-'), author_art, title_art, link_art]
                                compare_box.append(post_num)
                                save_data_list.append(article_array)
                                write_num += 1
                                # print(article_array)
                            else:
                                pass
                else:
                    delete_counter += 1
        print(f'Status : 目前抓取版面: {self.bname}.')
        print(f'Status : 資料寫入數量: {write_num}.')
        print(f'Status : 資料重複數量: {data_exist}.')
        print(f'Status : 文章刪除數量: {delete_counter}.')
        
        # ========可轉成excel存檔=============
        # df = pd.DataFrame(save_data_list, columns = ['PostNum', 'timeStamp', 'Boardname', 'Date', 'Author', 'Title', 'Link']).sort_values(by=['timeStamp'])
        # print(df)
        # df.to_excel('./test.xlsx', engine = 'openpyxl', index = None)
        
        # ========連結sqlite資料庫寫入=========
        DB_file = './0000A1_pttdata.db'
        con = sqlite3.connect(DB_file)
        cur = con.cursor()
        cur.executemany('INSERT INTO PTTDATA VALUES(?,?,?,?,?,?,?)', save_data_list)
        con.commit()
        con.close()

if __name__ == '__main__':
    # path = 'https://www.ptt.cc/bbs/Wanted/index.html'
    # path = 'https://www.ptt.cc/bbs/Sex/index.html'
    # path = 'https://www.ptt.cc/bbs/feminine_sex/index.html'
    # path = 'https://www.ptt.cc/bbs/StupidClown/index.html'
    # path = 'https://www.ptt.cc/bbs/joke/index.html'
    # path = 'https://www.ptt.cc/bbs/beauty/index.html'
    # path = 'https://www.ptt.cc/bbs/C_Chat/index.html'
    # path = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    # pageNumber = input('請輸入抓取頁數 : ')
    # timeSetting = input('請輸入監控分鐘數 : ')
    # a = FetchPtt(path, int(pageNumber), int(timeSetting))
    # a = FetchPtt(path, 5, 30)
    # b = a.page_link()
    # a.ptt_response(b)

    DB_path = './0000A1_pttdata.db'
    con = sqlite3.connect(DB_path)
    cur = con.cursor()

    inner_sets_val = cur.execute('SELECT WEBSITE,PAGES,TIMES FROM PTTSCRAPY')

    setting_c = [i for i in inner_sets_val]

    for i in range(len(setting_c)):
        a = FetchPtt(setting_c[i][0], setting_c[i][1], setting_c[i][2])
        b = a.page_link()
        a.ptt_response(b)
