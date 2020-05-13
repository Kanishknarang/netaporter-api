import json
from flask import request, jsonify

#function for loading json file
def load_json(path):

    #loading json data    
    product_json=[]
    with open(path,encoding='utf-8') as fp:
        for product in fp.readlines():
            product_json.append(json.loads(product))    

    return product_json

#function for getting query_type from request
def get_query_type():

    #ectracting json data from request
    data = request.get_json()

    #extracting query_type and filters from request
    query_type = data.get('query_type')
    
    return query_type

#function for getting query_type from request
def get_filters():
    
    #extracting json data from request
    data = request.get_json()

    #extracting filters from request   
    filters = data.get('filters')

    return filters
    

#function for checking if discount follows the filter condition
def check_discount(product, operator, operand2):
    #calculating discount
    discount = 100*((product['price']['regular_price']['value'] - product['price']['offer_price']['value'])/product['price']['regular_price']['value'])

    if operator == '>':
        if discount > int(operand2):
            return True
            
        else:
            return False
            

    elif operator == '==':
        if discount == int(operand2):
            return True
        else:
            return False

    else:
        if discount < int(operand2):
            return True
        else:
            return False


def check_brand_name(product, operand2):
    if product['brand']['name'] == operand2:
        return True
    else:
        return False


def check_discount_dif_and_competition(product, competition, discount_diff_operand2 , discount_diff_operator):
    
    basket_price = product['price']['basket_price']['value']
            
    f=1
    
    for knn_item in  product['similar_products']['website_results'][competition]['knn_items']:
        similar_product_basket_price = knn_item['_source']['price']['basket_price']['value']
        discount_diff = ((basket_price - similar_product_basket_price)/basket_price)*100
        
        
        if discount_diff_operator == '>':
            if discount_diff > int(discount_diff_operand2):
                return True           

        elif discount_diff_operator == '==':
            if discount_diff == int(discount_diff_operand2):
                return True           
        
        else:
            if discount_diff < int(discount_diff_operand2):
                return True
    return False
            
        

def get_discouted_products_list(product_json, filters):
    #list will contain the required result
    result = []
    
    #iterating through all the products in json data
    for product in product_json:


        #initializing variables
        competition = None
        discount_diff_operand1 = None
        discount_diff_operannd2 = None
        discount_diff_operator = None

        #flag variable
        f=0

        #iterating through the filters
        for filter in filters:

            #getting filter parameters from each filter
            operand1 = filter['operand1']
            operator = filter['operator']
            operand2 = filter['operand2']

            #print(operand1)

            if operand1 == 'discount':

                if not check_discount(product, operator , operand2):
                    f=1
                    break

            elif operand1 == 'brand.name':

                if check_brand_name(product, operand2) == False:
                    f=1
                    break

            elif operand1 == 'competition':
                
                if discount_diff_operand1 != None:

                    if not check_discount_dif_and_competition(product, operand2, discount_diff_operannd2, discount_diff_operator):
                        f=1
                        break
                else:
                    competition = operand2
                    

            elif operand1 == 'discount_diff':

                if competition != None:

                    if not check_discount_dif_and_competition(product, competition, operand2, operator):
                        f=1
                        break
                        

                else:
                    discount_diff_operand1 = operand1
                    discount_diff_operannd2 = operand2
                    discount_diff_operator = operator
    
        if f==0: 
            result.append(product['_id'])
            
            print(product['brand']['name'])                            

    return jsonify({'discounted_products_list' : result}) 

def get_discounted_products_count_and_avg_discount(product_json, filters):
    #list will contain the required result
    result = []

    product_count = 0
    discount_sum = 0
    
    #iterating through all the products in json data
    for product in product_json:
        
        #calculating discount
        discount = 100*((product['price']['regular_price']['value'] - product['price']['offer_price']['value'])/product['price']['regular_price']['value'])

        

        #initializing variables
        competition = None
        discount_diff_operand1 = None
        discount_diff_operannd2 = None
        discount_diff_operator = None

        #flag variable
        f=0

        #iterating through the filters
        for filter in filters:

            #getting filter parameters from each filter
            operand1 = filter['operand1']
            operator = filter['operator']
            operand2 = filter['operand2']

            if operand1 == 'discount':
                
                if not check_discount(product,operator, operand2):
                    f=1
                    break

            elif operand1 == 'brand.name':

                if check_brand_name(product, operand2) == False:
                    f=1
                    break

            elif operand1 == 'competition':
                if discount_diff_operand1 != None:

                    if not check_discount_dif_and_competition(product, operand2, discount_diff_operannd2, discount_diff_operator):
                        f=1
                        break
                else:
                    competition = operand2

            elif operand1 == 'discount_diff':

                if competition != None:
                    
                    if not check_discount_dif_and_competition(product, competition, operand2, operator):
                        f=1
                        break
                else:
                    discount_diff_operand1 = operand1
                    discount_diff_operannd2 = operand2
                    discount_diff_operator = operator

        if f==0: 
            product_count+=1
            discount_sum += discount
            print(product['brand']['name'])
            print(discount)
            
    return jsonify({"discounted_products_count": product_count, "avg_dicount": discount_sum/product_count}) 


def get_expencive_list(product_json, filters):
    #list will contain the required result
    result = []
    
    #iterating through all the products in json data
    for product in product_json:


        #initializing variables
        competition = None
        discount_diff_operand1 = None
        discount_diff_operannd2 = None
        discount_diff_operator = None

        #flag variable
        f=0

        #iterating through the filters
        for filter in filters:

            #getting filter parameters from each filter
            operand1 = filter['operand1']
            operator = filter['operator']
            operand2 = filter['operand2']

            #print(operand1)

            if operand1 == 'discount':
                
                if not check_discount(product, operator, operand2):
                    f=1
                    break

            elif operand1 == 'brand.name':

                if check_brand_name(product, operand2) == False:
                    f=1
                    break

            elif operand1 == 'competition':
                if discount_diff_operand1 != None:

                    if not check_discount_dif_and_competition(product, operand2, discount_diff_operannd2, discount_diff_operator):
                        f=1
                        break
                else:
                    competition = operand2

            elif operand1 == 'discount_diff':

                if competition != None:
                    
                    if not check_discount_dif_and_competition(product, competition, operand2, operator):
                        f=1
                        break
                else:
                    discount_diff_operand1 = operand1
                    discount_diff_operannd2 = operand2
                    discount_diff_operator = operator

        if f==0: 
            #result.append(product['_id'])
            basket_price = product['price']['basket_price']['value']
            
            f1 = 0
            for website_result in product['similar_products']['website_results']:
                for knn_item in  product['similar_products']['website_results'][website_result]['knn_items']:
                    similar_product_basket_price = knn_item['_source']['price']['basket_price']['value']

                    if basket_price > similar_product_basket_price:
                        result.append(product['_id'])
                        
                        f1 = 1
                        break
                if f1 == 1:
                    break

    return jsonify({'expensive_list' : result})

def get_competition_discount_diff_list(product_json, filters):
    #list will contain the required result
    result = []
    
    #iterating through all the products in json data
    for product in product_json:


        #initializing variables
        competition = None
        discount_diff_operand1 = None
        discount_diff_operannd2 = None
        discount_diff_operator = None

        #flag variable
        f=0

        #iterating through the filters
        for filter in filters:

            #getting filter parameters from each filter
            operand1 = filter['operand1']
            operator = filter['operator']
            operand2 = filter['operand2']

            #print(operand1)

            if operand1 == 'discount':
                
                if not check_discount(product, operator, operand2):
                    f=1
                    break

            elif operand1 == 'brand.name':

                if check_brand_name(product, operand2) == False:
                    f=1
                    break

            elif operand1 == 'competition':
                if discount_diff_operand1 != None:
                    # basket_price = product['price']['basket_price']['value']
            
                    # f=1
                    
                    # for knn_item in  product['similar_products']['website_results'][operand2]['knn_items']:
                    #     similar_product_basket_price = knn_item['_source']['price']['basket_price']['value']
                    #     discount_diff = abs(((basket_price - similar_product_basket_price)/basket_price)*100)
                        
                        
                    #     if discount_diff_operator == '>':
                    #         if discount_diff > int(discount_diff_operannd2):
                    #             f=0
                                
                    #             break

                    #     elif discount_diff_operator == '==':
                    #         if discount_diff == int(discount_diff_operannd2):
                    #             f=0
                    #             break
                        
                    #     else:
                    #         if discount_diff < int(discount_diff_operannd2):
                    #             f=0
                    #             break
                    if not check_discount_dif_and_competition(product, operand2, discount_diff_operannd2, discount_diff_operator):
                        f=1
                        break
                    
                else:
                    competition = operand2

            elif operand1 == 'discount_diff':

                if competition != None:
                    # basket_price = product['price']['basket_price']['value']
            
                    # f=1
                    
                    # for knn_item in  product['similar_products']['website_results'][competition]['knn_items']:
                    #     similar_product_basket_price = knn_item['_source']['price']['basket_price']['value']
                    #     discount_diff = ((basket_price - similar_product_basket_price)/basket_price)*100
                        
                        
                    #     if operator == '>':
                    #         if discount_diff > int(operand2):
                    #             f=0
                                
                    #             break

                    #     elif operator == '==':
                    #         if discount_diff == int(operand2):
                    #             f=0
                    #             break
                        
                    #     else:
                    #         if discount_diff < int(operand2):
                    #             f=0
                    #             break

                    if not check_discount_dif_and_competition(product, competition, operand2, operator):
                        f=1
                        break
                else:
                    discount_diff_operand1 = operand1
                    discount_diff_operannd2 = operand2
                    discount_diff_operator = operator

        if f==0: 
            result.append(product['_id'])
        
    return jsonify({'competition_discount_diff_list' : result}) 

