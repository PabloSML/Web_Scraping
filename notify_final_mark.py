# OS and Python Imports
from time import sleep
from typing import Optional
import warnings
# Web Scraping Imports
import requests
from bs4 import BeautifulSoup as soup #parses/cuts  the html
from urllib.parse import urljoin
# Desktop Notification Imports
from plyer import notification
# Email Notification Imports
from email.message import EmailMessage
import ssl
import smtplib
# Credential Imports
from creds import userName, password, email_sender, email_password, email_reciever

def check_mark(userName: str, password: str, subject_code: str) -> Optional[str]:

    with requests.Session() as s:

        res = s.get('https://sga.itba.edu.ar', allow_redirects=False)

        while res.status_code == 302:
            res = s.get(res.headers['Location'], allow_redirects=False, cookies=res.cookies)

        # print(res.text)

        payload = {
            'user': userName,
            'password': password,
            'js': '1',
            'login': 'Ingresar'
        }

        page_soup = soup(res.content, "html.parser") #parses/cuts the HTML

        # print(page_soup)
        action = page_soup.find('form').get_attribute_list('action')[0]

        res = s.post(urljoin(res.url, action), data=payload, allow_redirects=False, cookies=res.cookies)

        while res.status_code == 302:
            res = s.get(res.headers['Location'], allow_redirects=False, cookies=res.cookies)

        # Página de Inicio
        page_soup = soup(res.content, "html.parser") #parses/cuts the HTML

        # print(page_soup.find('td').find_next('tr').find('td'))

        # Feo pero bueno no se usar BS
        mi_leg = page_soup.find('li')
        for i in range(3):
            mi_leg = mi_leg.find_next_sibling()
        mi_leg = mi_leg.find_next('li')
        href = mi_leg.find('a')['href']

        res = s.get(urljoin(res.url, href), allow_redirects=False, cookies=res.cookies)

        while res.status_code == 302:
            res = s.get(res.headers['Location'], allow_redirects=False, cookies=res.cookies)

        # Mi Legajo
        page_soup = soup(res.content, "html.parser")
        href = page_soup.find("li",{"class":"tab3"}).find('a').get('href')

        res = s.get(urljoin(res.url, href), allow_redirects=False, cookies=res.cookies)

        while res.status_code == 302:
            res = s.get(res.headers['Location'], allow_redirects=False, cookies=res.cookies)
        
        # Datos del Alumno
        page_soup = soup(res.content, "html.parser")
        href = page_soup.find("li",{"class":"tab3"}).find_next("li",{"class":"tab3"}).find('a').get('href')

        res = s.get(urljoin(res.url, href), allow_redirects=False, cookies=res.cookies)

        while res.status_code == 302:
            res = s.get(res.headers['Location'], allow_redirects=False, cookies=res.cookies)

        # Loading Historia académica
        page_soup = soup(res.content, "html.parser")
        script_rancio = page_soup.find("script",{"id":"wicket-ajax-base-url"}).find_all_next('script')[1].string.split("'")[1]

        res = s.get(urljoin(res.url, script_rancio), allow_redirects=False, cookies=res.cookies)

        while res.status_code == 302:
            res = s.get(res.headers['Location'], allow_redirects=False, cookies=res.cookies)
        
        # Historia académica
        warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
        page_soup = soup(res.content, "lxml")
        for tr in page_soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
            td2 = tds[1]
            namespan = td2.find('span')
            if namespan is None:
                continue
            if namespan.string.startswith(subject_code):
                td_nota = tds[3].find('div')
                if td_nota is None:
                    return None
                else:
                    span_nota = td_nota.find('div').find('span').string
                    return span_nota

def send_email(sender: str, password: str, reciever: str, subject_code: str):
    subject = f"Nota de final - Materia {subject_code}"
    body = """
    ¡Tu nota del final está disponible!
    """

    em = EmailMessage()
    em['From'] = sender
    em['To'] = reciever
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(user=sender, password=password)
        smtp.sendmail(from_addr=sender, to_addrs=reciever, msg=em.as_string())

def desktop_notify(mark: str, subject_code: str, give_me_a_heart_attack=False):
    if give_me_a_heart_attack:
        my_message = f"Tu nota de {subject_code} es {mark}!!"
    else:
        my_message = f"Tu nota de {subject_code} es..."
        print("Felicitaciones/Lo siento! Tu nota es un", mark)

    notification.notify(
        title = 'Está la nota!',
        message = my_message,
        app_name= 'SGA Notafire',
        app_icon = "D:\VSCodeRepos\Web_Scraping\icon.ico",
        timeout = 90000,
        toast=False
    )


codigo_materia = "22.21"

while (nota := check_mark(userName=userName, password=password, subject_code=codigo_materia)) is None:
    sleep(900)

send_email(sender=email_sender, password=email_password, reciever=email_reciever, subject_code=codigo_materia)
desktop_notify(mark=nota, subject_code=codigo_materia, give_me_a_heart_attack=False)
