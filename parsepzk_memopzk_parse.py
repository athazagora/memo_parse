#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re
import os

import parsepzk_common_functions


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
    if len(tmp_conteiner) > 1: 
      prisoner_addr = re.sub("^\s+|\n|\r|\s+$", '', tmp_conteiner[1])
      # tmp_conteiner[1].split("\n", 1)[0]
  # print (prisoner_addr)
  
  # <div class="clause">
  prisoner_case=[]
  tmp_conteiner = soup.find('div', {'class': 'clause'})
  # print (tmp_conteiner)
  if tmp_conteiner:
    tmp_conteiner = tmp_conteiner.text.split("Статья УК:")
    for item in tmp_conteiner[1:]:
      if len(item) > 1: item = item.split("\n")
      for i in item:
        if len(i) > 1: prisoner_case.append (i)
  # print (prisoner_case)
  
  return { 'prisoner_desc': prisoner_desc, 'prisoner_addr': prisoner_addr, 'prisoner_case' : prisoner_case } 

def parse_memo_url(url):
  results = []
  r = requests.get(url)
  
  soup = BeautifulSoup(r.text, 'html.parser')
  # <li class="card-news-tags dossier__card">
  items = soup.find_all('li', {'class': 'card-news-tags dossier__card'})
    
  for item in items:
    prisoner_name = item.find('div', {'class': 'card-news-tags__title'}).text
    print (prisoner_name)
    prisoner_link = item.find('a', {'class': 'card-news-tags__invisible-link'}).get('href')
    prisoner_link = re.sub(r'/$', '', prisoner_link)
    prisoner_intro = parse_prisoner_link(prisoner_link)
    
    results.append({
            'prisoner_name': prisoner_name,
            'prisoner_link': prisoner_link,
            'prisoner_case': str(prisoner_intro['prisoner_case']),
            'prisoner_addr': str(prisoner_intro['prisoner_addr']),
            'prisoner_desc': str(prisoner_intro['prisoner_desc']),
            'prisoner_male' : 2,
            'prisoner_bday': 0,
            'prisoner_bmonth': 0,
            'prisoner_byear': 0,
            'prisoner_grad': ""
            })
  return results
  
def parse_memo_tag_url(url):
  results = []
  r = requests.get(url)
  
  soup = BeautifulSoup(r.text, 'html.parser')
  # <li class="card-news-tags archive__card tax__card">
  items = soup.find_all('li', {'class': 'card-news-tags archive__card tax__card'})
  
  for item in items:
    prisoner_name = item.find('a', {'class': 'card-news-tags__title'}).text
    # print (prisoner_name)
    prisoner_link = item.find('a', {'class': 'card-news-tags__invisible-link'}).get('href')
    prisoner_link = re.sub(r'/$', '', prisoner_link)
    # re.match(r'.*figurant.*', prisoner_link)
    if 'figurant' in prisoner_link : results.append(prisoner_link)
  return results  

def get_list_function(url, tag=0):
  prisoner_list = []
  page = ["not_empty"]
  i=1
  while len(page) != 0:
  # if 1:
    page = []
    print ("page " + str (i))
    if tag : page = parse_memo_tag_url(url+str(i))
    else : page = parse_memo_url(url+str(i))
    prisoner_list += page
    i+=1
  else:
    print(f'Набралось {i} страниц')
  
  if not tag :
    prisoner_list = parsepzk_common_functions.set_genrder_bit ( prisoner_list )
    prisoner_list = parsepzk_common_functions.catch_birth_date ( prisoner_list )
    prisoner_list = parsepzk_common_functions.clean_fields_from_exceed ( prisoner_list )
  
  return prisoner_list

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
  

def top (fold_name):

  polit_url='https://memopzk.org/list-persecuted/spisok-politzaklyuchyonnyh-bez-presleduemyh-za-religiyu/page/'
  relig_url='https://memopzk.org/list-persecuted/spisok-politzaklyuchyonnyh-presleduemyh-za-religiyu/page/'
  probo_url='https://memopzk.org/list-persecuted/veroyatnye-zhertvy-ne-voshedshie-v-spiski/page/'

  antiw_tag_url='https://memopzk.org/tags/repressii-za-antivoennuyu-pozicziyu/page/'
  krym_tag_url='https://memopzk.org/regions/krym/page/'
  relig_tag_url='https://memopzk.org/tags/presledovaniya-po-religioznomu-priznaku/page/'
  muslim_tag_url='https://memopzk.org/tags/dela-musulman/page/'

  polit_list=get_list_function(polit_url)
  prob_list = get_list_function(probo_url)
  relig_list = get_list_function(relig_url)
      
  antiw_tag_list=get_list_function(antiw_tag_url, 1)
  krym_tag_list=get_list_function(krym_tag_url, 1)
  relig_tag_list=get_list_function(relig_tag_url, 1)
  muslim_tag_list = get_list_function(muslim_tag_url, 1)
      
  # case207_3_list = [ i for i in polit_list if '207.3 ч.2' in i['prisoner_case'] ]
      
  antiw_svb_list = [ i for i in polit_list if i['prisoner_link'] in antiw_tag_list ]
  probp_svb_list = [ i for i in prob_list  if not (i['prisoner_link'] in antiw_tag_list + relig_tag_list + muslim_tag_list) ]
  probr_svb_list = [ i for i in prob_list  if (i['prisoner_link'] in relig_tag_list + muslim_tag_list) ]
  polit_svb_list = [ i for i in polit_list if not (i['prisoner_link'] in antiw_tag_list)]
  polit_svb_list = polit_svb_list + probp_svb_list
  relig_svb_list = relig_list + probr_svb_list

  parsepzk_common_functions.print_bot_list( antiw_svb_list, 'markdown', os.path.join(fold_name, "antiw_list.txt"))
  parsepzk_common_functions.print_bot_list( polit_svb_list, 'markdown', os.path.join(fold_name, "polit_list.txt"))
  parsepzk_common_functions.print_bot_list( relig_svb_list, 'markdown', os.path.join(fold_name, "relig_list.txt"))
    
# if args.month:
  # for one_month in args.month:
    # file_name = "month_" + one_month + "_list_" + datetime.strftime(datetime.today(), "%Y.%m.%d") + ".txt"
    # print("Generate list for month " + one_month + " to file \"" + file_name + "\"")
    # month_list_maker_function(polit_url, one_month, file_name)
    # month_list_maker_function(relig_url, one_month, file_name)
    # month_list_maker_function(probo_url, one_month, file_name)

  # if args.descr:
    # print(args.descr)
    # 
    # bot_description_maker_function(polit_url, os.path.join(fold_name, "descr_polit_list.txt"))
    # bot_description_maker_function(probo_url, os.path.join(fold_name, "descr_prob_list.txt"))
    # bot_description_maker_function(relig_url, os.path.join(fold_name, "descr_relig_list.txt"))
