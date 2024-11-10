#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##pip3 install beautifulsoup4
##pip3 install bs4
## python3 parsepzk_top.py --list=mm
## 

import argparse
import os
import re
from datetime import datetime, timedelta

import parsepzk_memopzk_parse
import parsepzk_krymsol_parse
import parsepzk_jwruss_parse
import parsepzk_oi_parse
import parsepzk_rs_parse
import parsepzk_tv_parse
import parsepzk_bot_parse
import parsepzk_common_functions
import parsepzk_proxy_functions


parser = argparse.ArgumentParser(description="Example of a single flag acting as a boolean and an option.")
parser.add_argument("-l", "--list", choices=["mm", "ks", "jw", "oi", "rs", "tv", "bot", "all"], default="", help="get classic format list")
parser.add_argument("-k", "--knock", default="", action="store_true", help="knock into one")
parser.add_argument("-c", "--compare", default="", action="store_true", help="compare all parsed")
parser.add_argument("-use_proxy"  , "--use_proxy",default="", action="store_true", help="not use proxy fo jw_russia")
parser.add_argument("-not_restore", "--not_restore",default="", action="store_true", help="not restore mem data from previous saved")
parser.add_argument("-test"       , "--test",default="", action="store_true", help="test mode")
parser.add_argument("-t", "--truncated",default="", action="store_true", help="get truncated address form")


args = parser.parse_args()

if args.use_proxy: 
  use_proxy = 1
  pr = parsepzk_proxy_functions.start_openvpn()
  print(pr)
  print ("-===== normal part =====-")
else: use_proxy = 0

if args.not_restore: try_to_restore = 0
else: try_to_restore = 1

if args.test: is_test = 1
else: is_test = 0

if args.truncated: is_truncated = 1
else: is_truncated = 0


if args.list:
  # print(args.list)
  fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
  if not os.path.exists(fold_name): os.makedirs(fold_name)
  print("Generate list to folder \"" + fold_name + "\"")
  
  if args.list in ["mm", "all"] :
    print ("Parse memo")
    parsepzk_memopzk_parse.top(fold_name, try_to_restore, truncated = is_truncated, test_mode = is_test )
  if args.list in ["ks","all"] : 
    print ("Parse ks")
    parsepzk_krymsol_parse.top(fold_name)
  if args.list in ["jw", "all"] :
    print ("Parse jw")
    parsepzk_jwruss_parse.top(fold_name, use_proxy, truncated = is_truncated)
    parsepzk_memopzk_parse.get_jwrus_only(fold_name, try_to_restore, truncated = is_truncated, test_mode = is_test )
  if args.list in ["oi", "all"] :
    print ("Parse oi")
    parsepzk_oi_parse.top(fold_name)
  if args.list in ["tv", "all"] :
    print ("Parse tv")
    parsepzk_tv_parse.top(fold_name)
  if args.list in ["rs", "all"] :
    print ("Parse rs")
    parsepzk_rs_parse.top(fold_name)
  if args.list in ["bot", "all"] :
    print ("Parse bot")
    parsepzk_bot_parse.top(fold_name, truncated = is_truncated)

if args.knock:
  fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
  if not os.path.exists(fold_name):
    fold_name = "list_" + datetime.strftime(datetime.today()-timedelta(1), "%Y.%m.%d")
  if not os.path.exists(fold_name):
    print("ERROR: folder \"" + fold_name + "\" not found")
  else:
    print("Go to folder \"" + fold_name + "\"")
    expected_list = ["relig_list.txt", "polit_list.txt", "antiw_list.txt", "oi_list.txt"]
    
    for filename in os.listdir(fold_name):
      print (filename)
      suff = " (" + filename + ")"
      if filename in ["relig_list.txt", "polit_list.txt", "antiw_list.txt"]: suff = " (Мемориал)"
      # if filename in ["bot_relig_list.txt", "bot_polit_list.txt", "bot_antiw_list.txt"]: suff = " (бот)"
      # if filename in ["bot_relig_list.txt"]: suff = " (бот)"
      if filename in ["oi_list.txt"]: suff = " (OI)"
      # if filename in ["jw_list.txt"]: suff = " (JWRUS)"
      # if filename in ["krymsol_list.txt"]: suff = " (Крымская Солидарность)"
      # if filename in ["skaz_list.txt"]: suff = " (СказкиПЗК)"
      # if filename in ["milja_list.txt"]: suff = " (Миля)"
      
      if filename in expected_list:
        with open(os.path.join(fold_name, filename), 'r') as f:
          line = f.readline()
          while line :
            line = re.sub(r"^\[(.*)\]\(.*\) `(.*) г.р.` :addr_delim:.*:addr_delim:", r'[\1] ::: \2 ::: ', line)
            line = re.sub(r"\s+", " ", line)
            line = re.sub(r"::: \d+\.\d+.(\d+) :::", r"::: \1 :::", line)
            if filename in ["relig_list.txt", "polit_list.txt", "antiw_list.txt"]: 
              line = re.sub(r"^(.*) ::: (\d+) ::: .* ФКУ", r"\1 ::: \2 ::: ФКУ", line)
            line = re.sub(r"$", suff, line)
            print(line)
            line = f.readline()

if args.compare:
  fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
  if not os.path.exists(fold_name):
    fold_name = "list_" + datetime.strftime(datetime.today()-timedelta(1), "%Y.%m.%d")
  if not os.path.exists(fold_name):
    print("ERROR: folder \"" + fold_name + "\" not found")
  else:
    print("Go to folder \"" + fold_name + "\"")
    expected_list = ["relig_list.txt", "polit_list.txt", "antiw_list.txt", "oi_list.txt"]
    # expected_list = ["relig_list.txt", "rs_list.txt"]
    
    mm_out_file = open("memo_all.txt", 'w')
    oi_out_file = open("oi_all.txt", 'w')
    rs_out_file = open("rs_all.txt", 'w')
    tv_out_file = open("tv_all.txt", 'w')
    bt_out_file = open("bt_all.txt", 'w')
    jw_out_file = open("jw_all.txt", 'w')
    jw_mem_out_file = open("jw_mem_all.txt", 'w')
      
    for filename in os.listdir(fold_name):

      # mem
      if filename in ["relig_list.txt", "polit_list.txt", "antiw_list.txt" ]:
        print (filename)
        with open(os.path.join(fold_name, filename), 'r') as f:
          parsepzk_common_functions.unified_list_file (f, mm_out_file)
                
      # rs
      if filename in ["rs_list.txt"]:
        print (filename)
        with open(os.path.join(fold_name, filename), 'r') as f:
          parsepzk_common_functions.unified_list_file (f, rs_out_file)
      
      # oi
      if filename in ["oi_list.txt"]:
        print (filename)
        with open(os.path.join(fold_name, filename), 'r') as f:
          parsepzk_common_functions.unified_list_file (f, oi_out_file)
       
      # tv
      if filename in ["tv_list.txt"]:
        print (filename)
        with open(os.path.join(fold_name, filename), 'r') as f:
          parsepzk_common_functions.unified_list_file (f, tv_out_file)
          
      # bot
      if filename in ["bot_list.txt" ]:
        print (filename)
        with open(os.path.join(fold_name, filename), 'r') as f:
          parsepzk_common_functions.unified_list_file (f, bt_out_file)
      
      # jw
      if filename in ["jw_list.txt" ]:
        print (filename)
        with open(os.path.join(fold_name, filename), 'r') as f:
          parsepzk_common_functions.unified_list_file (f, jw_out_file)
    
      if filename in ["jw_mem_list.txt" ]:
        print (filename)
        with open(os.path.join(fold_name, filename), 'r') as f:
          parsepzk_common_functions.unified_list_file (f, jw_mem_out_file)
      
      
    filename = "oi_add_list.txt"
    print (filename)
    with open(filename, 'r') as f:
      parsepzk_common_functions.unified_list_file (f, bt_out_file)
    
    filename = "oi_sub_list.txt"
    print (filename)
    with open(filename, 'r') as f:
      parsepzk_common_functions.unified_list_file (f, oi_out_file)
    
    mm_out_file.close()
    oi_out_file.close()
    rs_out_file.close()
    tv_out_file.close()
    bt_out_file.close()
    jw_out_file.close()
    jw_mem_out_file.close()
    
    parsepzk_common_functions.sort_lines_in_file("memo_all.txt", "memo_all_sort.txt")
    parsepzk_common_functions.sort_lines_in_file("bt_all.txt", "bt_all_sort.txt")
    parsepzk_common_functions.sort_lines_in_file("oi_all.txt", "oi_all_sort.txt")
    parsepzk_common_functions.sort_lines_in_file("tv_all.txt", "tv_all_sort.txt")

if use_proxy:
  parsepzk_proxy_functions.stop_openvpn(pr[0])
  print('finish')


# sed 's/\(\[.*]\)(.*) `\(.*\) г\.р\..*:addr_delim:.*:addr_delim:/\1 \2 :::/' list.txt | sed 's/:::.*ФКУ/ ФКУ/' | sort > full_svobot_list.txt

