#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import random
##import RPi.GPIO as GPIO
##import wiringpi2 as wiringpi
import sys
import csv
##import Adafruit_PCA9685
import time
import itertools
from itertools import combinations
from collections import Counter
import wx
import datetime
import pickle
import xlwt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
import warnings
warnings.filterwarnings('ignore')
import wx.lib.agw.flatnotebook as fnb
from multiprocessing import Process, Value, Array, Queue
from threading import (Event, Thread)
import datetime

print datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
# 初期化(普段はコメントアウト)
f = file('log.dump', 'w')
# parametor[-1] = [today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue()]
parametor = [[u"日付(年)", "", "", 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, ""], [
    u"日付(年)", "", "", 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, ""]]
pickle.dump(parametor, f)
f.close()
f = file('senbetu_log.dump', 'w')
senbetu_parametor = [[u"日付(年)", "", "", 0.0, 0.0, 0.0, 0, 0.0, 0.0, ""], [
    u"日付(年)", "", "", 0.0, 0.0, 0.0, 0, 0.0, 0.0, ""]]  # parametor[-1] = [today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue()]
pickle.dump(senbetu_parametor, f)
f.close()
f = file('set.dump', 'w')
setting = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,
           25, 200, 210, 195, 500, 800, 1, 15, 0, 20, 40, 60, 80, 800, 1]
# setting[16]からsetting[30]がsetting
pickle.dump(setting, f)
f.close()

#setting[16]#停止(秒)
#setting[17]平均重量(g)
#setting[18]上限重量(g)
#setting[19]下限重量(g)
#setting[20]#市場価格(円/kg)
#setting[21]#人件費(円/h)
#setting[22]#作業者数(人)
#senbetu_s_text 停止(秒) setting[23]
#senbetu_s_text_S S setting[24]
#senbetu_s_text_S S setting[25]
#senbetu_s_text_M M setting[26]
#senbetu_s_text_L L setting[27]
#senbetu_s_text_2L 2L setting[28]
#setting[29]#人件費(円/h)
#setting[30]#作業者数(人)

table_code=0
senbetu_table_code=0

# fp = FontProperties(fname=r'C:\Users\2140022\Desktop\プログラム\ipaexg.ttf', size=14)#'C:\Users\USER\Downloads\ipaexg.ttf'
x_plot = [1]
y_plot = [0]
final_sumweight_a = 0
final_sumweight_b = 0
final_sumweight_c = 0
final_sumweight_d = 0
x_bar = [1, 2, 3, 4]
g = file('set.dump', 'r')
setting = pickle.load(g)
# 計量されたテーブルNo
table_num = []
# テーブルごとの計量結果
table_weight = []
i = 0
count = 0  # counter for user
NGcount = 0
g.close()

# switch onで、190g以下の時の処理
discharge_list_a = []
discharge_list_b = []
discharge_list_c = []
discharge_list_d = []
discharge_i = 10
discharge_a_offset = True
discharge_b_offset = True
discharge_c_offset = True
discharge_d_offset = True
spare_num_a = []
spare_num_b = []
spare_num_c = []
spare_num_d = []
spare_i = 0
spare_sumweight_a = []
spare_sumweight_b = []
spare_sumweight_c = []
spare_sumweight_d = []
numbering = 0
senbetu_discharge_list_a = []
senbetu_discharge_list_b = []
senbetu_discharge_list_c = []
senbetu_discharge_list_d = []
table_code = 0  # 各テーブルの番号
mode_switch = True  # Trueなら組み合わせ、Falseなら選別のモード

final_sumweight = [0,0,0,0]

kumiawase_event = Event()
senbetu_event = Event()

working_sec_sw=False
senbetu_working_sec_sw=False




def choice():  # 4 dischargers
    # リセット
    sum_table_weight = []
    allcombi_num = []
    allcombi_weight = []
    allcombi_weight_dif = []  # allcombi_weight_dif=[204.78022541534693, 88.19455714403786, 84.85081941624652, 31.734848855062552, 113.21724615959693, 3.3684221117121638, 6.712159839503499, 123.29782811081253, 84.85042555351703, 31.73524271779206, 35.0789804455834, 151.6646487168925, 6.712553702232981, 123.29822197354207, 126.6419597013334, 243.22762797264244, 123.55823768144668, 6.972569410137623, 3.628831682346288, 112.9568365889628, 31.995258425696676, 84.59040984561244, 87.93414757340378, 204.5198158447128, 3.628437819616778, 112.95723045169228, 116.30096817948362, 232.88663645079276, 87.9345414361332, 204.52020970744235, 207.86394743523368, 324.4496157065427, 119.66939029119577, 3.083722019886693, 0.26001570790464257, 116.84568397921373, 28.106411035445774, 88.47925723586332, 91.82299496365465, 208.40866323496368, 0.26040957063412407, 116.84607784194321, 120.18981556973455, 236.77548384104364, 91.82338882638413, 208.40905709769322, 211.75279482548456, 328.33846309679365, 38.447402557295504, 78.13826571401353, 81.48200344180486, 198.06767171311395, 53.115576698454504, 169.7012449697636, 173.04498269755493, 289.63065096886396, 81.4823973045344, 198.06806557584343, 201.41180330363477, 317.997471574944, 173.04537656028435, 289.6310448315935, 292.97478255938483, 409.5604508306939]
    allcombi_weight_dif_order = []
    # allcombi_order=[[4, 5], [2, 3], [3, 4], [0, 1], [2, 5], [0, 4], [1, 5], [1, 4]]
    allcombi_order = []
    leftover_order_allcombi = []
    table_num_2 = []
    n = 0  # n=4
    combi_num = []
    combi_weight_a = []
    combi_weight_b = []
    combi_weight_c = []
    combi_weight_d = []
    global NGcount
    error_count = 0
    global table_num
    global table_weight
    global spare_num_a
    global spare_num_b
    global spare_num_c
    global spare_num_d
    global spare_sumweight_a
    global spare_sumweight_b
    global spare_sumweight_c
    global spare_sumweight_d
    global i
    global spare_i
    global today_weight
    global today_qty
    global setting

    spare_i = i

    # print "組合せ計算中"
    # べき集合の関数
    def powerset(s):
        return [[s[j] for j in xrange(len(s)) if (i & (1 << j))] for i in xrange(1 << len(s))]
    # 全組合せのNumとweightのlist作成
    allcombi_num = powerset(table_num)
    allcombi_weight = powerset(table_weight)
    # 全組合せweightと目標値の差分のlist作成
    sum_table_weight = sum(table_weight)  # sum_table_weight=614.340676246
    for j in allcombi_weight:
        allcombi_weight_dif.append(abs(sum(j) - setting[17]))

    allcombi_weight_dif_allorder = sorted(
        range(len(allcombi_weight_dif)), key=allcombi_weight_dif.__getitem__)
    for j in allcombi_weight_dif_allorder:
        allcombi_order.append(allcombi_num[j])
        
    def flatten(nested_list):
        """2重のリストをフラットにする関数"""
        return [e for inner_list in nested_list for e in inner_list]

    table_num_1 = table_num[:]

    #'4th start'
    lst = list(combinations(allcombi_order[:15], 4))
    # print lst
    for j in lst:
        f = flatten(j)
        # print f
        if [key for key, val in Counter(f).items() if val > 1] == [] :#かぶりなし、抜けなし
            # print '4th start'
            combi_num = list(j)

            while True:
                if table_num[0] in combi_num[0] or table_num[-1] in combi_num[3]:
                    random.shuffle(combi_num)
                else:
                    break
            
            print combi_num

            for j in combi_num[0]:
                combi_weight_a.append(table_weight[j])
            for j in combi_num[1]:
                combi_weight_b.append(table_weight[j])
            for j in combi_num[2]:
                combi_weight_c.append(table_weight[j])
            for j in combi_num[3]:
                combi_weight_d.append(table_weight[j])

            if sum(combi_weight_a) < setting[19] or sum(combi_weight_a) > setting[18]:
                error_count += 1
            if sum(combi_weight_b) < setting[19] or sum(combi_weight_b) > setting[18]:
                error_count += 1
            if sum(combi_weight_c) < setting[19] or sum(combi_weight_c) > setting[18]:
                error_count += 1
            if sum(combi_weight_d) < setting[19] or sum(combi_weight_d) > setting[18]:
                error_count += 1

            if error_count == 0:
                spare_num_a = combi_num[0]
                spare_num_b = map(lambda n: n + 1, combi_num[1])
                spare_num_c = map(lambda n: n + 2, combi_num[2])
                spare_num_d = map(lambda n: n + 3, combi_num[3])
                spare_sumweight_a = sum(combi_weight_a)
                spare_sumweight_b = sum(combi_weight_b)
                spare_sumweight_c = sum(combi_weight_c)
                spare_sumweight_d = sum(combi_weight_d)
                print 'combi'
                print(combi_num)
                print"a"
                print(spare_sumweight_a)
                print(spare_sumweight_b)
                print(spare_sumweight_c)
                print(spare_sumweight_d)
                print"d"
                g = file('log.dump', 'r')
                parametor = pickle.load(g)
                parametor[-1][3] += 4
                parametor[-1][4] += (spare_sumweight_a + spare_sumweight_b +
                                 spare_sumweight_c + spare_sumweight_d) / 1000
                g.close()
                
                f = file('log.dump', 'w')
                pickle.dump(parametor, f)
                f.close()

            elif error_count > 1:
                combi_num = []
                combi_weight_a = []
                combi_weight_b = []
                combi_weight_c = []
                combi_weight_d = []
                error_count = 0
                
                print '3rd start'
                # lst=[((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3)), ((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)), ((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 2, 4)), ((0, 1, 2), (0, 1, 4), (0, 2, 3), (0, 2, 4)), ((0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4))]
                lst = list(combinations(allcombi_order[:15], 3))
                # print lst
                for j in lst:
                    f = flatten(j)
                    # print f
                    if [key for key, val in Counter(f).items() if val > 1] == []:
                        combi_num = list(j)
                
                        while True:
                            if table_num[0] in combi_num[0]:
                                random.shuffle(combi_num)
                            else:
                                break
                                    
                        print combi_num
                
                        for j in combi_num[0]:
                            combi_weight_a.append(table_weight[j])
                        for j in combi_num[1]:
                            combi_weight_b.append(table_weight[j])
                        for j in combi_num[2]:
                            combi_weight_c.append(table_weight[j])
                
                        if sum(combi_weight_a) < setting[19] or sum(combi_weight_a) > setting[18]:
                            error_count += 1
                        if sum(combi_weight_b) < setting[19] or sum(combi_weight_b) > setting[18]:
                            error_count += 1
                        if sum(combi_weight_c) < setting[19] or sum(combi_weight_c) > setting[18]:
                            error_count += 1
                
                        if error_count == 0:
                            spare_num_a = combi_num[0]
                            spare_num_b = map(lambda n: n + 1, combi_num[1])
                            spare_num_c = map(lambda n: n + 2, combi_num[2])
                            spare_num_d = []
                            spare_sumweight_a = sum(combi_weight_a)
                            spare_sumweight_b = sum(combi_weight_b)
                            spare_sumweight_c = sum(combi_weight_c)
                            spare_sumweight_d = 0
                
                            print 'combi'
                            print(combi_num)
                            # print 'spare_num_d'
                            #print (spare_num_d)
                            print "a"
                            print(spare_sumweight_a)
                            print(spare_sumweight_b)
                            print(spare_sumweight_c)
                            print "c"
                
                            g = file('log.dump', 'r')
                            parametor = pickle.load(g)
                            parametor[-1][3] += 3
                            parametor[-1][4] += (spare_sumweight_a +
                                             spare_sumweight_b + spare_sumweight_c) / 1000
                            g.close()
                            
                            f = file('log.dump', 'w')
                            pickle.dump(parametor, f)
                            f.close()
        
                        elif error_count > 1:
                            combi_num = []
                            combi_weight_a = []
                            combi_weight_b = []
                            combi_weight_c = []
                            error_count = 0
                            # print '2nd start'
                            # lst=[((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3)), ((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)), ((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 2, 4)), ((0, 1, 2), (0, 1, 4), (0, 2, 3), (0, 2, 4)), ((0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4))]
                            lst = list(combinations(allcombi_order[:15], 2))
                            # print lst
                            for j in lst:
                                f = flatten(j)
                                # print f
                                if [key for key, val in Counter(f).items() if val > 1] == []:
                                    combi_num = list(j)
                                    print combi_num
                        
                                    for j in combi_num[0]:
                                        combi_weight_a.append(table_weight[j])
                                    for j in combi_num[1]:
                                        combi_weight_b.append(table_weight[j])
                        
                                    if sum(combi_weight_a) < setting[19] or sum(combi_weight_a) > setting[18]:
                                        error_count += 1
                                    if sum(combi_weight_b) < setting[19] or sum(combi_weight_b) > setting[18]:
                                        error_count += 1
                                    if error_count == 0:
                                        spare_num_a = combi_num[0]
                                        spare_num_b = map(lambda n: n + 1, combi_num[1])
                                        spare_num_c = []
                                        spare_num_d = []
                                        spare_sumweight_a = sum(combi_weight_a)
                                        spare_sumweight_b = sum(combi_weight_b)
                                        spare_sumweight_c = 0
                                        spare_sumweight_d = 0
                                        print 'combi'
                                        print(combi_num)
                                        print(spare_sumweight_a)
                                        print(spare_sumweight_b)
                                        g = file('log.dump', 'r')
                                        parametor = pickle.load(g)
                                        parametor[-1][3] += 2
                                        parametor[-1][4] += (spare_sumweight_a + spare_sumweight_b) / 1000
                                        g.close()
                                        
                                        f = file('log.dump', 'w')
                                        pickle.dump(parametor, f)
                                        f.close()
                                    
                                    elif error_count > 1:
                                        combi_num = []
                                        combi_weight_a = []
                                        combi_weight_b = []
                                        combi_weight_c = []
                                        error_count = 0
                                        # print '1st start'
                                        combi_num = allcombi_order[0]
                                        print combi_num
                            
                                        for j in combi_num:
                                            combi_weight_a.append(table_weight[j])
                            
                                        if sum(combi_weight_a) < setting[19] or sum(combi_weight_a) > setting[18]:
                                            error_count += 1
                                        if error_count == 0:
                                            spare_num_a = combi_num[0]
                                            spare_num_b = []
                                            spare_num_c = []
                                            spare_num_d = []
                                            spare_sumweight_a = sum(combi_weight_a)
                                            spare_sumweight_b = 0
                                            spare_sumweight_c = 0
                                            spare_sumweight_d = 0
                                            print 'combi'
                                            print(combi_num)
                                            print(spare_sumweight_a)
                                            g = file('log.dump', 'r')
                                            parametor = pickle.load(g)
                                            parametor[-1][3] += 1
                                            parametor[-1][4] += spare_sumweight_a  / 1000
                                            g.close()
                                            
                                            f = file('log.dump', 'w')
                                            pickle.dump(parametor, f)
                                            f.close()
                        
        



def measure():
    global weight
    global setting
    weight = random.uniform(1, 220) 


if __name__ == '__main__':
    i=0
    for j in range(300):
        measure()
        print weight
        table_num.append(i)
        i += 1
        table_weight.append(weight)
        if i>=9:
            print "choice start"
            choice()
#            count += 1
            table_num = []
            table_weight = []
            i=0

        j+=1
