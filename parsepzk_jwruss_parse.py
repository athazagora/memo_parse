#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import requests
import random
import re
import os

import parsepzk_common_functions
import parsepzk_proxy_functions
import parsepzk_prison_functions


def parse_prisoner_link(url, session):
  
  # r = session.get(url, timeout=1.5) 
  
  r = requests.get(url)
  r.encoding = r.apparent_encoding
  soup = BeautifulSoup(r.text, 'html.parser') 
  
   # <div class="prisoner-card__info">
   # <var class="fw-bold">ФИО</var>:
  tmp_conteiner = soup.find('div', {'class': 'prisoner-card__info'}).find_all('div')
  
  prisoner_full_name = "not parsed"
  prisoner_addr = "not parsed"
  prisoner_byear = "not parsed"
  
  for tmp in tmp_conteiner:
    clean_tmp_text = re.sub("^\s+|\n|\r|\s+$", '', tmp.text)
    clean_tmp_text = re.sub("\s+", ' ', clean_tmp_text)
    clean_tmp_text = re.sub("[a-zA-Z,]", '', clean_tmp_text)
    
    # print ("clean2:\n" + clean_tmp_text)
    if 'ФИО:' in clean_tmp_text:
      prisoner_full_name = clean_tmp_text.split("ФИО:")[1]
          
    if 'Дата рождения:' in clean_tmp_text:
      prisoner_byear = clean_tmp_text.split("Дата рождения:")[1]
      prisoner_byear = parsepzk_common_functions.get_birthdate_from_date(prisoner_byear)
      # print (prisoner_byear)
    if 'Текущее местонахождение:' in clean_tmp_text:
      prisoner_addr = clean_tmp_text.split("Текущее местонахождение:")[1]
      # print ("addr: " + prisoner_addr)
      prisoner_addr = re.sub("^\s+|\n|\r|\s+$", '', prisoner_addr)
      if (prisoner_addr != "not parsed") : prisoner_addr = "ФКУ " + prisoner_addr

  # print ("prisoner_name: " + prisoner_full_name)
  # print ("prisoner_date: " + prisoner_byear)
  # print ("prisoner_addr: " + prisoner_addr)

  return { 'prisoner_full_name': prisoner_full_name, 'prisoner_addr': prisoner_addr, 'prisoner_byear' : prisoner_byear } 

def parse_jwrussia_url(url, use_proxy):
  results = []
  
  if (use_proxy):
    rememb_session = parsepzk_proxy_functions.get_workable_proxy_for_url(url)
    print ( "via proxy: ")
    print ( rememb_session.proxies )
  else:
    rememb_session = requests
    
  # r = rememb_session.get(url, timeout=1.5)
  r = requests.get(url)
  r.encoding = r.apparent_encoding
  soup = BeautifulSoup(r.text, 'html.parser')
  
  # <div class="prisoner"
  items = soup.find_all('div', {'class': 'prisoner'})
  for item in items:
    # prisoner_verdict = item.get('data-verdict')
    # print (item)
    prisoner_status = item.get('data-verdict')
    if prisoner_status=='' : prisoner_status = item.get('data-restriction')
    
    print (prisoner_status)
    # <div class="prisoner__name">
    prisoner_name = item.find('div', {'class': 'prisoner__name'}).find('span')
    # print (prisoner_name)
    for br in prisoner_name.find_all("br"): br.replace_with(" ")
    prisoner_name = prisoner_name.text
    prisoner_name = re.sub("\s+", ' ', prisoner_name)
    print (prisoner_name)
    
    # <a href="/prisoners/abdulgalimov.html" class="prisoner__link">
    prisoner_link = item.find('a', {'class':'prisoner__link'}).get('href')
    prisoner_link = re.sub(r'/[\w\.]+$', '', url) + prisoner_link
    # print ("prisoner_link: " + prisoner_link)
    
    # <div class="prisoner__hidden">
    hidden_part = item.find('div', {'class': 'prisoner__hidden'}).find_all('div', {'class', 'prisoner__hidden-item'})
    for tmp in hidden_part:
      tmp_conteiner = tmp.text.split("Текущие ограничения:\n")
      if len(tmp_conteiner) > 1: 
        prisoner_status = re.sub("^\s+|\n|\r|\s+$", '', tmp_conteiner[1])
    # print ("prisoner_status: " + prisoner_status)
    
    if prisoner_status in ['исправительная колония', 'Следственный изолятор']:
      prisoner_intro = parse_prisoner_link(prisoner_link, rememb_session)
      results.append({
            'prisoner_name': str(prisoner_intro['prisoner_full_name']).strip(),
            'prisoner_link': prisoner_link,
            'prisoner_case': "JW",
            'prisoner_addr': str(prisoner_intro['prisoner_addr']),
            'prisoner_desc': "JW",
            'prisoner_male' : 2,
            'prisoner_bday': 0,
            'prisoner_bmonth': 0,
            'prisoner_byear': str(prisoner_intro['prisoner_byear']),
            'prisoner_grad': ""
            })
  return results


def top (fold_name, use_proxy=0, truncated = 0):
  url = "https://jw-russia.org/prisoners.html"
  url = "https://dgoj30r2jurw5.cloudfront.net/prisoners.html"
  # url = "https://dgoj30r2jurw5.cloudfront.net/"
  prison_list = parsepzk_prison_functions.create_prison_dict ( "parsepzk_prison_database.xls" )
  prisoner_list = parse_jwrussia_url(url, use_proxy)
  
  # for i in prisoner_list : print (i)
  prisoner_list = parsepzk_common_functions.set_genrder_bit ( prisoner_list )
  prisoner_list = parsepzk_common_functions.clean_fields_from_exceed ( prisoner_list )
  for i in prisoner_list :
    print ("+==============================+\n" + i['prisoner_name'] + ": " + i['prisoner_addr'])
    i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, truncated)
    print (i['prisoner_name'] + ": " + i['prisoner_addr'])
  
  parsepzk_common_functions.print_bot_list( prisoner_list, 'markdown', os.path.join(fold_name, "jw_list.txt"))

