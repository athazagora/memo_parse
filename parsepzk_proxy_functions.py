
from bs4 import BeautifulSoup

import requests
import re
import random

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
      print (f"curent {s.proxies}")
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
