#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re

import argparse
import os
from datetime import datetime

import memo_parse_functions



def parse_prisoner_link(url):
  
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  #  <div class="human-dossier__art">
  prisoner_desc = soup.find('div', {'class': 'human-dossier__art'}).text
  
  prisoner_addr = "no addr"
  # <div class="modal modal--preload modal--no-scale modal--fit-content modal--side" data-modal="letter">
  tmp_conteiner = soup.find('div', {'class': 'modal modal--preload modal--no-scale modal--fit-content modal--side'})
  if tmp_conteiner:
    tmp_conteiner = tmp_conteiner.text.split("Написать письмо\n")
    if len(tmp_conteiner) > 1: prisoner_addr = tmp_conteiner[1].split("\n", 1)[0]
  # print (prisoner_addr)
  
  return { 'prisoner_desc': prisoner_desc, 'prisoner_addr': prisoner_addr } 

def parse_memo_url(url):
  results = []
  r = requests.get(url)
    
  soup = BeautifulSoup(r.text, 'html.parser')
  # <li class="card-news-tags dossier__card">
  items = soup.find_all('li', {'class': 'card-news-tags dossier__card'})
  # print (items)
  for item in items:
    prisoner_name = item.find('div', {'class': 'card-news-tags__title'}).text
    print (prisoner_name)
    prisoner_link = item.find('a', {'class': 'card-news-tags__invisible-link'}).get('href')
    # print (prisoner_link)
    
    # prisoner_case = get_class_content (item, 'teaser__cases', 'a', "инд")
    results.append({
            'prisoner_name': prisoner_name,
            'prisoner_link': prisoner_link,
            # 'prisoner_case': prisoner_case,
            'prisoner_addr': str(parse_prisoner_link(prisoner_link)['prisoner_addr']),
            'prisoner_desc': str(parse_prisoner_link(prisoner_link)['prisoner_desc']),
            'prisoner_male' : 2,
            'prisoner_bday': 0,
            'prisoner_bmonth': 0,
            'prisoner_byear': 0,
            'prisoner_grad': ""
            })
  return results
  
def print_bot_list(p_list, print_format='', file_name=None):
  if file_name != None: f = open(file_name, 'w')
  for field in p_list: 
    if print_format == 'markdown' :
      name = f"[{field['prisoner_name']}]({field['prisoner_link']})"
    else:
      if print_format == '' :
        name = field['prisoner_name']
    # print (name + "- "+field['prisoner_addr'] )
    print (name, "`"+memo_parse_functions.print_date(field)+" г.р.` :addr_delim:", field['prisoner_grad'], ":addr_delim:", field['prisoner_addr'], file=f)
  if file_name != None: f.close()


def get_list_function(url):
  prisoner_list = []
  page = ["not_empty"]
  i=1
  while len(page) != 0:
  # if 1:
    page = []
    print ("page ", i)
    page = parse_memo_url(url+str(i))
    prisoner_list += page
    i+=1
  else:
    print(f'Набралось {i} страниц')
  
  prisoner_list = memo_parse_functions.set_genrder_bit ( prisoner_list )
  prisoner_list = memo_parse_functions.catch_birth_date ( prisoner_list )
  prisoner_list = memo_parse_functions.clean_fields_from_exceed ( prisoner_list )
  
  return prisoner_list


def month_list_maker_function(url, month, file_name=None):
  print ( url )
  prisoner_list = get_list_function (url, file_name)
  month_list = get_one_month_list (prisoner_list, month)
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

polit_url='https://memopzk.org/list-persecuted/spisok-politzaklyuchyonnyh-bez-presleduemyh-za-religiyu/page/'
relig_url='https://memopzk.org/list-persecuted/spisok-politzaklyuchyonnyh-presleduemyh-za-religiyu/page/'
probo_url='https://memopzk.org/list-persecuted/veroyatnye-zhertvy-ne-voshedshie-v-spiski/page/'


if args.month:
  for one_month in args.month:
    file_name = "month_" + one_month + "_list_" + datetime.strftime(datetime.today(), "%Y.%m.%d") + ".txt"
    print("Generate list for month " + one_month + " to file \"" + file_name + "\"")
    month_list_maker_function(polit_url, one_month, file_name)
    month_list_maker_function(relig_url, one_month, file_name)
    month_list_maker_function(probo_url, one_month, file_name)
else:
  if args.full_list:
    print(args.full_list)
    fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
    if not os.path.exists(fold_name): os.makedirs(fold_name)
    print("Generate list to folder \"" + fold_name + "\"")
    print_bot_list(get_list_function(polit_url), 'markdown', os.path.join(fold_name, "polit_list.txt"))
    print_bot_list(get_list_function(relig_url), 'markdown', os.path.join(fold_name, "prob_list.txt"))
    print_bot_list(get_list_function(probo_url), 'markdown', os.path.join(fold_name, "relig_list.txt"))
  if args.descr:
    print(args.descr)
    fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
    if not os.path.exists(fold_name): os.makedirs(fold_name)
    print("Generate descr to folder \"" + fold_name + "\"")
    bot_description_maker_function(polit_url, os.path.join(fold_name, "descr_polit_list.txt"))
    bot_description_maker_function(probo_url, os.path.join(fold_name, "descr_prob_list.txt"))
    bot_description_maker_function(relig_url, os.path.join(fold_name, "descr_relig_list.txt"))   

  
