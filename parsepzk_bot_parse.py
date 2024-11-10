#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import requests
import re
import os

import parsepzk_common_functions
import parsepzk_prison_functions


def parse_svobot_url(url):
  results = []
  
  r = requests.get(url)
  r.encoding = r.apparent_encoding
  soup = BeautifulSoup(r.text, 'html.parser')
  # <div class="prisoner"
  items = soup.find_all('a')
  for item in items:
    print (item)
    prisoner_name = item.text
    prisoner_name_first = re.split(' ', prisoner_name)[0]
    prisoner_link = item.get('href')
    
    if len(prisoner_name)>0 and not (prisoner_name in {"---наверх---", " - по месяцам - ", " - по полам - ", "СВОБОТа"}) :
      prisoner_info = re.findall(fr'{prisoner_link}.*{prisoner_name_first}.*', r.text)
      if len (prisoner_info) > 0: prisoner_info = prisoner_info[0]
      # print ("prisoner_info: ", prisoner_info)
      # else prisoner_info = ""
      prisoner_addr = re.sub(fr".*{prisoner_name}</a> .* г\.р\. : (.*) <br>", r"\1" , prisoner_info )
      prisoner_name = re.sub(fr" \([\w ]+\)", "", prisoner_name)
      prisoner_info = re.sub(fr" \([\w ]+\)", "", prisoner_info)
      prisoner_date = re.sub(fr".*{prisoner_name}</a> .*(\d\d\d\d) г\.р\. : .*" , r"\1" , prisoner_info )
      # prisoner_date = re.sub(fr"^\d\d\." , r"" , prisoner_date )
      # print ("prisoner_date: ", prisoner_date, " - ", prisoner_name)
      
      results.append({
        'prisoner_name': prisoner_name,
        'prisoner_link': prisoner_link,
        'prisoner_case': "",
        'prisoner_addr': prisoner_addr,
        'prisoner_desc': "bot",
        'prisoner_male' : 2,
        'prisoner_bday': 0,
        'prisoner_bmonth': 0,
        'prisoner_byear': prisoner_date,
        'prisoner_grad': ""
      })
  return results


def top (fold_name, truncated = 0 ):
  # url = "http://441701-ce65673.tmweb.ru"
  # prisoner_list = parse_svobot_url(url)
  
  RELIG_LIST=create_list('/home/ath/a212/telegrambot/delo212_tgbot/relig_list.txt')
  POLIT_LIST=create_list('/home/ath/a212/telegrambot/delo212_tgbot/polit_list.txt')
  ANTIW_LIST=create_list('/home/ath/a212/telegrambot/delo212_tgbot/antiw_list.txt')
  prisoner_list=POLIT_LIST+RELIG_LIST+ANTIW_LIST
  
  # prisoner_list = parsepzk_common_functions.set_genrder_bit ( prisoner_list )
  # prisoner_list = parsepzk_common_functions.clean_fields_from_exceed ( prisoner_list )
  prison_list = parsepzk_prison_functions.create_prison_dict ( "parsepzk_prison_database.xls" )
  for i in prisoner_list :
    i['prisoner_addr'] = parsepzk_prison_functions.find_max_compare ( i['prisoner_addr'], prison_list, truncated)
  parsepzk_common_functions.print_bot_list( prisoner_list, 'markdown', os.path.join(fold_name, "bot_list.txt"))


def create_list(file_name):
  results = []
  with open(file_name, 'r') as f:
    for item in list(f):
      # print ("item - " + item)
      if not (item and item.strip()) :
        print ("Error in line " + str(len(results)+1) + " : line is empty." ) ;
        continue
        
      parse_item = re.split( ":addr_delim:", item)
      if len(parse_item) < 3:
        print ("Error in create list at line " + str(len(results)+1) + ":" + item)
        continue
      
      tmp_date = re.findall("`[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4} г\.р\.`", parse_item[0])
      if len(tmp_date) > 0:
        ddate = tmp_date[0].replace(".", " ").replace("`", " ").split()
      else:
        year = re.findall("[0-9]{1,4} г\.р\.`", parse_item[0])
        if len(year) > 0:
          ddate=[0,0, year[0].replace(" г.р.`", "")]
        else:
          print ("Error in date parse at line " + str(len(results)+1) + ":" + item)
          ddate=[0,0,0]
      
      prisoner_name = re.findall("\[.*\]", parse_item[0])[0]
      prisoner_name = re.sub("\[|\]", "", prisoner_name)
      # print (prisoner_name)
      prisoner_link = re.findall("\(htt.*\)", parse_item[0])[0]
      prisoner_link = re.sub("\(|\)", "", prisoner_link)
      # print (prisoner_link)
      prisoner_addr = parse_item[2].strip()
      
      results.append({            
        'prisoner_name': prisoner_name,
        'prisoner_link': prisoner_link,
        'prisoner_case': "",
        'prisoner_addr': prisoner_addr,
        'prisoner_desc': "bot",
        'prisoner_male' : 2,
        'prisoner_bday': int(ddate[0]),
        'prisoner_bmonth': int(ddate[1]),
        'prisoner_byear': int(ddate[2]),
        'prisoner_grad': ""
      })
        
  return results

