#importing modules
from run import app
from processing import *
from load_json import *

def get_query_type():

    '''This function is used for extracting the query_type from the request.'''

    #ectracting json data from request
    data = request.get_json()

    #extracting query_type and filters from request
    query_type = data.get('query_type')
    
    return query_type

#function for getting query_type from request
def get_filters():

    """This function is used for extracting the filters from the request"""
    
    #extracting json data from request
    data = request.get_json()

    #extracting filters from request   
    filters = data.get('filters')

    return filters

@app.route('/', methods = ['POST'])
def main():

    """handles the request. It loads the data from netaporter_gb_similar.json file using the load_json module.
    when the data is loaded, it extracts the query_type and the filters from the request.
    Then it checks the query_type and calls the functions present in processing.py module based on the type of request."""

    #path of json  data file
    file_path = 'netaporter_gb_similar.json'

    #loading json data
    product_json = load_json(file_path)

    #extracting query_type and filters from request
    query_type = get_query_type()
    filters = get_filters()

    if filters == None:
        filters = []

    #creating object of class Process
    process = Process(product_json, query_type, filters)

    #checking query type
    if query_type == 'discounted_products_list':
        result = process.get_discouted_products_list()
        return result
        
    elif query_type == 'discounted_products_count|avg_discount':
        result = process.get_discounted_products_count_and_avg_discount()
        return result
        
    elif query_type == 'expensive_list':
        result = process.get_expencive_list()
        return result
        
    elif query_type == 'competition_discount_diff_list':
        result = process.get_competition_discount_diff_list()
        return result
        






   
