import json
#function for loading json file
def load_json(path):

    #loading json data    
    product_json=[]
    with open(path,encoding='utf-8') as fp:
        for product in fp.readlines():
            product_json.append(json.loads(product))    

    return product_json