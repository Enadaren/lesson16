import requests
import json

BASE_URL = "https://rest.uniprot.org/uniprotkb/search?fields=accession,reviewed,id,protein_name,gene_names,organism_name,length&query="

BASE_ORGANISM = {"человек": "9606", "мышь": "10090", "крыса": "10116","бык": "9913"}

storage: list|None = None
class BaseParser:      
    def __init__(self, url: str, query: str = None) -> None:
        self._url = url
        self._query = query

    def combine_reqest(request,species):
        if species!="NA":
            result = BASE_URL + "(" +request + ") AND (model_organism:" +BASE_ORGANISM[species] +")"
        else:
            result = BASE_URL + "(" +request + ")"
        return result
    
    def get_inform(url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        
    def writefile(data,path):
        with open(path,"w") as file:
            json.dump(data,file,indent=4, ensure_ascii=False)
        return
    
def main():
    ask=input("Enter quaery: ")
    species = input("Enter species or NA: ")
    combine_request=BaseParser.combine_reqest(ask,species)
    information = BaseParser.get_inform(combine_request)
    if species !="NA":
        filename=ask+"_"+species+".json"
    else:
        filename = ask +".json"
    BaseParser.writefile(information["results"],filename)
    return

if __name__=="__main__":
    main()