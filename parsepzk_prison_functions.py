#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#lib downloaded from https://pypi.org/project/requests/#modal-close
import re
import pandas as pd

def create_prison_dict (file_name, is_debug = 0):
  
  results = []
  tmp_list = []
  
  df = pd.read_excel(file_name, 0) # can also index sheet by name or fetch all sheets
  tmp_list = df.values.tolist()
  for item in tmp_list: item = [str(s).strip() for s in item]
  fku_id = 0
  for item in tmp_list:
    address_parts = re.split(',|\(|\)', item[4])
    address_parts += [str(item [3])]
    address_parts = [s for s in address_parts if not (s in {'', "nan"})]
    # print (address_parts)
    address_parts = [re.sub(r'^ул\. |^г\. |^мкр\. |^д\. |^зд\. |^п\. |^пер\. |^с\. |^бул\. |^пр-т |^стр\. |^р\. п\.  |^ш\. |^пгт |проезд$|квартал ', '', s.strip()) for s in address_parts]
    address_parts = [re.sub(r'—|–|−|-', '-', s.upper()) for s in address_parts]
    address_parts = [re.sub('Ё', 'Е', s)                for s in address_parts]
    address_parts = [re.sub(r'САЛАВАТ−6', 'САЛАВАТ', s) for s in address_parts]
    
    item [0] = re.sub(r'(\(|\))', r'\\\1', item [0])
    # print (item [0])
    
    results.append({
      'fku_id'      : fku_id,
      'fku_reg'     : item [0],
      'fku_type'    : str(item [1]),
      'fku_num'     : str(item [2]),
      'fku_slng'    : str(item [3]),
      'fku_addr'    : item [4],
      'addr_parts'  : address_parts,
      'fku_fsin'    : "",
      'fku_name'    : "",
      'fku_reg_d'   : ""
    })
    fku_id += 1

  df = pd.read_excel(file_name, 1) # can also index sheet by name or fetch all sheets
  tmp_list = df.values.tolist()
  for item in tmp_list: item = [str(s).strip() for s in item]
  for item in tmp_list:
    item [0] = re.sub(r'(\(|\))', r'\\\1', item [0])
    # item [1] = re.sub(r'(\(|\))', r'\\\1', item [1])
    # print ("fcu_reg : ", item [0])
  
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
    i['fku_reg_d'] = re.sub(r".* ПО ", "", i['fku_fsin'].upper())
    i['fku_reg_d'] = re.sub(r'—|–|−|-', '-', i['fku_reg_d'])
  
  df = pd.read_excel(file_name, 2) # can also index sheet by name or fetch all sheets
  tmp_list = df.values.tolist()
  for item in tmp_list: item = [str(s).strip() for s in item]
  
  for i in results:
    for item in tmp_list:
      if i['fku_reg'].strip().upper() == item[0].strip().upper() :
        if is_debug: 
          print ("++++++++++++++++")
          print (i)
          print (item)
        last = 0
        while last < len(item) and not pd.isna(item[last]) : last+=1
        excid_arr = [item[last-2], item[last-1]]
        if is_debug: 
          print (excid_arr)
        
        if re.search(fr"{excid_arr[0]}.*{excid_arr[1]}(,|$)", i['fku_addr']) :
          i['fku_addr'] = re.sub(f"{excid_arr[0]}, ", "", i['fku_addr'])
          if is_debug: 
            print (excid_arr[0]+".*"+excid_arr[1])
            print ("result :", i['fku_addr'])
          
        
        # i['fku_short_addr'] = item[1].strip()
    # if i['fku_fsin'] == "" : print (i)
  
  return results


def part_comparsion (part, int_arr, index_string, address_string, is_debug = 0):
  compare_num = 0
  
  if part.isnumeric() :
    compare_num += part in int_arr
    compare_num += int(part) == int(index_string)
    if is_debug:
      print ("num : ", compare_num, " : ", part, " in string :", index_string, int_arr )
  else :
    if re.search(fr"{part}\b", address_string): compare_num += 1
    if is_debug:
      print ("char: ", compare_num, " : \"" + part + "\" is part of :", address_string)
  return compare_num


def find_max_compare (init_address_string, prison_list, truncated = 0, is_debug = 0):
  
  waigth_id_list = []
  if is_debug:
    print ("======================\ninit_address_string : ", init_address_string )
  prepared_address_string = init_address_string ;
  
  prepared_address_string = re.sub(r'—|–|−|-', '-', prepared_address_string.upper())  #defis
  prepared_address_string = re.sub(r'«|"|»'  , ' ', prepared_address_string)          #quotes
  prepared_address_string = re.sub('Ё'       , 'Е', prepared_address_string)          #ё
  prepared_address_string = re.sub(r'(\d+) (\w{1},)'  , r'\1\2', prepared_address_string) # one letter after num, like д. 24 Б
  prepared_address_string = re.sub(r'^(\d{3}) (\d{3})', r'\1\2', prepared_address_string) # index in one number

  prepared_address_string = re.sub(r'ПО (.*) ОБЛ\b'                   , r'ПО \1 ОБЛАСТИ'       , prepared_address_string)
  prepared_address_string = re.sub(r'АЯ\sОБЛ\b\.?'                    , r'АЯ ОБЛАСТЬ'          , prepared_address_string)
  prepared_address_string = re.sub(r'\sИСПРАВИТЕЛЬНАЯ\sКОЛОНИЯ\s'        , ' ИК '              , prepared_address_string)
  prepared_address_string = re.sub(r'\sСЛЕДСТВЕННЫЙ\sИЗОЛЯТОР\s'         , ' СИЗО '            , prepared_address_string)
  prepared_address_string = re.sub(r'\bТЮРЬМА\b'                         , 'Т'                 , prepared_address_string)
  prepared_address_string = re.sub(r'\bФКУТ\b'                           , 'ФКУ Т'             , prepared_address_string)
  prepared_address_string = re.sub(r'\sФЕДЕРАЛЬНОЕ\sКАЗЕННОЕ\sУЧРЕЖДЕНИЕ\s'  , ' ФКУ '         , prepared_address_string)
  prepared_address_string = re.sub(r'\b(СИЗО|ИК|Т|ЛИУ|КП|ОИК)\b[\s№\-]{1,3}?(\d+)' , r"\1-\2"        , prepared_address_string)
  prepared_address_string = re.sub(r'\bСАНКТ- ПЕТЕРБУРГ\b'            , r"САНКТ-ПЕТЕРБУРГ"     , prepared_address_string)
  
  prepared_address_string = re.sub(r'УФСИН(.*)\sПО\s(.*)РЕСПУБЛИКИ'            , r'УФСИН\1 ПО \2РЕСПУБЛИКЕ'               , prepared_address_string)
  
  prepared_address_string = re.sub(r'ПО (Г\. )?САНКТ-ПЕТЕРБУРГУ И ЛЕНИНГРАДСКОЙ ОБЛАСТИ|ПО СПБ И ЛО|ПО ПЕТЕРБУРГУ И ЛЕНИНГРАДСКОЙ ОБЛАСТИ', 
                                                                    "ПО Г. САНКТ-ПЕТЕРБУРГУ И ЛЕНИНГРАДСКОЙ ОБЛАСТИ"     , prepared_address_string)
  prepared_address_string = re.sub(r'ПО РЕСПУБЛИКЕ КРЫМ И Г\.? СЕВАСТОПОЛЬ'    , 'ПО РЕСПУБЛИКЕ КРЫМ И Г. СЕВАСТОПОЛЮ'   , prepared_address_string)
  prepared_address_string = re.sub(r'ПО ЧУВАШИИ|ПО ЧУВАШСКОЙ РЕСПУБЛИКЕ|ПО ЧР' , 'ПО ЧУВАШСКОЙ РЕСПУБЛИКЕ - ЧУВАШИИ'     , prepared_address_string)
  prepared_address_string = re.sub(r'ПО УДМУРТИИ|ПО РЕСПУБЛИКЕ УДМУРТИЯ|ПО УР' , 'ПО УДМУРТСКОЙ РЕСПУБЛИКЕ'              , prepared_address_string)
  prepared_address_string = re.sub(r'ПО ХМАО'                                  , 'ПО ХМАО - ЮГРЕ'                        , prepared_address_string)
  prepared_address_string = re.sub(r'ПО ЯНАО'                                  , 'ПО ЯМАЛО-НЕНЕЦКОМУ АВТОНОМНОМУ ОКРУГУ' , prepared_address_string)
  # prepared_address_string = re.sub(r'ПО РЕСПУБЛИКЕ САХА \(ЯКУТИЯ\)'            , 'ПО РЕСПУБЛИКЕ САХА'                    , prepared_address_string)
  # prepared_address_string = re.sub(r'(\(|\))', r'\\\1', prepared_address_string)
  

  special_mode_dict = { 'УКП' : 0 , 'ПФРСИ' : 0 , 'МОБ' : 0, 'предположительно' : 0, 'отряд \d+' : 0}
  for key in special_mode_dict :
    if re.search(fr"\b{key}\b", prepared_address_string):
      prepared_address_string = re.sub(fr'\b{key}\b', '', prepared_address_string)
      special_mode_dict[key] = 1
      if is_debug:
        print ("find ", key, " in prepared_address_string: ", prepared_address_string)
  
  index_string = re.findall(r'\d{6}', prepared_address_string)
  if len (index_string) > 0 :
    cleaned_address_string = re.sub(index_string[0] , '', prepared_address_string)
    index_string = index_string[0].strip()
  else :
    cleaned_address_string = prepared_address_string
    index_string = -1
  
  if is_debug: 
    print ("prepared_address_string string: ", prepared_address_string )
  
  fku_string = re.findall(r'\sСИЗО\b-? ?\d+|\sИК\b-? ?\d+|\sКП\b-? ?\d+|\sТ\b-? ?\d+|\sЛИУ\b-? ?\d+|\sТ\b|\b\w+\sВК\b', cleaned_address_string)
  if len (fku_string) == 0 :
    if is_debug: print ("Not found fku_type in \"", init_address_string, "\"")
    return init_address_string
  
  if is_debug: print ("fku_string", fku_string)
  cleaned_address_string = re.sub(fku_string[0] , '', cleaned_address_string)
  fku_string = fku_string[0].strip()
  
  int_arr = re.findall(r'\d+', cleaned_address_string)
  
  if is_debug: 
    print ("Reserched string: ", init_address_string )
    print ("Extracted fku_string : ", fku_string)
    print ("Extracted index_string : ", index_string)
    print (int_arr)
    print ("curent string: ", cleaned_address_string)
    print ("++++++++++++++++")
  
  pattern_found = 0
  for item in prison_list:
    compare_num = 0
    fku_reg_d = re.sub(r'(\(|\))', r'\\\1', item['fku_reg_d'])
    # print (fku_reg_d)
    
    if re.search(fr"\b{item['fku_name']}\b.*\s{fku_reg_d}|{item['fku_reg'].upper()}\b.*\b{item['fku_name']}\b", prepared_address_string):
      compare_num += 10
      pattern_found |= 1
      if is_debug: print (compare_num, " : ", prepared_address_string, " : pattern find : ", item['fku_name'], " по ", item['fku_reg_d'])
    else:
      compare_num += fku_string == item['fku_name']
      if is_debug: print (compare_num, " : ", fku_string, " == ", item['fku_name'] )
      compare_num += cleaned_address_string.find(item['fku_reg'].upper()) > 0
      if is_debug: print (compare_num, " : ", cleaned_address_string, " : ", item['fku_reg'].upper())
    
    for part in item ['addr_parts']: 
      compare_num += part_comparsion (part, int_arr, index_string, cleaned_address_string, is_debug)
    
    waigth_id_list.append({
      'fku_id'      : item['fku_id'],
      'fku_addr'    : item['fku_addr'] + ", ФКУ " + item['fku_name'] + " " + item['fku_fsin'],
      'fku_addr_d'  : "ФКУ " + item['fku_name'] + " " + item['fku_fsin'],
      'fku_waigth'  : compare_num
    })
  
  waigth_list = [ i['fku_waigth'] for i in waigth_id_list ]
  max_id_list = [ i for i in waigth_id_list if i['fku_waigth'] == max ( waigth_list ) ]
  if truncated:
    result_addr = max_id_list[0]['fku_addr_d']
  else:
    result_addr = max_id_list[0]['fku_addr']
  
  for key in special_mode_dict :
    if special_mode_dict[key] :
      if key in ["УКП", "ПФРСИ", "МОБ"]:
        result_addr = re.sub(r'ФКУ', fr"{key} при ФКУ" , result_addr)
      else:
        result_addr = result_addr + fr" ({key})"
  
  if len (max_id_list) != 1 : 
    print ("More then one case for reserched string: ", init_address_string )
    print ("Extracted fku_string : ", fku_string)
    print ("Extracted index_string : ", index_string)
    print (int_arr)
    print ("curent string: ", cleaned_address_string)
    if (max_id_list[0]['fku_waigth'] < 5): result_addr = init_address_string
    print ("return string: ", result_addr)
    print ("----------------")
  
  if pattern_found != 1 :
    print ("Pattern not found for reserched string: ", init_address_string )
    print ("Extracted fku_string : ", fku_string)
    print ("Extracted index_string : ", index_string, int_arr)
    print ("curent string: ", cleaned_address_string)
    print ("++++++++++++++++")

  if is_debug:
    print ("return string: ", result_addr)
    print ("----------------")
  
  return result_addr
  
  
