# coding=UTF-8

import requests
import math
import re
import time
import json
import pymysql

from pyquery import PyQuery as pq


def findJijinName(code):
    res = requests.get(
        "http://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?callback=jQuery18305633066860360876_1505491078607&m=1&key=" + code + "&_=1505491085173")
    # print(res.text)
    js=json.loads(re.findall(r"jQuery\d+_\d+\((.*)\)", res.text)[0])
    return (js['Datas'][0]['NAME']);


def findHtml(code, start_day, end_day):
    res = requests.get(
        "http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=" + code + "&page=1&per=5000&sdate=" + start_day + "&edate=" + end_day + "&rt=0.7972726072734566")
    #print(res.text)
    return re.findall(r"content\:\"(.*)\",records", res.text)[0]

def calc_some_one(code,once_money,start_day,end_day):
    fund_name=findJijinName(code)
    print('基金名称[%s]：%s,单次购买:%s元, 开始时间:%s,结束时间:%s'%(str(code),fund_name,once_money,start_day,end_day))
    p=pq(findHtml(code,start_day,end_day))

    td_list=p("tbody tr td:lt(3)")
    my_list = [([0] * 3) for i in range(int(len(td_list)/3))]

    if len(td_list)==1:
       print('\t暂无数据')
       return

    for a in range(len(td_list)):
        my_list[math.floor(a/3)][a%3]=p(td_list[a]).html()

    price_now=my_list[0][1]

    def calc(buy_day):
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='fund_db',charset='utf8')
        conn.encoding='UTF-8'
        cursor = conn.cursor()
        sql_basic="insert into fund_basic(fund_code,fund_name,today,dot,price,price_addtion,earn_per,cost_all,now_all)\n"
        sql_basic+=" values('%s','%s','%s','%s','%s',%s,%s,%s,%s)"
        dics=['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
        dot = 0
        buy_time = 0
        my_list.reverse()

        for dt, price,price_addtion in my_list:
            st = time.strptime(dt, "%Y-%m-%d")
            if buy_day==-1 or st.tm_wday == buy_day:
                dot += once_money / float(price)
                buy_time += 1
                now_all = dot * float(price_addtion)
                cost_all = buy_time * float(once_money)
                earn_per = (now_all - cost_all) * 100 / cost_all
                sql_exec=sql_basic%(code, fund_name, dt,dot, price,price_addtion, earn_per,  cost_all,now_all)
                print(sql_exec)
                cursor.execute(sql_exec)
        now_all=dot*float(price_now)
        cost_all=buy_time*once_money
        earn_per=(now_all-cost_all)*100/cost_all

        conn.commit()
        cursor.close()
        conn.close()
        print("\t%s购买,总共购买了%s次，花费%s元，现在总额为%.2f元,盈利%.2f%%"%(dics[buy_day],buy_time,cost_all,now_all,earn_per))

    calc(-1)
    # for index in range(5):
    #     calc(index)

    print('\n')

codes=["000527","519091","519674","001244","001335","202005","160813","400025","001179","001927","590006","001897","233011","002340","100056","000877","002653","570001","001972","002666","519672","519674","481013","481008","110022","001104","001651","001878","000988","000307","000216","161124","400030","000047","233012","004614","004615","000045"]
for c in codes :
    calc_some_one(c, 200, '2014-09-15', '2017-09-15')
    # calc_some_one(c, 200, '2014-09-15', '2015-09-15')
    # calc_some_one(c, 200, '2015-09-15', '2016-09-15')
    # calc_some_one(c, 200, '2016-09-15', '2017-09-15')
