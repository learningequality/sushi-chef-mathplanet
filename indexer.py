import requests
import requests_cache
import lxml.html

class Page(object):
    def __init__(self, json):
        self._id = json['id']
        self.name = json['name']
        self.children = json['children']
        self.url = json['url']
        self.parent = json['parent']
        self.level =json['level']
        self.model = json['model']
        
    def get_children(self):
        return [pageindex[item] for item in self.children]
        
    def __repr__(self):
        return "<{}: {}>".format(self._id, self.name)
    
requests_cache.install_cache()
url = "https://www.mathplanet.com/Umbraco/Api/MenuStructureApi/Json?ticks=636891894231922743&id=1057"
j = requests.get(url).json()
print (j["1604"])

pageindex = {}
for item in j:
    pageindex[j[item]["id"]] = Page(j[item])
    
root = pageindex[1604]

for child in root.get_children():  # note: we also need to acquire the intermediary stages!
    for grandchild in child.get_children():
        print (grandchild.get_children()) # there are no deeper levels