#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import os
import re
from datetime import datetime, timedelta

import parsepzk_memopzk_parse
import parsepzk_krymsol_parse
import parsepzk_jwruss_parse


parser = argparse.ArgumentParser(description="Example of a single flag acting as a boolean and an option.")
parser.add_argument("-l", "--list", choices=["mm", "kr", "jw", "all"], default="", help="get classic format list")
parser.add_argument("-k", "--knock", default="", action="store_true", help="knock into one")
parser.add_argument("-use_proxy", "--use_proxy",default="", action="store_true", help="not use proxy fo jw_russia")

args = parser.parse_args()

if args.use_proxy: use_proxy = 1
else: use_proxy = 0

if args.list:
  # print(args.list)
  fold_name = "list_" + datetime.strftime(datetime.today(), "%Y.%m.%d")
  if not os.path.exists(fold_name): os.makedirs(fold_name)
  print("Generate list to folder \"" + fold_name + "\"")
  
  if args.list in ["mm", "all"] :
    print ("Parse memo")
    parsepzk_memopzk_parse.top(fold_name)
  if args.list in ["kr", "all"] : 
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
      if filename in ["relig_list.txt", "polit_list.txt", "antiw_list.txt"]: suff = " (Мемориал)"
      if filename in ["jw_list.txt"]: suff = " (JWRUS)"
      if filename in ["krymsol_list.txt"]: suff = " (Крымская Солидарность)"
      if filename in ["skaz_list.txt"]: suff = " (СказкиПЗК)"
      
      with open(os.path.join(fold_name, filename), 'r') as f:
        line = f.readline()
        while line :
          line = re.sub(" :addr_delim:.*:addr_delim:", ':::::', line)
          line = re.sub("\n$", suff, line)
          print(line)
          line = f.readline()


