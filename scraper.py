from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import pandas as pd

class FincaRaizScraper:
    def __init__(self):
        self.cities = []
        self.current_page = 1
    
        self.base_url = 'https://www.fincaraiz.com.co'
        
        self.test = None
        
        self.driver = webdriver.Chrome(executable_path='driver/chromedriver.exe')
        
        self.data = {
            'Tipo': [],
            'Propiedad': [],
            'Acción': [],
            'Habitaciones': [],
            'Baños': [],
            'Parqueaderos': [],
            'Área construída': [],
            'Área privada': [],
            'Estrato': [],
            'Estado': [],
            'Piso N°': [],
            'Antigüedad': [],
            'Administración': [],
            'Precio m²': [],
            'Dirección': [],
            'Barrio': [],
            'Ciudad': [],
            'Departamento': [],
            'Características': [],
            'Precio (COP)': [],
            'Descripción general': [],
            'No. Fotos': [],
            'Fecha Sacada': [],
            'Fecha Publicada': [],
            'Enlace': []
        }
        
    def set_cities(self, *args):
        for arg in args:
            self.cities.append(arg)
            
    def get_data(self):
        return self.data
    
    def get_dataframe(self):
        return pd.DataFrame(self.data)
    
    def go_to_city(self, city, pages_per_city):
        self.change_tab(0)
        self.current_page = 1
        self.driver.get(self.base_url + '/apartamentos-casas/venta?ubicacion=' + city.replace(' ', '+'))
        sleep(3)
        for page in range(pages_per_city):
            houses = self.get_houses_on_page()
            self.process_houses_on_page()
            self.next_page(city)
        
    def go(self, pages_per_city=10):
        for city in self.cities:
            self.change_tab(0)
            self.go_to_city(city, pages_per_city)
            
    def next_page(self, city):
        self.change_tab(0)
        self.current_page += 1
        self.driver.get(self.base_url + '/apartamentos-casas/venta?ubicacion=' + city + '&pagina=' + str(self.current_page))
        sleep(4)
             
    def get_houses_on_page(self):
        html = self.driver.page_source
        self.test = html
        soup = BeautifulSoup(html, 'html.parser')
        houses = [h.find('a')['href'] for h in soup.find_all('article')]
        return houses
    
    def change_tab(self, n):
        self.driver.switch_to.window(self.driver.window_handles[n])
    
    def process_houses_on_page(self):
        houses = self.get_houses_on_page()
        
        for house in houses:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            house_url = self.base_url + house
            self.driver.get(house_url)
        
        for house in houses:
            self.driver.switch_to.window(self.driver.window_handles[1])
            sleep(1.3)
            self.process_single_house()
            self.driver.close()
            
    def error_on_page(self, house):
        if house.find('svg', {'class':'icon-error-sad'}) is not None:
            return True
    
    def process_single_house(self):        
        house = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        if self.error_on_page(house):
            return
        
        # Get URL
        self.data['Enlace'].append(self.driver.current_url)

        # Get today
        self.data['Fecha Sacada'].append(datetime.now())

        for f in self.data.keys():
            i = 0
            p_tags = house.find_all('p')

            if f == 'Propiedad':
                temp_text = p_tags[2].text.split(' en ')
                if len(temp_text) == 2:
                    self.data[f].append(p_tags[2].text.split(' en ')[0])
                else:
                    self.data[f].append(p_tags[2].text)

            elif f == 'Acción':
                temp_text = p_tags[2].text.split(' en ')
                if len(temp_text) == 2:
                    self.data[f].append(p_tags[2].text.split(' en ')[1])
                else:
                    self.data[f].append(None)

            elif f == 'Barrio' and len(self.data['Barrio']) < len(self.data['Enlace']) and len(p_tags[3].text.split(' - ')) == 3:
                self.data[f].append(p_tags[3].text.split(' - ')[0])

            if f == 'Ciudad' and len(p_tags[3].text.split(' - ')) == 3:
                self.data[f].append(p_tags[3].text.split(' - ')[1])
            elif f == 'Ciudad':
                self.data[f].append(p_tags[3].text.split(' - ')[0])

            if f == 'Departamento' and len(p_tags[3].text.split(' - ')) == 3:
                self.data[f].append(p_tags[3].text.split(' - ')[2])

            elif f == 'No. Fotos':
                self.data[f].append(p_tags[4].text.split(' / ')[-1])

            for p in p_tags:
                if f in p.text and len(self.data[f]) < len(self.data['Enlace']):
                    if f == 'Características':
                        self.data[f].append([c.text for c in p_tags[i+1:-9]])
                        break
                    elif f == 'Código Fincaraíz':
                        self.data[f].append(p.text.split(': ')[-1])
                        break
                    elif f == 'Fecha Publicada' and 'hace' in p.text:
                        self.data[f].append(p.text)
                        break
                    else:
                        self.data[f].append(p_tags[i+1].text.strip('$\xa0').strip('*m²'))
                        break

                i += 1

        # Get Tipo
        if len(self.data['Tipo']) < len(self.data['Enlace']):
            self.data['Tipo'].append(house.find_all('span', {'class': 'MuiChip-label'})[0].text.split(' · ')[0])

        for key in [k for k in self.data.keys() if len(self.data[k]) < len(self.data['Enlace'])]:
            self.data[key].append(None)
               
        self.validate()
               
    def validate(self):
        std_l = len(self.data['Enlace'])
        print('--'*40)
        print(f'Number of items should be {std_l}')
        error_list = []
        for key in self.data.keys():
            if len(self.data[key]) != std_l:
                error_list.append({key: len(self.data[key])})
        print(f'Errors: {error_list}')
        print('--'*40)
        
        return len(error_list) == 0
    
    def trim(self):
        if self.validate() == False:
            bad_len = len(self.data['Enlace'])
            for k in self.data.keys():
                if len(self.data[k]) == bad_len:
                    self.data[k].pop()
        print("Done trimming.")
        return True
    
    def close(self):
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.close()
        self.driver.quit()