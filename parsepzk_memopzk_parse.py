#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re
import os

import parsepzk_common_functions
import parsepzk_prison_functions

import pickle


def parse_prisoner_link(url):
  
  r = requests.get(url, timeout=500)
  soup = BeautifulSoup(r.text, 'html.parser')
  #  <div class="human-dossier__art">
  prisoner_desc = soup.find('div', {'class': 'human-dossier__art'}).text
  
  prisoner_addr = "no addr"
  # <div class="modal modal--preload modal--no-scale modal--fit-content modal--side" data-modal="letter">
  tmp_conteiner = soup.find('div', {'class': 'modal modal--preload modal--no-scale modal--fit-content modal--side'})
  if tmp_conteiner:
    tmp_conteiner = tmp_conteiner.text.split("Написать письмо\n")
    if len(tmp_conteiner) > 1: 
      # print (tmp_conteiner)
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
  r = requests.get(url, timeout=500)
  
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
  r = requests.get(url, timeout=500)
  
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

def page_exist(url):
  r = requests.get(url, timeout=500);
  return len(r.text) > 10 ;
  

def save_tmp_list(prisoner_list, file_name):
  print ("save tmp to filename : " +  file_name)
  # f = open(file_name, 'w')
  with open(file_name, "wb") as fp:   #Pickling
    pickle.dump(prisoner_list, fp)


def restore_tmp_list(file_name):
  print ("restore tmp from filename : " +  file_name)
  result = []
  with open(file_name, "rb") as fp:   # Unpickling
    result = pickle.load(fp)
  return result


def get_list_function(url, try_to_restore = 0, fold_name="", tag=0):
  prisoner_list = []
  page = ["not_empty"]
  i=1
  
  filename= url
  filename= re.sub('https://memopzk.org/', '', filename)
  filename= re.sub('/', '_', filename) + "tmp.pkl"
  filename= os.path.join(fold_name, filename)
  
  if try_to_restore and os.path.exists(filename):
    prisoner_list = restore_tmp_list (filename)
  else :
    while page_exist(url+str(i)):
      print ("page " + url+str (i))
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
  
    save_tmp_list (prisoner_list, filename)
    
  return prisoner_list


def bot_description_maker_function(url, file_name=None):
  print ( url )
  prisoner_list = get_list_function (url)
  
  f = open(file_name, 'w')
  for field in prisoner_list: 
    print ("[" + field['prisoner_name'] + "]")
  f.close()
  
  return 0
  

def top (fold_name, try_to_restore = 1, truncated = 0, test_mode = 0):

  polit_url='https://memopzk.org/list-persecuted/spisok-politzaklyuchyonnyh-bez-presleduemyh-za-religiyu/page/'
  relig_url='https://memopzk.org/list-persecuted/spisok-politzaklyuchyonnyh-presleduemyh-za-religiyu/page/'
  probo_url='https://memopzk.org/list-persecuted/veroyatnye-zhertvy-ne-voshedshie-v-spiski/page/'
  
  antiw_page_url='https://memopzk.org/list-persecuted/antivoennoe-delo/page/'
  antiw_tag_url='https://memopzk.org/tags/repressii-za-antivoennuyu-pozicziyu/page/'
  
  case_207_3_1='https://memopzk.org/uk/207-3-ch-1/page/'
  case_207_3_2='https://memopzk.org/uk/207-3-ch-2/page/'
  krym_tag_url='https://memopzk.org/regions/krym/page/'
  relig_tag_url='https://memopzk.org/tags/presledovaniya-po-religioznomu-priznaku/page/'
  muslim_tag_url='https://memopzk.org/tags/dela-musulman/page/'
  hizb_tag_url='https://memopzk.org/tags/hizb-ut-tahrir/page/'
  jw_tag_url='https://memopzk.org/tags/presledovanie-svidetelej-iegovy/page/'
  
  prison_list = parsepzk_prison_functions.create_prison_dict ( "parsepzk_prison_database.xls" )

  if test_mode:
    polit_list = get_list_function(polit_url, try_to_restore, fold_name)
    prison_list = parsepzk_prison_functions.create_prison_dict ( "parsepzk_prison_database.xls" )
    
    one_list = [ i for i in polit_list if (i['prisoner_name'] == "Петрова Виктория Руслановна")]
    
    for item in one_list:
      print (item)
      item['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( item['prisoner_addr'], prison_list)
      print (item['prisoner_addr'])
    print ("")

  else :
  
    polit_list = get_list_function(polit_url, try_to_restore, fold_name)
    prob_list  = get_list_function(probo_url, try_to_restore, fold_name)
    relig_list = get_list_function(relig_url, try_to_restore, fold_name)
    
    full_list = polit_list+prob_list+relig_list    
    
    if 0 :
      # JWRUS list only
      jw_only_tag_list =  get_list_function(jw_tag_url, try_to_restore, fold_name, 1)
      jw_only_list = [ i for i in relig_list+prob_list if (i['prisoner_link'] in jw_only_tag_list ) ]
      parsepzk_common_functions.print_bot_list( jw_only_list, 'markdown', os.path.join(fold_name, "relig_list.txt"))
      # Jurnalist list
      descr_journalist_list  = [ i for i in full_list if 'журналист' in i['prisoner_desc'] ]
      descr_journalist_list += [ i for i in full_list if 'блогер'    in i['prisoner_desc'] ]
      descr_journalist_list += [ i for i in full_list if 'блоггер'   in i['prisoner_desc'] ]
      parsepzk_common_functions.print_simle_list( descr_journalist_list, 'markdown', os.path.join(fold_name, "journ_list.txt"))
    else :
      antiw_list  = get_list_function(antiw_page_url, try_to_restore, fold_name)
      antiw_tag_list = [ i['prisoner_link'] for i in antiw_list ]
      
      case207_3_list = get_list_function(case_207_3_1, 1) + get_list_function(case_207_3_2, 1)
      # krym_tag_list=get_list_function(krym_tag_url, 1)
      relig_tag_list  = get_list_function(relig_tag_url , try_to_restore, fold_name, 1)
      muslim_tag_list = get_list_function(muslim_tag_url, try_to_restore, fold_name, 1)
      hizb_tag_list   = get_list_function(hizb_tag_url  , try_to_restore, fold_name, 1)
      
      antiw_svb_list = [ i for i in full_list if (i['prisoner_link'] in antiw_tag_list + case207_3_list) ]
      probp_svb_list = [ i for i in prob_list if (i['prisoner_link'] not in muslim_tag_list + relig_tag_list + hizb_tag_list + antiw_tag_list) ]
      probr_svb_list = [ i for i in prob_list if (i['prisoner_link'] in     muslim_tag_list + relig_tag_list + hizb_tag_list) ]
      
      polit_svb_list = [ i for i in polit_list if not (i['prisoner_link'] in antiw_tag_list)]
      polit_svb_list = polit_svb_list + probp_svb_list
      relig_svb_list = relig_list + probr_svb_list
      
      for i in antiw_svb_list :
        i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, truncated)
      for i in polit_svb_list :
        i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, truncated)
      for i in relig_svb_list :
        i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, truncated)
      
      parsepzk_common_functions.print_bot_list( antiw_svb_list, 'markdown', os.path.join(fold_name, "antiw_list.txt"))
      parsepzk_common_functions.print_bot_list( polit_svb_list, 'markdown', os.path.join(fold_name, "polit_list.txt"))
      parsepzk_common_functions.print_bot_list( relig_svb_list, 'markdown', os.path.join(fold_name, "relig_list.txt"))
     
  # if args.descr:
    # print(args.descr)
    # 
    # bot_description_maker_function(polit_url, os.path.join(fold_name, "descr_polit_list.txt"))
    # bot_description_maker_function(probo_url, os.path.join(fold_name, "descr_prob_list.txt"))
    # bot_description_maker_function(relig_url, os.path.join(fold_name, "descr_relig_list.txt"))
