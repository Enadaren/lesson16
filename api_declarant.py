import requests
import json

BASE_URL = "https://belarusborder.by/info/monitoring-new?token=test&checkpointId="

BASE_PORTAL = {"Бенякони":"bts47d5f-6420-4f74-8f78-42e8e4370cc4", 
               "Берестовица":"7e46a2d1-ab2f-11ec-bafb-ac1f6bf889c1",
               "Брест":"a9173a85-3fc0-424c-84f0-defa632481e4",
               "Григоровщина":"bts47d5f-6420-4f74-8f78-42e8e4370cc4",
               "Каменный Лог":"b60677d4-8a00-4f93-a781-e129e1692a03",
               "Козловичи":"98b5be92-d3a5-4ba2-9106-76eb4eb3df49",
               "Котловка":"b7b368c7-d00c-11e7-a46c-001517da0c91",
               "Урбаны":"22f8ccbf-e260-4f9f-926c-e0c0874aec52"
               }

BASE_TRANSPORT = {"легковая": "car","грузовая":"truck"}
class BaseParser:
    storage: list|None = None
      
    def __init__(self, url: str, query: str = None) -> None:
        self._url = url
        self._query = query

    def get_zone(checkpoint):
        url=BASE_URL+BASE_PORTAL[checkpoint]
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        
    def get_Queue(transport, data):
        key=BASE_TRANSPORT[transport.lower()]+"LiveQueue"
        Queue = data[key]
        return (Queue)
    
    def writefile(data,path):
        with open(path,"w") as file:
            json.dump(data,file,indent=4, ensure_ascii=False)
        return
    
def main():
    checkpoint=input("Введіте погранічный пункт: ")
    transport = input("Очередь легковая ілі грузовая: ")
    zone_inform=BaseParser.get_zone(checkpoint)
    queue = BaseParser.get_Queue(transport,zone_inform)
    filename=checkpoint+"_"+transport+".json"
    BaseParser.writefile(queue,filename)
    return

if __name__=="__main__":
    main()