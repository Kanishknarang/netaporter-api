#importing modules
from run import app
from processing import *

@app.route('/main', methods = ['POST'])
def main():

    #path of json  data file
    file_path = 'netaporter_gb_similar.json'

    #loading json data
    product_json = load_json(file_path)

    #extracting query_type and filters from request
    query_type = get_query_type()
    filters = get_filters()

    if filters == None:
        filters = []

    
    #checking query type
    if query_type == 'discounted_products_list':
        result = get_discouted_products_list(product_json, filters)
        return result
        
    elif query_type == 'discounted_products_count|avg_discount':
        result = get_discounted_products_count_and_avg_discount(product_json, filters)
        return result
        
    elif query_type == 'expensive_list':
        result = get_expencive_list(product_json, filters)
        return result
        
    elif query_type == 'competition_discount_diff_list':
        result = get_competition_discount_diff_list(product_json, filters)
        return result
        






   
