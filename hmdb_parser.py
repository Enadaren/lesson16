import json
import requests_html
import bs4
import re

BASE_URL="http://hmdb.ca/metabolites"
class BaseParser:
    __storage: list|None = None
    def __init__(self, url:str, query:str=None)->None:
        self.url=url
        self.query=query
    
    def get_page(num,session,url):
        response= session.get(url,params={"page":num})
        if response.status_code==200:
            return response
    
    def create_filter(list):
        filter="?utf8/=✓&"
        for key in list:
            filter = filter+key+"=1&"
        filter=filter+"filter=true"
        return filter
    
    def get_number_of_pages(session,filter):
        page= BaseParser.get_page(1,session, BASE_URL + filter)
        page_text=bs4.BeautifulSoup(page.text,"lxml")
        info_page=page_text.find("li","last next")
        if info_page is not None:
            link=str(str(info_page.contents[1]).split("page=")[1])
            last_page=int(link.split("&")[0])
        else:
            last_page=1
        return last_page
    
    def get_data(session, filter):
        last_page = BaseParser.get_number_of_pages(session,filter)
        dict_data = {}
        dict_data["name"]=list()
        dict_data["HMDB"]=list()
        dict_data["weight"]=list()
        for i in range(1, last_page+1):
            page=BaseParser.get_page(i,session,BASE_URL+filter)
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
    
    def transform(data):
        transform_data=list()
        for i in range(len(data["name"])):
            el_dict={}
            el_dict["name"]=data["name"][i]
            el_dict["HMDB"]=data["HMDB"][i]
            el_dict["weight"]=data["weight"][i]
            transform_data.append(el_dict)
        return transform_data
    
    def writefile(data,path):
        with open(path,"w") as file:
            json.dump(data,file,indent=4, ensure_ascii=False)
        return
    

def main():
    filter=input("Enter filter criteria by space: ").split(" ")
    filter_format=BaseParser.create_filter(filter) 
    session = requests_html.HTMLSession()
    data=BaseParser.get_data(session,filter_format)
    dictionary_data=BaseParser.transform(data)
    name_file="hmdb_"+"_".join(filter)+"_html_parser.json"
    BaseParser.writefile(dictionary_data,name_file)
    return

if __name__=="__main__":
    main()