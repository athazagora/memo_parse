#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from bs4 import BeautifulSoup
# import requests
import re
import os

import parsepzk_common_functions
import parsepzk_prison_functions

import csv

def parse_tv_cvs(filename):
 
  results = []
  # with open(filename, 'r') as f:
  with open(filename, newline='') as csvfile:
    spamreader = csv.DictReader(csvfile)
    for row in spamreader:
      
      # .replace("\n", ""
      # print (row)
      # prisoner_bday = 
            
      bmonth = 0
      bday = 0
      if row['Дата рождения'] != '' :
        bday = re.sub('(\d+)\.\d+\.\d{4}'    , r'\1', row['Дата рождения'])
        # print (" month ", bmonth)
        bmonth = re.sub('\d+\.(\d+)\.\d{4}'      , r'\1', row['Дата рождения'])
        # print (" day ", bday)
        byear = re.sub('\d+\.\d+\.(\d{4})'      , r'\1', row['Дата рождения'])
        
      
      if row['Где сидит'] not in ['Освобожден', 'Домашний арест', 'Умер', 'Подписка о невыезде', 'Находится за границей', 'Запрет определенных действий', 'Ушел на СВО']:
        results.append({
            'prisoner_name': row['ФИО'],
            'prisoner_link': "",
            'prisoner_case': str(row['Категория']),
            'prisoner_addr': str(row['Где сидит']),
            'prisoner_desc': row['Обвинение'],
            'prisoner_male' : 2,
            'prisoner_bday': bday,
            'prisoner_bmonth': bmonth,
            'prisoner_byear': byear,
            'prisoner_grad': "",
            'prisoner_prison': ""
            })
      
  return results
  
def clean_tv_fields_from_exceed(prisoner_list):
  for field in prisoner_list:
    field['prisoner_addr'] = re.sub(r'Уточняется'                                    , r'уточняется'         , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Областная клиническая психиатрическая больница', r'ОКПБ'               , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН России по Луганской народной республике' , r'УФСИН по ЛНР'       , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'по Ханты-Мансийскому автономному округу-Югре ' , r'по ХМАО'            , field['prisoner_addr'])
  return prisoner_list

def top (fold_name, try_to_restore = 1):

  # url='https://airtable.com/appM0RUv3AZgjWJXX/shrLpdbgcdDjgPBOr/tbldEW4S6zyMPb8MZ'
  url = "tmp/Общая база политически преследуемых - Основная база.csv"
  prisoner_list = parse_tv_cvs(url)
  prisoner_list = parsepzk_common_functions.set_genrder_bit ( prisoner_list )
  prisoner_list = clean_tv_fields_from_exceed ( prisoner_list )
  
  # parsepzk_common_functions.print_simle_list( descr_journalist_list, 'markdown', os.path.join(fold_name, "journ_list.txt"))
  prison_list = parsepzk_prison_functions.create_prison_dict ( "parsepzk_prison_database.xls" )
  for i in prisoner_list :
    i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, 1)
    # print (i['prisoner_addr'])
      
  parsepzk_common_functions.print_bot_list( prisoner_list, 'markdown', os.path.join(fold_name, "tv_list.txt"))
  
