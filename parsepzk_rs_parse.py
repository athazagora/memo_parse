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

def parse_rs_cvs(filename):
 
  results = []
  # with open(filename, 'r') as f:
  with open(filename, newline='') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=';')
    for row in spamreader:
      
      # .replace("\n", ""
      # print (row)
      for field in row :
        row[field] = re.sub(r"\n", " ", row[field])
        row[field] = re.sub(r"\s{2,}", " ", row[field])
        
      # print (row)
        
      
      birth = re.findall(r',?\s?\d{0,2}\.?\d{0,2}\.?\d{4}\s?г?\.?р?\.?', row['ФИО'] )
      if len (birth) == 0 :
        print ("Not found berth in \"", row['ФИО'], "\"")
        birth = "0000"
      else :
        row['ФИО'] = re.sub(birth[0] , '', row['ФИО'])
        birth = re.sub(r'.*(\d{4})\s?г?\.?р?\.?', r'\1', birth[0]).strip()
        # return results
      # print (row['ФИО'], birth)
       
      results.append({
            'prisoner_name': row['ФИО'],
            'prisoner_link': "",
            'prisoner_case': str(row['Группа/год приговора']),
            'prisoner_addr': str(row['Место нахождения']),
            'prisoner_desc': row['Год ареста и  срок отбывания'],
            'prisoner_male' : 2,
            'prisoner_bday': 0,
            'prisoner_bmonth': 0,
            'prisoner_byear': birth,
            'prisoner_grad': "",
            'prisoner_prison': ""
            })
      
  return results
  
def clean_rs_fields_from_exceed(prisoner_list):
  # for field in prisoner_list:
    # field['prisoner_addr'] = re.sub(r'УФСИН по РБ'                                      , r'УФСИН по Республике Башкортостан'                 , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'УФСИН России по РТ'                               , r'УФСИН по Республике Татарстан'                    , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'УФСИН России по РМ'                               , r'УФСИН по Республике Мордовия'                     , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'УФСИН России по РК'                               , r'УФСИН по Республике Карелия'                      , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'УФСИН по ХМАО'                                    , r'УФСИН по ХМАО — Югре'                             , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'УФСИН России по ЯНАО'                             , r'УФСИН по Ямало-Ненецкому автономному округу'      , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'Томск (.*) ФСИН'                                  , r'Томск \1 УФСИН по Томской области'                , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'УФСИН России по Кабардино-Балкарской республики|УФСИН России по КБР'  , r'УФСИН по Кабардино-Балкарской республике'  , field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'«|»', r' ', field['prisoner_addr'])
  return prisoner_list


def top (fold_name, try_to_restore = 1):

  url = "tmp/roditelskaja_solidarnost.csv"
  prisoner_list = parse_rs_cvs(url)
  prisoner_list = parsepzk_common_functions.set_genrder_bit ( prisoner_list )
  # prisoner_list = clean_rs_fields_from_exceed ( prisoner_list )
  
  prison_list = parsepzk_prison_functions.create_prison_dict ( "parsepzk_prison_database.xls" )
  for i in prisoner_list :
    print (i['prisoner_addr'])
    i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, 0)
    print (i['prisoner_addr'])
      
  parsepzk_common_functions.print_bot_list( prisoner_list, 'markdown', os.path.join(fold_name, "rs_list.txt"))
  
