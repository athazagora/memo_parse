
from bs4 import BeautifulSoup

import requests
import random

import os, sys, subprocess, time, signal

# functions from : https://waksoft.susu.ru/2021/04/15/kak-v-python-ispolzovat-proksi-dlya-podmeny-ip%E2%80%91adresov/

def get_free_proxies():
  url = "https://free-proxy-list.net/"
  # получаем ответ HTTP и создаем объект soup
  soup = BeautifulSoup(requests.get(url).content, "html.parser")
  proxies = []
  
  items = soup.find('div', {'class': 'table-responsive fpl-list'}).find_all("tr")[1:]
  for row in items :
    tds = row.find_all("td")
    try:
      ip = tds[0].text.strip()
      port = tds[1].text.strip()
      host = f"{ip}:{port}"
      proxies.append(host)
    except IndexError:
      continue
  return proxies
  
def get_session(proxies):
  # создать HTTP‑сеанс
  session = requests.Session()
  # выбираем один случайный прокси
  proxy = random.choice(proxies)
  session.proxies = {"http": proxy, "https": proxy}
  return session

def find_workable(proxies, url):
  rememb_session = []

  while True :
    s = get_session(proxies)
  
    try:
      print (f"try {s.proxies}")
      r = s.get(url, timeout=1.5)
      rememb_session.append(s)
      break
    except Exception as e:
      continue
  return rememb_session

def get_workable_proxy_for_url (url):
  url = "https://jw-russia.org/prisoners.html"
  free_proxies = get_free_proxies()
  print(f'Обнаружено бесплатных прокси - {len(free_proxies)}:')
  rememb_session = find_workable(free_proxies, url)
  print ("remembed:")
  for s in rememb_session: 
    print ( s.proxies )
    return s


def start_openvpn ():
  path2cfg = os.path.abspath('client19.ovpn')
  path2log = os.path.abspath('vpn_log.log')
  process_output = open(path2log, 'w')
  # log_file.close()
  
  with open(path2cfg, "a") as myfile:
    # print 
    # myfile.write("\nscript-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf")
    # myfile.close()
    process = subprocess.Popen(['sudo','openvpn', '--auth-nocache', '--config', path2cfg], stdout = process_output, stderr = process_output)
    print (process)
    print ("PID", process.pid)
    print ("sleep 90", process.pid)
    time.sleep(90)

  with open(path2log, "r") as log:
    if log.read().find('Initialization Sequence Completed') != -1:
      print("find(Initialization Sequence Completed)")
      return [process, True]
    else:
      print("not find(Initialization Sequence Completed)")
      return [process, False]


def stop_openvpn(process):
  print(process)
  print(process.pid)
  process.kill()
  pid = process.pid + 1
  print(pid)
  while process.poll() != 0:
    time.sleep(1)
    return
    
