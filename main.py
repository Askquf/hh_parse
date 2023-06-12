import time
import json
import requests
from fake_headers import Headers
import bs4
from params import PARAMS
import pyprind

def get_headers():
    return Headers(browser='firefox', os='win').generate()

def get_page_soup(url, params=None):
    response = requests.get(url, params=params, headers=get_headers()).text
    return bs4.BeautifulSoup(response, 'lxml')

def get_all_vacancies():
    data = []
    params = PARAMS
    URL = 'https://spb.hh.ru/search/vacancy'
    soup = get_page_soup(URL, params)
    number_vacancies = soup.find('h1', class_='bloko-header-section-3')
    pages = int(number_vacancies.text.split(' ')[0].replace('\xa0', '')) // 20 + 1
    bar = pyprind.ProgBar(pages)
    for i in range(pages):
        vacancies = soup.find_all(class_='serp-item')
        for vac in vacancies:
            data.append(vac.find('a', class_='serp-item__title').attrs['href'])
        time.sleep(0.33)
        params['page'] = i + 1
        soup = get_page_soup(URL, params)
        bar.update()
    return data

def save_vacancies_data(data):
    with open('data.json', 'w') as f:
        vacancy_data = []
        bar = pyprind.ProgBar(len(data))
        for vac in data:
            soup = get_page_soup(vac)
            description = soup.find('div', 'vacancy-description')
            if description is not None:
                description = description.text.lower()
                if 'django' in description and 'flask' in description:
                    salary = soup.find('span', class_='bloko-header-section-2').text
                    company_name = soup.find('span', class_='vacancy-company-name').text
                    address = soup.find(attrs={'data-qa': 'vacancy-view-raw-address'})
                    if address is None:
                        address = soup.find(attrs={'data-qa': 'vacancy-view-location'})
                    vacancy_data.append({'company': company_name, 'salary': salary, 'address': address.text, 'link': vac})
            time.sleep(0.33)
            bar.update()
        json.dump(vacancy_data, f, ensure_ascii=False)

def main():
    save_vacancies_data(get_all_vacancies())

if __name__ == '__main__':
    main()