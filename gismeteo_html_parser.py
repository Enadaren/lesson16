import json
import requests_html
import bs4
import re

BASE_URL="https://gismeteo.by/"

class BaseParser:
    __storage: list|None = None
    def __init__(self, url:str, query:str=None)->None:
        self.url=url
        self.query=query
    
    def get_page(session,url):
        response= session.get(url)
        if response.status_code==200:
            return response
        
    def parse_country(session,country):
        page = BaseParser.get_page(session,BASE_URL+"catalog/")
        page_text=bs4.BeautifulSoup(page.text,"lxml")
        catalog=page_text.find_all("div","catalog-item-link")
        flag=False
        for row in catalog:
            country_info=row.find("a","link-item").text
            if country_info==country:
                result=row.find("a","link-item").attrs['href']
                flag=True
                break
        if not flag:
            result=None
            print("Sorry, we have not information about this country")
        return result
    
    def parse_city(session,country, city):
        page = BaseParser.get_page(session,BASE_URL+country)
        page_text=bs4.BeautifulSoup(page.text,"lxml")
        catalog=page_text.find_all("a","link-item link-popular")
        flag=False
        for row in catalog:
            city_info=row.text
            if city_info==city:
                result = row.attrs['href']
                flag=True
                break
        if not flag:
            result = None 
            print("Sorry, it is unpopular city. Please, travel to popular city")
        return result
    
    def parse_weather(session, city):
        page = BaseParser.get_page(session,BASE_URL+city+"now/")
        page_text=bs4.BeautifulSoup(page.text,"lxml")
        weather_inform={}
        weather_inform["Temperature"]=page_text.find("div","now-weather").find("span", "unit unit_temperature_c").text
        weather_inform["wind"]={}
        wind=page_text.find("div","now-info-item wind").find("div","unit unit_wind_m_s").text.split("м/c")
        weather_inform["wind"]["module"]=float(wind[0])
        weather_inform["wind"]["source"]=wind[1]
        pressure = page_text.find("div","now-info-item pressure")
        weather_inform["pressure"]=int(re.findall(r"\d+",pressure.find("div", "unit unit_pressure_mm_hg").text)[0])
        humidity=page_text.find("div","now-info-item humidity")
        weather_inform["humidity"]=int(humidity.find("div","item-value").text)
        return weather_inform
    
    def writefile(data,path):
        with open(path,"w") as file:
            json.dump(data,file,indent=4, ensure_ascii=False)
        return

def main():
    country=input("Please, enter the country (on Russian): ")+" "
    session = requests_html.HTMLSession()
    country_catalog=BaseParser.parse_country(session,country)
    if country_catalog is not None:
        city = input("Please, enter the city (on the Russian): ")
        city_page = BaseParser.parse_city(session,country_catalog,city)
        if city_page is not None:
            weather=BaseParser.parse_weather(session,city_page)
            namefile= city_page.split("-")[1] +"_gismeteo_html_parser.json"
            BaseParser.writefile(weather,namefile)
    return

if __name__=="__main__":
    main()