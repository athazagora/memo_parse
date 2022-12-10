#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re

import argparse
import os
from datetime import datetime

import parsepzk_common_functions



def parse_prisoner_link(url):
  
  r = requests.get(url)
  r.encoding = r.apparent_encoding
  
  soup = BeautifulSoup(r.text, 'html.parser')
  # <div class="p24 fw4 lh17 fs14">
  prisoner_desc = soup.find('div', {'class': 'p24 fw4 lh17 fs14'})
  if prisoner_desc : prisoner_desc=prisoner_desc.text.replace(r'^\n$', '')
  # print (prisoner_desc)
   
  prisoner_case = []
  # <div class="fs14 fw6 ttu cw fw7 tac pa b0 l0 bgcy py8 px24">В ЗАКЛЮЧЕНИИ</div>
  case_item = soup.find('div', {'class': 'fs14 fw6 ttu cw fw7 tac pa b0 l0 bgcy py8 px24'})
  if case_item : case_item = case_item.text
  prisoner_case.append (case_item)
  
  prisoner_bday = 0
  prisoner_bmonth = 0
  prisoner_byear = 0
  # <div><div class="bgcw p24 bs1 bt btw4 btco br5"><h2 class="fs18 fw8 cdi mb16 ttu">Краткая информация</h2>
  tmp_conteiner=soup.find_all('div', {'class': 'bgcw p24 bs1 bt btw4 btco br5'})
  # print (tmp_conteiner)
  for tmp in tmp_conteiner:
    # <a class="fs12 tdu cli" 
    prisoner_addr = tmp.find('a', {'class': 'fs12 tdu cli'})
    if prisoner_addr : prisoner_addr = prisoner_addr.text
    # print (prisoner_addr)
    
    # <div class="r aic"><div class="i0 miw100 maw100"><div class="fs12 fw6">Дата рождения</div></div>
    items = tmp.find_all('div', {'class': 'r aic'})
    for item in items :
      if 'Статья' in item.text: 
        case_item = item.text.split("\n")[1]
        prisoner_case.append (case_item)
        
      if 'Статус' in item.text: 
        case_item = item.text.split("\n")[1]
        prisoner_case.append (case_item)
        
      if 'Дата рождения' in item.text:
        prisoner_date = item.text.split("\n")[1].split('/')
        if len(prisoner_date) == 3:
          prisoner_bday = prisoner_date[0]
          prisoner_bmonth = prisoner_date[1]
          prisoner_byear = prisoner_date[2]

  print (prisoner_case)

  return { 'prisoner_desc': prisoner_desc, 'prisoner_addr': prisoner_addr, 'prisoner_case' : prisoner_case, 
           'prisoner_bday': prisoner_bday, 'prisoner_bmonth': prisoner_bmonth, 'prisoner_byear': prisoner_byear } 

def parse_krym_url(url):
  results = []
  
  r = requests.get(url)
  r.encoding = r.apparent_encoding
  
  soup = BeautifulSoup(r.text, 'html.parser')
  # <div class="i6-S i4-X">
  items = soup.find_all('div', {'class': 'i6-S i4-X'})
  # print (items)
    
  for item in items:
    # <div class="fs14 fw7 lh12 mt28 mb24 tac df jcc">
    prisoner_name = item.find('div', {'class': 'fs14 fw7 lh12 mt28 mb24 tac df jcc'}).text
    print (prisoner_name)
    
    # <a class="db tdn-hf h100p" href="polit-prisoners/profile/krosh--enver-131">
    prisoner_link = item.find('a', {'class': 'db tdn-hf h100p'}).get('href')
    prisoner_link = re.sub(r'/$', '', prisoner_link)
    prisoner_link = "https://crimean-solidarity.org/"+prisoner_link
    prisoner_intro = parse_prisoner_link(prisoner_link)
    
    results.append({
            'prisoner_name': prisoner_name,
            'prisoner_link': prisoner_link,
            'prisoner_case': str(prisoner_intro['prisoner_case']),
            'prisoner_addr': str(prisoner_intro['prisoner_addr']),
            'prisoner_desc': str(prisoner_intro['prisoner_desc']),
            'prisoner_male' : 2,
            'prisoner_bday': str(prisoner_intro['prisoner_bday']),
            'prisoner_bmonth': str(prisoner_intro['prisoner_bmonth']),
            'prisoner_byear': str(prisoner_intro['prisoner_byear']),
            'prisoner_grad': ""
            })
  return results


def month_list_maker_function(url, month, file_name=None):
  print ( url )
  prisoner_list = get_list_function (url, file_name)
  month_list = parsepzk_common_functions.get_one_month_list (prisoner_list, month)
  print_list(month_list,'markdown', file_name)
  return 0

def bot_description_maker_function(url, file_name=None):
  print ( url )
  prisoner_list = get_list_function (url)
  
  f = open(file_name, 'w')
  for field in prisoner_list: 
    print ("[" + field['prisoner_name'] + "]")
  f.close()
  
  return 0
  


parser = argparse.ArgumentParser(description="Example of a single flag acting as a boolean and an option.")
parser.add_argument('--month', nargs='+', default=False)
parser.add_argument('--full_list', nargs='?', const="full_list", default=False)
parser.add_argument('--descr', nargs='?', const="descr", default=False)

args = parser.parse_args()

polit_url='https://crimean-solidarity.org/polit-prisoners'

if args.month:
  for one_month in args.month:
    file_name = "month_" + one_month + "_list_" + datetime.strftime(datetime.today(), "%Y.%m.%d") + ".txt"
    print("Generate list for month " + one_month + " to file \"" + file_name + "\"")
    month_list_maker_function(polit_url, one_month, file_name)
else:
  if args.full_list:
    print(args.full_list)
    fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
    if not os.path.exists(fold_name): os.makedirs(fold_name)
    print("Generate list to folder \"" + fold_name + "\"")
    full_list=parse_krym_url(polit_url)
    
    prisoner_list = [ i for i in full_list if 'ОСУЖДЕН' in i['prisoner_case'] or 'В ЗАКЛЮЧЕНИИ' in i['prisoner_case'] ]
    prisoner_list.sort(key=lambda day: day['prisoner_name'])
    # for i in prisoner_list:
       
    # prisoner_list = parsepzk_common_functions.set_genrder_bit ( prisoner_list )
    # prisoner_list = parsepzk_common_functions.clean_fields_from_exceed ( prisoner_list )
  
    parsepzk_common_functions.print_bot_list(prisoner_list, 'markdown', os.path.join(fold_name, "krymsol_list.txt"))
  if args.descr:
    print(args.descr)
    fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
    if not os.path.exists(fold_name): os.makedirs(fold_name)
    print("Generate descr to folder \"" + fold_name + "\"")
    bot_description_maker_function(polit_url, os.path.join(fold_name, "krymsol_descr_polit_list.txt"))

  
