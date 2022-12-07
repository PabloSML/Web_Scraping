from time import sleep
from typing import Optional
import requests
import warnings
from bs4 import BeautifulSoup as soup #parses/cuts  the html
from urllib.parse import urljoin
from plyer import notification
from creds import userName, password

def revisar_nota(userName: str, password: str, subject_code: str) -> Optional[str]:

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

codigo_materia = "22.21"

while (nota := revisar_nota(userName=userName, password=password, subject_code=codigo_materia)) is None:
    sleep(900)

print("Felicitaciones/Lo siento! Tu nota es un", nota)

notification.notify(
    title = 'Está la nota!',
    message = f"Tu nota de {codigo_materia} es...",
    app_name= 'SGA Notafire',
    app_icon = "D:\VSCodeRepos\Web_Scraping\icon.ico",
    timeout = 90000,
    toast=False
)
