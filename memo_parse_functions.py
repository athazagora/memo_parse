#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#lib downloaded from https://pypi.org/project/requests/#modal-close
import requests
import shutil
import re

def set_genrder_bit (prisoner_list):
  for field in prisoner_list:
    # set gender
    if re.match(".*[вч]на", field['prisoner_name']):
      field['prisoner_male'] = 0
    if re.match(".*[вь]ич", field['prisoner_name']):
      field['prisoner_male'] = 1
    if re.match(".* оглы",  field['prisoner_name']):
      field['prisoner_male'] = 1
    field['prisoner_name'] = re.sub(r"\s+$", "", field['prisoner_name'])
  return prisoner_list

def catch_birth_date(prisoner_list):
  mons_list=["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
  for field in prisoner_list:
    # print (field['prisoner_name'])
    for mon in mons_list:
      if field['prisoner_male'] == 1: 
        tmp_date = re.findall("[рР]оди[лвший]{1,4}ся [0-9]{1,2}." + mon + " [0-9]{2,4}", field['prisoner_desc'])
      else:
        tmp_date = re.findall("[рР]одилась [0-9]{1,2} " + mon + " [0-9]{2,4}", field['prisoner_desc'])
       # Родился 5 мая 1981 года
      for tmp_d in tmp_date:
        result = re.split( " " + mon + " ", tmp_d)
        if len(result) > 1:
          if field['prisoner_male'] > 0:
            field['prisoner_bday'] = int(re.sub("[рР]оди[лвший]{1,4}ся ", "", result[0]))
          else:
            field['prisoner_bday'] = int(re.sub("[рР]одилась ", "", result[0]))
          field['prisoner_bmonth'] = mons_list.index(mon) + 1
          field['prisoner_byear'] = int(result[1])
    
    if (field['prisoner_byear']==0) :
      tmp_year = {}
      if field['prisoner_male'] == 1:
        tmp_year = re.findall("[рР]одился в [0-9]{2,4} году", field['prisoner_desc'])
      else:
        tmp_year = re.findall("[рР]одилась в [0-9]{2,4} году", field['prisoner_desc'])
      # print (tmp_year)
      for tmp_y in tmp_year:
        result = re.split(" ", tmp_y)
        # print (result)
        field['prisoner_byear'] = int (result[2])
    
    if (field['prisoner_byear']==0) :
      tmp_year = {}
      tmp_year = re.findall(", [0-9]{4} г. р.,", field['prisoner_desc'])
      print(tmp_year)
      # field['prisoner_byear'] = int (result[2])
          
      
  return prisoner_list

def clean_fields_from_exceed(prisoner_list):
  for field in prisoner_list:
    # delete exceed word
    field['prisoner_name'] = re.sub('\(.+\) ', '', field['prisoner_name'])
    # find grad
    name = field['prisoner_name'].split()
    
    # print (name, field['prisoner_addr'])
    
    if len(name) > 2:
      for i in range(2): name[i] = name[i][0:-2] + ".+"
      find_grad = ''.join(re.findall(name[0]+" "+name[1], field['prisoner_addr'])).split()
      # print (find_grad)
      if len(find_grad) > 1: 
        # print (field['prisoner_addr'])
        field['prisoner_grad'] = find_grad[1] + " " + find_grad [0]
        field['prisoner_addr'] = field['prisoner_addr'].split(find_grad[0], 1)[0]
        field['prisoner_addr'] = field['prisoner_addr'].split("ФИО", 1)[0]
        field['prisoner_addr'] = field['prisoner_addr'].split("или через сервис:", 1)[0]
        field['prisoner_grad'] = re.sub('Александр ', 'Александру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Владимир ', 'Владимиру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Андрей ', 'Андрею ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Багаудин ', 'Багаудину ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Салех ', 'Салеху ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Юрий ', 'Юрию ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Дмитрий ', 'Дмитрию ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Дамир ', 'Дамиру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Азат ', 'Азату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Рифат ', 'Рифату ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub(r'ов$', 'ову', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'ев$', 'еву', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'ин$', 'ину', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'ун$', 'уну', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'кий$', 'кому', field['prisoner_grad'])
        
        # field['prisoner_addr'] = field['prisoner_addr'].split("ФИО, год рождения.','', field['prisoner_addr'])
        
        field['prisoner_addr'] = re.sub(r'\n', r' ', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub(r'^(\d{3}) (\d{3})', r'\1\2', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub(r'^(\d{6}) ', r'\1, ', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub(r'[.,] *$', '', field['prisoner_addr'])
        
        field['prisoner_addr'] = re.sub('Исправительная колония', 'ИК', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('Следственный изолятор', 'СИЗО', field['prisoner_addr'])
        
        has_fky = re.findall ('ФКУ', field['prisoner_addr'])
        if len (has_fky)==0:
          field['prisoner_addr'] = re.sub(r'ИК', 'ФКУ ИК', field['prisoner_addr'])
          field['prisoner_addr'] = re.sub(r'СИЗО', 'ФКУ СИЗО', field['prisoner_addr'])
          field['prisoner_addr'] = re.sub(r'ЛИУ', 'ФКУ ЛИУ', field['prisoner_addr'])
        
        field['prisoner_addr'] = re.sub(r'ФКУ (\w{2,4})[^\d]+(\d{1,3}) (\w{4,6}) России', r'ФКУ \1-\2 \3 России', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('г. Ростов-на-Дону ул. Тоннельная', 'г. Ростов-на-Дону, ул. Тоннельная', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub(r'Япеева, 16\. СИЗО-1 по РТ*$', 'Япеева, 16/1, СИЗО-1 по Республике Татарстан', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub(r'Новгородская обл., Валдайский район, г. Валдай', 'Новгородская обл., г. Валдай', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('бул. Ленина 4', 'Бульвар Ленина, д. 4,', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('России по РБ','России по Республике Башкортостан', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('России по РТ','России по Республике Татарстан', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub(r'России по (\w+) обл\.', r'России по \1 области', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('357500', '357502', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('с. Кочубеевское, Ставропольский край', 'Ставропольский край, с. Кочубеевское', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('Ростовская обл., Новочеркасск', 'Ростовская область, г. Новочеркасск', field['prisoner_addr'])
        field['prisoner_addr'] = re.sub('СИЗО № ', 'СИЗО-', field['prisoner_addr'])
        # print (field['prisoner_addr'])
  return prisoner_list

def print_date(field):
  date_per_point = "0"
  
  if field['prisoner_byear']!=0:
    date_per_point = str(field['prisoner_byear'])
    if field['prisoner_bmonth']!=0:
      date_per_point = str(field['prisoner_bmonth']) + "." + date_per_point
      if field['prisoner_bday']!=0:
        date_per_point = str(field['prisoner_bday']) + "." + date_per_point
    
  return date_per_point

def print_addr_existanse(field):
  if field['prisoner_addr'] == "не указан" : return "адрес не указан"
  else: return ""

def print_google_table_link(p_list):
  for field in p_list:
    print ("=HYPERLINK(\"https://memohrc.org/"+field['prisoner_link']+"\";\""+field['prisoner_name']+"\")")

    
def print_list(p_list, print_format='', file_name=None):
  f = open(file_name, 'w')
      
  for field in p_list: 
    if print_format == 'markdown' :
      name = "["+field['prisoner_name']+"](https://memohrc.org"+field['prisoner_link']+")"
      field['prisoner_case'] = re.sub(r'.*«Хизб ут-Тахрир».*', r'[«Хизб ут-Тахрир»](https://memohrc.org/ru/special-projects/presledovanie-organizacii-hizb-ut-tahrir)', field['prisoner_case'])
      field['prisoner_case'] = re.sub(r'.*к свидетелям Иеговы.*', r'[«Cвидетели Иеговы»](https://memohrc.org/ru/special-projects/spisok-presleduemyh-po-obvineniyu-v-prinadlezhnosti-k-svidetelyam-iegovy)', field['prisoner_case'])
      field['prisoner_case'] = re.sub(r'Дело ингушской оппозиции', r'[Дело ингушской оппозиции](https://memohrc.org/ru/special-projects/delo-ingushskoy-oppozicii)', field['prisoner_case'])
      field['prisoner_case'] = re.sub(r'Пензенское дело запрещённой «Сети»', r'[дело «Сети»](https://memohrc.org/ru/special-projects/penzenskoe-delo-zapreshchyonnoy-seti)', field['prisoner_case'])
      field['prisoner_case'] = re.sub(r'Петербургское дело запрещённой «Сети»', r'[дело «Сети»](https://memohrc.org/ru/special-projects/peterburgskoe-delo-zapreshchyonnoy-seti)', field['prisoner_case'])
      field['prisoner_case'] = re.sub(r'.*кинотеатре «Киргизия».*', r'[«теракт в «Киргизии»](https://memohrc.org/ru/special-projects/delo-o-podgotovke-terakta-v-moskovskom-kinoteatre-kirgiziya)', field['prisoner_case'])
      field['prisoner_case'] = re.sub(r'Дело о «массовых беспорядках» в Москве 27 июля 2019 года', r'[«Московское дело»](https://memohrc.org/ru/special-projects/delo-o-massovyh-besporyadkah-v-moskve-27-iyulya-2019-goda)', field['prisoner_case'])
      field['prisoner_case'] = re.sub(r'Дело о теракте в петербургском метро 3 апреля 2017 года', r'[«теракт в петербургском метро»](https://memohrc.org/ru/special-projects/delo-o-terakte-v-peterburgskom-metro-3-aprelya-2017-goda)', field['prisoner_case'])
    else: 
      if print_format == '' :
        name = field['prisoner_name']
      else:
        if print_format == 'full' :
          name = field['prisoner_name'] + " - " + field['prisoner_case'] + " - " + field['prisoner_code'] + " - " + field ['prisoner_addr']
        else:
          if print_format == 'gend' :
            name = field['prisoner_name'] + " - " + str(field['prisoner_male'])
          else:
            if print_format == 'botlist' :
              name = "["+field['prisoner_name']+"](https://memohrc.org"+field['prisoner_link']+")"

    # print (name, "-", print_date(field), "-", print_addr_existanse(field), file=file_name)
    print (name, "-", print_date(field), "-", print_addr_existanse(field), field['prisoner_case'], file=file_name)
    # print (name, "-", print_date(field), "-", field['prisoner_addr'], file=file_name)
  f.close()
  
def print_bot_list(p_list, print_format='', file_name=None):
  f = open(file_name, 'w')
  for field in p_list: 
    if print_format == 'markdown' :
      name = "["+field['prisoner_name']+"](https://memohrc.org"+field['prisoner_link']+")"
    else:
      if print_format == '' :
        name = field['prisoner_name']
    
    print (name, "`"+print_date(field)+" г.р.` :addr_delim:", field['prisoner_grad'], ":addr_delim:", field['prisoner_addr'], file=f)
  f.close()


def get_one_month_list(prisoner_list, month):
  month_list = [ i for i in prisoner_list if i['prisoner_bmonth'] == month]
  month_list.sort(key=lambda day: day['prisoner_bday'])
  return month_list
