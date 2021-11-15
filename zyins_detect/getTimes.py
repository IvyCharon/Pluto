import time
import requests
import time
import os
import csv
import re
import json
from html.parser import HTMLParser

names = {
    'dataisland@outlook.com' : 'me',
}

save_path = 'saves'
zy_article_url = 'https://zhiyuan.sjtu.edu.cn/api/get_singlepage_by_id/'

time_str = '%04d-%02d-%02d %02d:%02d:%02d'

salon_records = [('2013', '2948'),
                 ('2014', '2943'),
                 ('2015', '2942'),
                 ('2016', '1902'),
                 ('2017', '2909'),
                 ('2018', '2919'),
                 ('2019', '3368'),
		         ('2020', '3813'),
                 ('2021', '3911'),
                 ('other', '3814')]

other_set = {'other'}

stu_info_file = 'stu_info.csv'
update_time_file = 'update_time.text'
salon_record_file = 'record_%s.text'

class UniObject(object):
    pass

class MyHTMLParser(HTMLParser):
    in_page_body = False
    in_h2 = False
    in_p = False
    get_pre_h2 = False
    lines = []

    def myInit(self):
        self.in_page_body = True
        self.in_h2 = False
        self.in_p = False
        self.in_span = False
        self.get_pre_h2 = False
        self.lines = []
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and attrs == [('class', 'page-body')]:
            self.in_page_body = True
        if not self.in_page_body:
            return
        if tag == 'h2':
            self.title = ''
            self.in_h2 = True
        elif tag == 'p':
            self.in_p = True

    def handle_endtag(self, tag):
        if not self.in_page_body:
            return
        if tag == 'div':
            self.in_page_body = False
        elif tag == 'h2':
            self.in_h2 = False
            if len(self.lines) > 0 and len(self.lines[-1]) == 0:
                # print('[DEBUG]',self.lines[-2])
                self.lines.pop()
                self.lines.pop()
            if '2' in self.title and '.' in self.title:
                self.get_pre_h2 = True
                self.lines.append(self.title.strip().replace('（','(').replace('）',')').replace(' ', '').replace('\n',''))
                self.lines.append('')
        elif tag == 'p':
            self.in_p = False

    def handle_data(self, data):
        if not self.in_page_body:
            return
        if self.in_h2:
            self.title += data
        elif self.get_pre_h2 and self.in_p and '5' in data:
            self.lines[-1] += data.strip().replace('（','(').replace('）',')').replace(' ', '').replace('\n','')
        # elif len(data.strip()) > 0:
            # print('[DEBUG]', data)
            
def process_html(name, html):
    html = json.loads(html)['text']['cn_content']
    parser = MyHTMLParser()
    parser.myInit()
    parser.feed(html)
    out_file = os.path.join(save_path, salon_record_file % (name))
    # print('WRITE', name, 'info to', out_file)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(parser.lines))

def update_text():
    update_time = time.time()
    failed = False

    if not os.path.exists(save_path):
        os.makedirs(save_path) 

    for record in salon_records[-3:]:
        # print('FETCH', record, 'info')
        try:
            html = requests.get(zy_article_url + record[1]).text
            process_html(record[0], html)
        except Exception as e:
            # print('[ERROR] ', e)
            failed = True

    if not failed:        
        out_file = os.path.join(save_path, update_time_file)
        with open(out_file, 'w', encoding='utf8') as f: 
            f.write(str(update_time))

def get_map():
    sid_data = {}
    salons = {}
    sid_list_pattern = r'(\d+(\(\d+\))?、)*\d+(\(\d+\))?'
    sid_set = set()

    names = [x[0] for x in salon_records[-3:]]
    for name in names:
        # print('LOAD', name, 'data')
        in_file = os.path.join(save_path, salon_record_file % (name))
        sid_data[name] = []
        salons[name] = []
        with open(in_file, 'r', encoding='utf8') as f:
            for line in f.readlines():
                s = line.replace(' ', '').replace('\n', '').rstrip('、')
                if '.' in line:
                    title = line.strip('\n').strip(' ')
                    # print('  Loading salon', title)
                    salons[name].append(title)
                    sid_data[name].append([])
                else:
                    sid_list = s.split('、')
                    sid_data_now = []
                    for sid in sid_list:
                        sid_now = ''
                        count_now = 0
                        if '(' in sid:
                            sid_now = sid.split('(')[0]
                            count_now = int(sid.split('(')[1].replace(')', ''))
                        else:
                            sid_now = sid
                            count_now = 1
                        for i in range(count_now):
                            sid_data[name][-1].append(sid_now)
                        if sid_now not in sid_set:
                            sid_set.add(sid_now)
                    # sid_data[name].append(sid_data_now)

    stus = {}
    for sid in sid_set:            
        stu = UniObject()
        stu.count_zy = 0
        stu.count_other = 0
        stu.acts_zy = []
        stu.acts_other = []
        for name in names:
            for i in range(len(salons[name])):
                num = sid_data[name][i].count(sid)
                if num == 0:
                    continue
                if name not in other_set: 
                    stu.acts_zy.append((salons[name][i], num))
                    stu.count_zy += num
                else:
                    stu.acts_other.append((salons[name][i], num))
                    stu.count_other += num
        stus[sid] = stu
    return stus

def check_update_time(app):
    update_time = 0.0
    with open(os.path.join(save_path, 'update_time.text'), 'r', encoding='utf8') as f:
        update_time = float(f.read())
    
    u_time = time.localtime(update_time)
    now_time = time.time()
    n_time = time.localtime(now_time)
    failed = False
    if (u_time.tm_year, u_time.tm_mon, u_time.tm_mday, u_time.tm_hour, u_time.tm_min / 10) != (n_time.tm_year, n_time.tm_mon, n_time.tm_mday, n_time.tm_hour, n_time.tm_min / 10):
        try:
            # print('here')
            update_text()
            app.table = get_map()
            u_time = n_time
        except Exception as e:            
            failed = True
    if not failed:
        ret = time_str % (u_time.tm_year, u_time.tm_mon, u_time.tm_mday, u_time.tm_hour, u_time.tm_min, u_time.tm_sec)
    else:
        ret = 'Unknown'
    return ret

last_time=-1
def getTimes(id):
    id=str(id)

    update_text()
    table = get_map()
    if id not in table:
        return -1
    else:
        report = table[id]
        return report.count_zy + report.count_other

'''
id = input("enter you student id: ")
ans=getTimes(id)
if ans==-1 :
    print('ask error')
else:
    print('your times is '+str(ans))

example

from getTimes import getTimes

while True:
    id = input("enter you student id: ")
    ans=getTimes(id,3600)
    if ans==-1 :
        print('ask error')
    else:
        print('your times is '+str(ans))
'''