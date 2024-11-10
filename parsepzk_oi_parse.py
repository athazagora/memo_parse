#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from bs4 import BeautifulSoup
# import requests
import re
import os

import parsepzk_common_functions
import parsepzk_prison_functions

# import pickle
import csv

def parse_ovdinfo_cvs(filename):
 
  results = []
  # with open(filename, 'r') as f:
  with open(filename, newline='') as csvfile:
    spamreader = csv.DictReader(csvfile)
    for row in spamreader:
      
      # .replace("\n", ""
      # print (row)
      
      if row['Колония (актуальная)'] != '' :
        row['СИЗО (актуальное)'] = row['Колония (актуальная)']
      
      if row ['СИЗО (актуальное)'] == '' :
        row['СИЗО (актуальное)'] = row['Где находится']
       
      row['СИЗО (актуальное)'] = re.sub(r"\n|\|", "", row['СИЗО (актуальное)'])
      row['Колония (актуальная)'] = re.sub(r"\n|\|", "", row['Колония (актуальная)'])
      # print (row['СИЗО (актуальное)'] )
      
      bmonth = 0
      bday = 0
      if row['Дата рождения'] != '' :
        bmonth = re.sub('(\d+)\/\d+\/\d{4}'    , r'\1', row['Дата рождения'])
        # print (" month ", bmonth)
        bday = re.sub('\d+\/(\d+)\/\d{4}'      , r'\1', row['Дата рождения'])
        # print (" day ", bday)
        
  
      
      results.append({
            'prisoner_name': row['ФИО'],
            'prisoner_link': "",
            'prisoner_case': str(row['Статьи']),
            'prisoner_addr': str(row['СИЗО (актуальное)']),
            'prisoner_desc': row['История'],
            'prisoner_male' : 2,
            'prisoner_bday': bday,
            'prisoner_bmonth': bmonth,
            'prisoner_byear': str(row['Год рождения']),
            'prisoner_grad': "",
            'prisoner_prison': ""
            })
      
  return results
  
def clean_oi_fields_from_exceed(prisoner_list):
  for field in prisoner_list:
    field['prisoner_addr'] = re.sub(r'УФСИН по РБ'                                      , r'УФСИН по Республике Башкортостан'                 , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН России по РТ'                               , r'УФСИН по Республике Татарстан'                    , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН России по РМ'                               , r'УФСИН по Республике Мордовия'                     , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН России по РК'                               , r'УФСИН по Республике Карелия'                      , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН по ХМАО'                                    , r'УФСИН по ХМАО — Югре'                             , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН России по ЯНАО'                             , r'УФСИН по Ямало-Ненецкому автономному округу'      , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН по РСЯ'                                     , r'УФСИН по Республике Саха (Якутия)'                , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Томск (.*) ФСИН'                                  , r'Томск \1 УФСИН по Томской области'                , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'УФСИН России по Кабардино-Балкарской республики|УФСИН России по КБР'  , r'УФСИН по Кабардино-Балкарской республике'  , field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'«|»', r' ', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Этап', r'этап', field['prisoner_addr'])
  return prisoner_list


def top (fold_name, try_to_restore = 1):

  # url='https://airtable.com/appM0RUv3AZgjWJXX/shrLpdbgcdDjgPBOr/tbldEW4S6zyMPb8MZ'
  url = "tmp/МЛС_Свобот.csv"
  prisoner_list = parse_ovdinfo_cvs(url)
  prisoner_list = parsepzk_common_functions.set_genrder_bit ( prisoner_list )
  # prisoner_list = parsepzk_common_functions.catch_birth_date ( prisoner_list )
  prisoner_list = clean_oi_fields_from_exceed ( prisoner_list )
  
  # parsepzk_common_functions.print_simle_list( descr_journalist_list, 'markdown', os.path.join(fold_name, "journ_list.txt"))
  prison_list = parsepzk_prison_functions.create_prison_dict ( "parsepzk_prison_database.xls" )
  for i in prisoner_list :
    i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, 1)
    # print (i['prisoner_addr'])
      
  parsepzk_common_functions.print_bot_list( prisoner_list, 'markdown', os.path.join(fold_name, "oi_list.txt"))
  
