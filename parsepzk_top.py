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


parser = argparse.ArgumentParser(description="Example of a single flag acting as a boolean and an option.")
parser.add_argument("-l", "--list", choices=["mm", "ks", "jw", "all"], default="", help="get classic format list")
parser.add_argument("-k", "--knock", default="", action="store_true", help="knock into one")
parser.add_argument("-use_proxy", "--use_proxy",default="", action="store_true", help="not use proxy fo jw_russia")
parser.add_argument("-not_restore", "--not_restore",default="", action="store_true", help="not restore mem data from previous saved")

args = parser.parse_args()

if args.use_proxy: use_proxy = 1
else: use_proxy = 0

if args.not_restore: try_to_restore = 0
else: try_to_restore = 1

if args.list:
  # print(args.list)
  fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
  if not os.path.exists(fold_name): os.makedirs(fold_name)
  print("Generate list to folder \"" + fold_name + "\"")
  
  if args.list in ["mm", "all"] :
    print ("Parse memo")
    parsepzk_memopzk_parse.top(fold_name, try_to_restore)
  if args.list in ["ks","all"] : 
    print ("Parse ks")
    parsepzk_krymsol_parse.top(fold_name)
  if args.list in ["jw", "all"] :
    print ("Parse jw")
    parsepzk_jwruss_parse.top(fold_name, use_proxy)

if args.knock:
  fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
  if not os.path.exists(fold_name):
    fold_name = "list_" + datetime.strftime(datetime.today()-timedelta(1), "%Y.%m.%d")
  if not os.path.exists(fold_name):
    print("ERROR: folder \"" + fold_name + "\" not found")
  else:
    print("Go to folder \"" + fold_name + "\"")
    for filename in os.listdir(fold_name):
      print (filename)
      suff = " (" + filename + ")"
      # if filename in ["relig_list.txt", "polit_list.txt", "antiw_list.txt"]: suff = " (Мемориал)"
      # if filename in ["bot_relig_list.txt", "bot_polit_list.txt", "bot_antiw_list.txt"]: suff = " (бот)"
      if filename in ["bot_relig_list.txt"]: suff = " (бот)"
      if filename in ["jw_list.txt"]: suff = " (JWRUS)"
      # if filename in ["krymsol_list.txt"]: suff = " (Крымская Солидарность)"
      # if filename in ["skaz_list.txt"]: suff = " (СказкиПЗК)"
      # if filename in ["milja_list.txt"]: suff = " (Миля)"
      
      with open(os.path.join(fold_name, filename), 'r') as f:
        line = f.readline()
        while line :
          line = re.sub(r"^\[", r'', line)
          line = re.sub(r"исправительная колония № ", r'ИК-', line)
          line = re.sub(r"`(.*) г.р.` :addr_delim:.*:addr_delim:", r'\1 :::', line)
          line = re.sub(r" :::.*ФКУ", r" ::: ФКУ", line)
          line = re.sub(r"\n$", suff, line)
          print(line)
          line = f.readline()

# sed 's/\(\[.*]\)(.*) `\(.*\) г\.р\..*:addr_delim:.*:addr_delim:/\1 \2 :::/' list.txt | sed 's/:::.*ФКУ/ ФКУ/' | sort > full_svobot_list.txt

