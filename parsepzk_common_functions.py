#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#lib downloaded from https://pypi.org/project/requests/#modal-close
import requests
import shutil
import re
import datetime
import pandas as pd


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

def catch_birth_date_old(prisoner_list):
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
      #print(tmp_year)
      # field['prisoner_byear'] = int (result[2])


  return prisoner_list

def create_prison_dict (file_name):
  results = []
  tmp_list = []
  
  df = pd.read_excel(file_name, 0) # can also index sheet by name or fetch all sheets
  tmp_list = df.values.tolist()
  for item in tmp_list: item = [str(s).strip() for s in item]
  fku_id = 0
  for item in tmp_list:
    address_parts = re.split(',|\(|\)', item[3])
    # print (address_parts)
    address_parts = [re.sub(r'^ул\. |^г\. |^мкр\. |^д\. |^зд\. |^п\. |^пер\. |^с\. |^бул\. |^стр\. |^р\. п\.  |^ш\. |^пгт |проезд$|квартал ', '', s.strip()) for s in address_parts]
    address_parts = [re.sub(r'—|–|−|-', '−', s.upper()) for s in address_parts]
    address_parts = [re.sub('Ё', 'Е', s) for s in address_parts]
    address_parts = [re.sub(r'САЛАВАТ−6', 'САЛАВАТ', s) for s in address_parts]
    
    results.append({
      'fku_id'      : fku_id,
      'fku_reg'     : item [0],
      'fku_type'    : str(item [1]),
      'fku_num'     : str(item [2]),
      'fku_addr'    : item [3],
      'addr_parts'  : address_parts,
      'fku_fsin'    : "",
      'fku_name'    : ""
    })
    fku_id += 1

  df = pd.read_excel(file_name, 1) # can also index sheet by name or fetch all sheets
  tmp_list = df.values.tolist()
  for item in tmp_list: item = [str(s).strip() for s in item]
  
  for i in results:
    if i['fku_type'] == "СИЗО (ц. п.)" :
      i['fku_fsin'] = "ФСИН России"
      i['fku_name'] = f"СИЗО-{i['fku_num']}"
    else:
      for item in tmp_list:
        if i['fku_reg'].strip().upper() == item[0].strip().upper() : 
          i['fku_fsin'] = item[1].strip()
          if i['fku_num'] == "б/н" :
            i['fku_name'] = i['fku_type']
          else :
            i['fku_name'] = i['fku_type'] + "-" + i['fku_num']
      if i['fku_fsin'] == "" or i['fku_name'] == "" : print (i)
  
  df = pd.read_excel(file_name, 2) # can also index sheet by name or fetch all sheets
  tmp_list = df.values.tolist()
  for item in tmp_list: item = [str(s).strip() for s in item]
  
  for i in results:
    for item in tmp_list:
      if i['fku_reg'].strip().upper() == item[0].strip().upper() :
        print (i)
        print (item)
        print (f"{len(item)} isna {pd.isna(item[2])}")
        last = 0
        while last < len(item) and not pd.isna(item[last]) : 
          print("curent : ", last)
          last+=1
        print (last)
        excid_arr = [item[last-2], item[last-1]]
        # if pd.isna(item[2]) : excid_arr = [item[0], item[1]]
        # else      : excid_arr = [item[1], item[2]]
        print (excid_arr)
        
        if re.search(excid_arr[0]+'.*'+excid_arr[1]+', ', i['fku_addr']) :
          print (excid_arr[0]+".*"+excid_arr[1]+", ")
          i['fku_addr'] = re.sub(f"{excid_arr[0]}, ", "", i['fku_addr'])
          
        
        # i['fku_short_addr'] = item[1].strip()
    # if i['fku_fsin'] == "" : print (i)
  
  return results


def find_max_compare (init_address_string, prison_list):
  is_debug = 0
  
  waigth_id_list = []
  # print ("MAX : ", address_string )
  address_string = init_address_string ;
  
  address_string = re.sub(r'^(\d{3}) (\d{3})', r'\1\2', address_string)
  index_string = re.findall(r'\d{6}', address_string)
  if len (index_string) == 0 : return init_address_string
  address_string = re.sub(index_string[0] , '', address_string)
  index_string = index_string[0].strip()
  
  address_string = re.sub(r'—|–|−|-', '-', address_string.upper())
  address_string = re.sub(r'«|"|»', '', address_string)
  address_string = re.sub('Ё', 'Е', address_string)
  address_string = re.sub(r'(\d+) (\w{1},)', '\1\2', address_string)
  address_string = re.sub(r' ОБЛ\.', ' ОБЛАСТЬ', address_string)
  address_string = re.sub(r'ОМУ КРАЮ', 'ИЙ КРАЙ', address_string)
  address_string = re.sub(r'ОЙ ОБЛАСТИ', 'АЯ ОБЛАСТЬ', address_string)
  address_string = re.sub(r'ОЙ РЕСПУБЛИКЕ', 'АЯ РЕСПУБЛИКА', address_string)
  address_string = re.sub(r' РЕСПУБЛИКЕ', ' РЕСПУБЛИКА', address_string)
  
  
  fku_string = re.findall(r' СИЗО-\d+| ИК-\d+| КП-\d+| Т-\d+| ЛИУ-\d+ | ТЮРЬМА ', address_string)
  if len (fku_string) == 0 : return init_address_string
  address_string = re.sub(fku_string[0]   , '', address_string)
  fku_string = fku_string[0].strip()
  fku_string = re.sub(r'ТЮРЬМА', 'Т', fku_string)
  
  
  
  
  int_arr = re.findall(r'\d+', address_string)
  
  
  if is_debug: 
    print ("Reserched string: ", init_address_string )
    print ("Extracted fku_string : ", fku_string)
    print ("Extracted index_string : ", index_string)
    print (int_arr)
    print ("curent string: ", address_string)
    print ("++++++++++++++++")
  
  for item in prison_list:
    compare_num = 0
    compare_num += fku_string == item['fku_name']
    if is_debug: 
      print (compare_num, " : ", fku_string, " == ", item['fku_name'] )
    compare_num += address_string.find(item['fku_reg'].upper()) > 0
    if is_debug:
      print (compare_num, " : ", address_string, " : ", item['fku_reg'].upper())
    
    for part in item ['addr_parts']:
      if part.isnumeric() :
        compare_num += part in int_arr
        compare_num += int(part) == int(index_string)
        if is_debug:
          print ("num : ", compare_num, " : index in string ", index_string, " : ", part)
      else :
        compare_num += address_string.find(part) > 0
        if is_debug:
          print ("char: ", compare_num, " : ", part)
    
    waigth_id_list.append({
      'fku_id'      : item['fku_id'],
      'fku_addr'    : item['fku_addr'] + ", ФКУ " + item['fku_name'] + " " + item['fku_fsin'],
      'fku_waigth'  : compare_num
    })
  
  waigth_list = [ i['fku_waigth'] for i in waigth_id_list ]
  max_id_list = [ i for i in waigth_id_list if i['fku_waigth'] == max ( waigth_list ) ]
  if len (max_id_list) != 1 : 

    print ("Reserched string: ", init_address_string )
    print ("Extracted fku_string : ", fku_string)
    print ("Extracted index_string : ", index_string)
    print (int_arr)
    print ("curent string: ", address_string)
    print ("++++++++++++++++")
    
    for i in max_id_list : 
      print (i)
      for item in prison_list:
        
        if i['fku_id'] == item ['fku_id'] :
          compare_num = 0
          compare_num += fku_string == item['fku_name']
          print (compare_num, " : ", fku_string, " == ", item['fku_name'])
          compare_num += address_string.find(item['fku_reg'].upper()) > 0
          print (compare_num, " : ", address_string, " : ", item['fku_reg'].upper())
        
          for part in item ['addr_parts']:
            if part.isnumeric() :
              compare_num += int(part) in int_arr
              compare_num += int(part) == int(index_string)
              print ("num: ", compare_num, " : index in string ", index_string, " : ", part)
              print (int_arr)
            else :
              compare_num += address_string.find(part) > 0
              print ("char: ", compare_num, " : ", part)
          
          print (compare_num)
  
  return max_id_list[0]['fku_addr']


# PATTERN = r'[р|Р]одил[а-я]*\s+(?P<day_1>\d{1,2})\s+(?P<month_1>[а-яА-Я]+)\s+(?P<year_1>\d{4})|(?P<day_2>\d{1,2})\s+(?P<month_2>[а-яА-Я]+)\s+(?P<year_2>\d{4})\s+года рождения|родил(ся|ась)\s+в\s+(?P<year_3>\d{4})\s+году|(?P<year_4>\d{4})\s+г\.\s?р\.'
# PATTERN_WRAPPED = (
    # r'[р|Р]одил[а-я]*\s+(?P<day_1>\d{1,2})\s+(?P<month_1>[а-яА-Я]+)\s+(?P<year_1>\d{4})|'
    # r'(?P<day_2>\d{1,2})\s+(?P<month_2>[а-яА-Я]+)\s+(?P<year_2>\d{4})\s+года рождения|'
    # r'родил(ся|ась)\s+в\s+(?P<year_3>\d{4})\s+году|'
    # r'(?P<year_4>\d{4})\s+г\.\s?р\.'
    # )


def catch_birth_date(prisoner_list):
  for field in prisoner_list:
    # print (field['prisoner_name'])
    date = get_birthdate_from_text(field['prisoner_desc'])
    split_date = date.replace('.', ' ').split()
    # print (split_date)
    field['prisoner_byear'] = split_date[-1]
    if (len(split_date) > 1): field['prisoner_bmonth'] = split_date[-2]
    if (len(split_date) > 2): field['prisoner_bday'] = split_date[-3]

  return prisoner_list


def get_birthdate_from_text(text: str) -> str:
  """Извлекает дату или год рождения из текста
  (для описаний с сайта https://memopzk.org/)
  и возвращает в формате 'd.m.yyyy' """
  # Чтобы красиво объединить все варианты регулярок,
  # нужен флаг (?J) - он же gmJ. Но в модуле re он отсутсвует,
  # поэтому для каждого варианта используем своё название групп
  PATTERN = (
    r'[р|Р]одил[а-я]*\s+(?P<day_1>\d{1,2})\s+(?P<month_1>[а-яА-Я]+)\s+(?P<year_1>\d{4})|'
    r'(?P<day_2>\d{1,2})\s+(?P<month_2>[а-яА-Я]+)\s+(?P<year_2>\d{4})\s+года рождения|'
    r'родил(ся|ась)\s+в\s+(?P<year_3>\d{4})\s+году|'
    r'(?P<year_4>\d{4})\s+г\.\s?р\.'
  )
  MONTHS = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12
  }
  text_match = re.search(PATTERN, text)
  #print (text_match)
  if text_match:
    # Если в тексте найдена дата рождения полностью
    if text_match.group('year_1') or text_match.group('year_2'):
      day = text_match.group('day_1') or text_match.group('day_2')
      month_str = (
          text_match.group('month_1') or text_match.group('month_2'))
      year = text_match.group('year_1') or text_match.group('year_2')
      try:
        date = datetime.datetime(
                    year=int(year),
                    month=MONTHS[month_str],
                    day=int(day)
                ).date()
        date_str = date.strftime('%d.%m.%Y')
        # print (date_str)
        return date_str
      except Exception:
        return '0'
    # Если в тексте найден только год рождения
    elif text_match.group('year_3') or text_match.group('year_4'):
      year = (
                text_match.group('year_3')
                or text_match.group('year_4')
                or '0')
      year_str = year
      return year_str
  else:
    return '0'


def clean_fields_from_exceed(prisoner_list):
  for field in prisoner_list:
    # delete exceed word
    field['prisoner_name'] = re.sub('\(.+\) ', '', field['prisoner_name'])
    field['prisoner_name'] = re.sub(' +', ' ', field['prisoner_name'])
    # find grad
    name = field['prisoner_name'].split()

    # print (name, field['prisoner_addr'])

    if len(name) > 2:
      for i in range(2): 
        if len(name[i]) > 2 : name[i] = name[i][0:-2] + ".+"
          
      find_grad = ''.join(re.findall(name[0]+" "+name[1], field['prisoner_addr'])).split()
      # print (find_grad)
      if len(find_grad) > 1:
        # print (field['prisoner_addr'])
        field['prisoner_grad'] = find_grad[1] + " " + find_grad [0]
        field['prisoner_addr'] = field['prisoner_addr'].split(find_grad[0], 1)[0]
        field['prisoner_grad'] = re.sub('Азат ', 'Азату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Адам ', 'Адаму ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Айдар ', 'Айдару ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Айрат ', 'Айрату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Александр ', 'Александру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Андрей ', 'Андрею ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Алексей ', 'Алексею ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Аслан ', 'Аслану ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Алим ', 'Алиму ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Альберт ', 'Альберту ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Анзор ', 'Анзору ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Артур ', 'Артуру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Багаудин ', 'Багаудину ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub('Вадим ', 'Вадиму ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Владимир ', 'Владимиру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Вячеслав ', 'Вячеславу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Василий ', 'Василию ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Виктор ', 'Виктору ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub('Дамир ', 'Дамиру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Данис ', 'Данису ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Данил ', 'Данилу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Дмитрий ', 'Дмитрию ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Зафар ', 'Зафару ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Завур ', 'Завуру ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub('Илфат ', 'Илфату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Ильсур ', 'Ильсуру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Ильгиз ', 'Ильгизу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Имран ', 'Имрану ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Инял ', 'Инялу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Ирек ', 'Иреку ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Ислам ', 'Исламу ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub('Линар ', 'Линару ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Ленар ', 'Ленару ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Мухамадюсуп ', 'Мухамадюсупу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Марлен ', 'Марлену ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Наиль ', 'Наилю ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Нурмагомед ', 'Нурмагомеду ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub('Павел ', 'Павлу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Радик ', 'Радику ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Радмир ', 'Радмиру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Раиф ', 'Раифу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Рафаэль ', 'Рафаэлю ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Рефат ', 'Рефату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Ринат ', 'Ринату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Рифат ', 'Рифату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Рафис ', 'Рафису ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Рузим ', 'Рузиму ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Руслан ', 'Руслану ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Рустем ', 'Рустему ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub('Салех ', 'Салеху ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Сергей ', 'Сергею ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Тимур ', 'Тимуру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Тагир ', 'Тагиру ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Тажиб ', 'Тажибу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Урал ', 'Уралу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Фанис ', 'Фанису ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Фарид ', 'Фариду ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Фаррух ', 'Фарруху ', field['prisoner_grad'])
        
        field['prisoner_grad'] = re.sub('Шамиль ', 'Шамилю ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Шахбоз ', 'Шахбозу ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Шафкат ', 'Шафкату ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Эрфан ', 'Эрфану ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Эрсмак ', 'Эрсмаку ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Юрий ', 'Юрию ', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub('Ян ', 'Яну ', field['prisoner_grad'])

        field['prisoner_grad'] = re.sub(r'ов$', 'ову', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'ев$', 'еву', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'ёв$', 'ёву', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'ин$', 'ину', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'ун$', 'уну', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'кий$', 'кому', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'Шохиста Каримова', 'Шохисте Каримовой', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'Матлюба Насимова', 'Матлюбе Насимовой', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'Виктору Шур', 'Виктору Шуру', field['prisoner_grad'])
        field['prisoner_grad'] = re.sub(r'Юрию Корный', 'Юрию Корному', field['prisoner_grad'])

    # field['prisoner_addr'] = field['prisoner_addr'].split("ФИО, год рождения.','', field['prisoner_addr'])

    field['prisoner_addr'] = field['prisoner_addr'].split("ФИО", 1)[0]
    field['prisoner_addr'] = field['prisoner_addr'].split("или через сервис:", 1)[0]
    
    field['prisoner_addr'] = re.sub(r'\s+', ' ', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'\n', r' ', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'^(\d{3}) (\d{3})', r'\1\2', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'^(\d{6}) ', r'\1, ', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r', *$', '', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'\. *$', '', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('Написать письмо осуждённым можно через сайт «Крымской Солидарности»: https://crimean-solidarity.org/jaz-ummetim Бумажные письма отправлять по адресу:', '', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('Через ФСИН-письмо или обычной почтой:', '', field['prisoner_addr'])
    # field['prisoner_addr'] = re.sub(r'ул. Вторая Промышленная,\.*8,', 'ул. Вторая Промышленная, зд. 7Б, стр. 2', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'ул. Вторая Промышленная, д. 8', 'ул. Вторая Промышленная, зд. 7Б, стр. 2', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r' ул. 2-я промышленная , д. 8', 'ул. Вторая Промышленная, зд. 7Б, стр. 2', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r' ул. Вторая Промышленная, 8', 'ул. Вторая Промышленная, зд. 7Б, стр. 2', field['prisoner_addr'])

    field['prisoner_addr'] = re.sub('Исправительная колония', 'ИК', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r"исправительная колония № ", r'ИК-', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('Следственный изолятор', 'СИЗО', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'sivilia_1@mail.ru', r'', field['prisoner_addr'])

    has_fky = re.findall ('ФКУ', field['prisoner_addr'])
    if len (has_fky)==0:
      field['prisoner_addr'] = re.sub(r'ИК', 'ФКУ ИК', field['prisoner_addr'])
      field['prisoner_addr'] = re.sub(r'СИЗО', 'ФКУ СИЗО', field['prisoner_addr'])
      field['prisoner_addr'] = re.sub(r'ЛИУ', 'ФКУ ЛИУ', field['prisoner_addr'])


    field['prisoner_addr'] = re.sub(r'ФКУ (\w{2,4})[^\d]+(\d{1,3}) (\w{4,6}) России', r'ФКУ \1-\2 \3 России', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('г. Ростов-на-Дону ул. Тоннельная', 'г. Ростов-на-Дону, ул. Тоннельная', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('ул. <200b>Албазинская, 45<200b>,', 'ул. Албазинская, д. 45,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Япеева, 16\. СИЗО-1 по РТ*$', 'Япеева, 16/1, СИЗО-1 по Республике Татарстан', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Новгородская обл., Валдайский район, г. Валдай', 'Новгородская обл., г. Валдай', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('бул. Ленина 4', 'Бульвар Ленина, д. 4,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('России по РБ','России по Республике Башкортостан', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('ГУФСИН России по Республике Башкортостан', 'УФСИН России по Республике Башкортостан', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('России по РТ','России по Республике Татарстан', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'России по (\w+) обл\.', r'России по \1 области', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('357500', '357502', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('107076,', '107996,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('с. Кочубеевское, Ставропольский край', 'Ставропольский край, с. Кочубеевское', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub('Ростовская обл., Новочеркасск', 'Ростовская область, г. Новочеркасск', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'СИЗО № *', 'СИЗО-', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'ИК № *', 'ИК-', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'обл\.$|обл$', r'области', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'НА ЭТАПЕ|На этапе', r'этап', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'ЭТАП', r'этап', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'АДРЕС УТОЧНЯЕТСЯ|Адрес уточняется|адрес уточняется', r'уточняется', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r', Россия, ', r',', field['prisoner_addr'])
    
    field['prisoner_addr'] = re.sub(r'Тюменская обл., г. Тюмень', 'г. Тюмень', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Тюменская область, г. Тюмень', 'г. Тюмень', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Томская область, г. Томск', 'г. Томск', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Ростовская область, Ростов-на-Дону', 'г. Ростов-на-Дону', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Ростовская область, г. Ростов-на-Дону,', 'г. Ростов-на-Дону,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Россия, респ. Татарстан, г. Казань', r'г. Казань', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Свердловская область, г. Екатеринбург,', r'г. Екатеринбург,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Республика Крым, г. Симферополь,', r'г. Симферополь,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Алтайский край, г. Барнаул,', r'г. Барнаул,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Краснодарский край, г. Краснодар,', r'г. Краснодар,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Красноярский край, г. Красноярск,', r'г. Красноярск,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Кировская область, г. Киров,', r'г. Киров,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Костромская область, г. Кострома,', r'г. Кострома,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Липецкая область, г. Липецк, ', r'г. Липецк,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Тверская область, г. Тверь,', r'г. Тверь,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Ярославская область, г. Ярославль,', r'г. Ярославль,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Владимирская область, г. Владимир,', r'г. Владимир,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Рязанская область, г. Рязань,', r'г. Рязань,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Омская область, г. Омск,', r'г. Омск,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Иркутская область, г. Иркутск,', r'г. Иркутск,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Чеченская Республика, г. Грозный,', r'г. Грозный,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Республика Татарстан, г. Казань,', r'г. Казань,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Республика Бурятия, г. Улан-Удэ,', r'г. Улан-Удэ,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Верхнеуральский район, г. Верхнеуральск,', r'г. Верхнеуральск,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Чугуевский район, с. Чугуевка,', r'с. Чугуевка,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Апшеронский район, г. Хадыженск,', r'г. Хадыженск,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'п. Индустриальный, ул. Кразовская', r'ул. Кразовская', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'г. Колпино, ул. Колпинская,', r'ул. Колпинская,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Новомосковский район, г. Новомосковск,', r'г. Новомосковск,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'г. Архангельск, Приморский район, п. Талаги,', r'г. Архангельск, п. Талаги,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Краснодарский край, Усть-Лабинский район, п. Двубратский', r'Краснодарский край, п. Двубратский', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Ставропольский край, Советский район, г. Зеленокумск,', r'Ставропольский край, г. Зеленокумск,', field['prisoner_addr'])
    field['prisoner_addr'] = re.sub(r'Ленинградская область, Ломоносовский район, Виллозское городское поселение,', r'Ленинградская область, Ломоносовский район,', field['prisoner_addr'])
    
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
  if file_name != None: f = open(file_name, 'w')
  p_list.sort(key=lambda name: name['prisoner_name'])

  for field in p_list:
    if print_format == 'markdown' :
      name = f"[{field['prisoner_name']}]({field['prisoner_link']})"
    else:
      if print_format == '' :
        name = field['prisoner_name']
    # print (name + "- "+field['prisoner_addr'] )
    print (name, "`"+print_date(field)+" г.р.` :addr_delim:", field['prisoner_grad'], ":addr_delim:", field['prisoner_addr'], file=f)
  if file_name != None: f.close()

def print_simle_list(p_list, print_format='', file_name=None):
  if file_name != None: f = open(file_name, 'w')

  for field in p_list:
    if print_format == 'markdown' :
      name = f"[{field['prisoner_name']}]({field['prisoner_link']})"
    else:
      if print_format == '' :
        name = field['prisoner_name']
    print (name, file=f)
  if file_name != None: f.close()

def get_one_month_list(prisoner_list, month):
  month_list = [ i for i in prisoner_list if i['prisoner_bmonth'] == month]
  month_list.sort(key=lambda day: day['prisoner_bday'])
  return month_list


