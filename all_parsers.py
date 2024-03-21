import requests
import json
import requests_html
import bs4
import re
from abc import ABC, abstractmethod

class BaseParser(ABC):
    __storage: list|None = None

    def __init__(self, url:str, query=None, session:requests_html.HTMLSession = None)->None:
        self.url=url
        self.query=query
        self.session = session

    def _get_page(self, num=1):
        response= self.session.get(self.url+self.query,params={"page":num})
        if response.status_code==200:
            return response
    
    def writefile(self,data,path):
        with open(path,"w") as file:
            json.dump(data,file,indent=4, ensure_ascii=False)
        return
    
class HmdbParser(BaseParser):    
    def create_filter(self):
        filter="?utf8/=✓&"
        for key in self.query:
            filter = filter+key+"=1&"
        filter=filter+"filter=true"
        self.query=filter
        return self
    
    def get_number_of_pages(self):
        page= self._get_page(1)
        page_text=bs4.BeautifulSoup(page.text,"lxml")
        info_page=page_text.find("li","last next")
        if info_page is not None:
            link=str(str(info_page.contents[1]).split("page=")[1])
            last_page=int(link.split("&")[0])
        else:
            last_page=1
        return last_page
    
    def get_data(self):
        last_page = self.get_number_of_pages()
        dict_data = {}
        dict_data["name"]=list()
        dict_data["HMDB"]=list()
        dict_data["weight"]=list()
        for i in range(1, last_page+1):
            page=self._get_page(i)
            page_text=bs4.BeautifulSoup(page.text,"lxml")
            info=page_text.find_all("td","metabolite-name")          
            for el in info:
                dict_data["name"].append(el.text)
            info=page_text.find_all("td","metabolite-link")
            for el in info:
                dict_data["HMDB"].append(el.find("a","btn-card").text)
            info=page_text.find_all("td","weight-value")
            for el in info:
                try: 
                    weight=float(el.contents[len(el.contents)-1])
                except:
                    weight = None
                dict_data["weight"].append(weight)
        return dict_data
    
    def transform(self,data):
        transform_data=list()
        for i in range(len(data["name"])):
            el_dict={}
            el_dict["name"]=data["name"][i]
            el_dict["HMDB"]=data["HMDB"][i]
            el_dict["weight"]=data["weight"][i]
            transform_data.append(el_dict)
        return transform_data
    

class GismeteoParser(BaseParser):
    def parse_country(self,country):
        page = self._get_page()
        page_text=bs4.BeautifulSoup(page.text,"lxml")
        catalog=page_text.find_all("div","catalog-item-link")
        flag=False
        for row in catalog:
            country_info=row.find("a","link-item").text
            if country_info==country:
                self.query=row.find("a","link-item").attrs['href']
                flag=True
                break
        if not flag:
            self.query=None
            print("Sorry, we have not information about this country")
        return self
    
    def parse_city(self, city):
        page = self._get_page()
        page_text=bs4.BeautifulSoup(page.text,"lxml")
        catalog=page_text.find_all("a","link-item link-popular")
        flag=False
        for row in catalog:
            city_info=row.text
            if city_info==city:
                self.query = row.attrs['href'] +"now/"
                flag=True
                break
        if not flag:
            self.query = None 
            print("Sorry, it is unpopular city. Please, travel to popular city")
        return self
    
    def parse_weather(self):
        page = self._get_page()
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


BASE_PORTAL = {"Бенякони":"53d94097-2b34-11ec-8467-ac1f6bf889c0", 
               "Берестовица":"7e46a2d1-ab2f-11ec-bafb-ac1f6bf889c1",
               "Брест":"a9173a85-3fc0-424c-84f0-defa632481e4",
               "Григоровщина":"ffe81c11-00d6-11e8-a967-b0dd44bde851",
               "Каменный Лог":"b60677d4-8a00-4f93-a781-e129e1692a03",
               "Козловичи":"98b5be92-d3a5-4ba2-9106-76eb4eb3df49",
               "Котловка":"b7b368c7-d00c-11e7-a46c-001517da0c91",
               "Урбаны":"22f8ccbf-e260-4f9f-926c-e0c0874aec52"
               }
BASE_TRANSPORT = {"легковая": "car","грузовая":"truck"}
class DeclarantParser(BaseParser):

    def _get_page(self, num=1):
        response= requests.get(self.url+self.query)
        if response.status_code==200:
            return response

    def get_zone(self, checkpoint):
        self.query=BASE_PORTAL[checkpoint]
        return self

    def get_Queue(self,transport, data):
        key=BASE_TRANSPORT[transport.lower()]+"LiveQueue"
        Queue = data[key]
        return (Queue)

BASE_ORGANISM = {"человек": "9606", "мышь": "10090", "крыса": "10116","бык": "9913"}

class UniprotParser(BaseParser):

    def _get_page(self, num=1):
        response= requests.get(self.url+self.query)
        if response.status_code==200:
            return response
        
    def combine_reqest(self,request,species):
        if species!="NA":
            self.query = "(" +request + ") AND (model_organism:" +BASE_ORGANISM[species] +")"
        else:
            self.query = "(" +request + ")"
        return self
    
def hmdb_parser():
    session = requests_html.HTMLSession()
    parser=HmdbParser(url="http://hmdb.ca/metabolites",session=session)
    parser.query=input("Enter filter criteria by space: ").split(" ")
    for_name=parser.query
    parser=parser.create_filter() 
    data=parser.get_data()
    dictionary_data=parser.transform(data)
    name_file="common_parser/hmdb_"+"_".join(for_name)+"_html_parser.json"
    parser.writefile(dictionary_data,name_file)
    return

def gismeteo_parser():
    session = requests_html.HTMLSession()
    parser=GismeteoParser(url="https://gismeteo.by/",query="catalog/",session=session)
    country=input("Please, enter the country (on Russian): ")+" "
    parser=parser.parse_country(country)
    if parser.query is not None:
        city = input("Please, enter the city (on the Russian): ")
        parser = parser.parse_city(city)
        if parser.query is not None:
            weather=parser.parse_weather()
            namefile= "common_parser/"+parser.query.split("-")[1] +"_gismeteo_html_parser.json"
            parser.writefile(weather,namefile)
    return

def declarant_parser():
    checkpoint=input("Введіте погранічный пункт: ")
    transport = input("Очередь легковая ілі грузовая: ")
    parser=DeclarantParser(url="https://belarusborder.by/info/monitoring-new?token=test&checkpointId=")
    parser=parser.get_zone(checkpoint)
    zone_inform=parser._get_page().json()
    queue = parser.get_Queue(transport,zone_inform)
    filename="common_parser/"+checkpoint+"_"+transport+"_declarant_api_parser.json"
    parser.writefile(queue,filename)
    return

def uniprot_parser():
    ask=input("Enter quaery: ")
    species = input("Enter species or NA: ")
    parser=UniprotParser(url="https://rest.uniprot.org/uniprotkb/search?fields=accession,reviewed,id,protein_name,gene_names,organism_name,length&query=")
    combine_request=parser.combine_reqest(ask,species)
    information = parser._get_page().json()
    if species !="NA":
        filename="common_parser/"+ask+"_"+species+".json"
    else:
        filename = ask +".json"
    parser.writefile(information["results"],filename)
    return

def main():
    answer = input("which site do you need? 1- HMBD, 2- Gismeteo, 3 - mon.declarant, 4 - uniprot: ")
    match answer:
        case "1":
            hmdb_parser()
        case "2":
            gismeteo_parser()
        case "3":
            declarant_parser()
        case "4":
            uniprot_parser()
    return

if __name__=="__main__":
    main()