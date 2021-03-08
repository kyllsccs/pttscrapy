import sqlite3


page_num = int(input('please set page mounts (page) :'))
time_num = int(input('please set time ranges (mins) :'))

DB_path = './0000A1_pttdata.db'

con = sqlite3.connect(DB_path)
cur = con.cursor()

cur.execute(f'UPDATE PTTSCRAPY SET PAGES={page_num},TIMES={time_num};')
con.commit()
con.close()