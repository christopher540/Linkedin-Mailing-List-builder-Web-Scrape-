from bs4 import BeautifulSoup
import requests, json, lxml
import re
import pandas as pd
import pycountry
import streamlit as st
from PIL import Image


page_limit=5

def extract_email(paragraph):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, paragraph)

    if paragraph==None:
      return None
    if match:
        return match.group()
    else:
        return None

image = Image.open('Tap-Smart Logo-1.png')
new_image = image.resize((200, 100))
st.image(new_image)
st.title('Mailing List Generator')
with st.form (key="Registration Form"):
  country=st.text_input('Enter the target country')
  job_title=st.text_input('Enter the target job title')
  industry=st.text_input('Enter the target industry')
  email=st.text_input('Would you like their emails (y/n)')
  email=email.lower()
  submit=st.form_submit_button(label='Submit Query')

if st.button('Get Another Query'):
    st.rerun()


if submit:
  country_code=pycountry.countries.get(name=country).alpha_2.lower()
  if email=='n':
    query=f'{job_title} {industry} -intitle:"profiles" -inurl:"dir/ " site:{country_code}.linkedin.com/in/ OR site:{country_code}.linkedin.com/pub/'
  else:
    query=f'{job_title} {industry} -intitle:"profiles" -inurl:"dir/ " email "@gmail.com" site:{country_code}.linkedin.com/in/ OR site:{country_code}.linkedin.com/pub/'

  # https://docs.python-requests.org/en/master/user/quickstart/#passing-parameters-in-urls
  params = {
      "q": query,          # query example
      "hl": "en",          # language
      "gl": "uk",          # country of the search, UK -> United Kingdom
      "start": 0,          # number page by default up to 0
      #"num": 100          # parameter defines the maximum number of results to return.
  }

  # https://docs.python-requests.org/en/master/user/quickstart/#custom-headers
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
  }

  #change page limit

  page_num=0

  results = []
  while True:
    page_num+=1
    print(f'Page no: {page_num}')

    html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
    print(html)
    soup = BeautifulSoup(html.text, 'lxml')
    profiles = soup.select('div.MjjYud')
    for profile in profiles:
      temp={}
      a_tag = profile.find('a')
      h3_tag=profile.find('h3')
      div_tag=profile.find('div',class_='VwiC3b')

      #Name handle
      if h3_tag:
        temp['Name']=h3_tag.get_text()
      else:
        temp['Name']=None
      results.append(temp)

      #Desc handle
      if div_tag:
        temp['desc']=div_tag.get_text()
      else:
        temp['desc']=None

      #Email handle
      temp['email']=extract_email(str(temp['desc']))

      #Link handle
      if a_tag:
          temp['link']=a_tag['href']
      else:
          temp['link']=None

    if page_num == page_limit:
        break
    elif soup.find('a',id='pnnext'):
      params['start']+=10
    else:
      break

  df=pd.DataFrame(results)
  df=df.dropna()
  st.dataframe(df)