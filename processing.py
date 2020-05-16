import json
from flask import request, jsonify

# this class contains functions for working on data and providing the correct response
class Process:

    #constructor
    def __init__(self, product_json, query_type , filters):
        
        self.product_json = product_json
        self.query_type = query_type
        self.filters = filters

    #function for checking if discount follows the filter condition
    def check_discount(self, product, operator, discount_value):

        """This function is used for applying the discount filter on the products
        It calculates the discount on the product based on the formula [100*(difference of regular_price and offer_price)/ regular_price].
        after calculating the discount it compares the it with the discount_value parameter based on the operator parameter and returns true or false accordingly."""

        #calculating discount
        discount = 100*((product['price']['regular_price']['value'] - product['price']['offer_price']['value'])/product['price']['regular_price']['value'])

        #comparing discount to discount_value value based on the operator
        if operator == '>':
            if discount > int(discount_value):
                return True          
            else:
                return False
                
        elif operator == '==':
            if discount == int(discount_value):
                return True
            else:
                return False

        else:
            if discount < int(discount_value):
                return True
            else:
                return False

    #function for checking if the product brand follows the filter brand
    def check_brand_name(self, product, brand):

        """This function used for applying the brand.name filter.
        it compares the brand name of the product with the parameter brand.if they are equal, it returns true else false."""


        if product['brand']['name'] == brand:
            return True
        else:
            return False

    #function for checking if the product follows the cometition and discount diff filter
    def check_discount_dif_and_competition(self, product, competition, discount_diff_operand2 , discount_diff_operator):

        """This function is used to apply competition and discount_dif filter on the product.first it extracts the basket price of the product.
        Then it goes through all the similar products of the given competiton, Extracts basket price of each similar product,
        Calculates discount diff based on formula : ((basket_price - similar_product_basket_price)/((basket_price + similar_product_basket_price)/2))*100
        Then it checks if the discount diff is >,==,<  dis count_dif_operand2 based on the operator.
         the condition is true for even one on the similar products it return true.
        If none of the similar products is satisfies the condition it returns false."""

        
        discount_diff = 0
        similar_product_basket_price = 0
        #extracting basket_price
        basket_price = product['price']['basket_price']['value']

        #flag variable        
        f=1
        
        #traversing through all the similar products of the given competition
        for knn_item in  product['similar_products']['website_results'][competition]['knn_items']:
            
            similar_product_basket_price = knn_item['_source']['price']['basket_price']['value']

            #calculating discount difference
            discount_diff = ((basket_price - similar_product_basket_price)/((basket_price + similar_product_basket_price)/2))*100
                
            #comparing calculated discount_diff with discount diff operand2 value present in the filter based on the operator 
            if discount_diff_operator == '>':
                if discount_diff > int(discount_diff_operand2):
                    return True           

            elif discount_diff_operator == '==':
                if discount_diff == int(discount_diff_operand2):
                    return True           
            
            else:
                if discount_diff < int(discount_diff_operand2):
                    return True

        
        #if filter does not get satisfied for all the products false is returned
        return False
                
    def check_filters(self, product):
        
        #initializing variables
        #as competition and discount diff self.filters are applied together, we need to get both of them from request before applying them.there is no particular
        #order for filter i.e either competition filter or discount_diff filter can be fetched first.
        #so we store the one that is fetched first and use it when both are available.
        competition = None
        discount_diff_operand1 = None
        discount_diff_operannd2 = None
        discount_diff_operator = None


        #iterating through the self.filters
        for filter in self.filters:

            #getting filter parameters from each filter
            operand1 = filter['operand1']
            operator = filter['operator']
            operand2 = filter['operand2']

            #print(operand1)

            if operand1 == 'discount':
                
                #calling self.check_discount function to check that discount follows the filter 
                if not self.check_discount(product, operator , operand2):
                    return False

            elif operand1 == 'brand.name':

                #checking brand name
                if self.check_brand_name(product, operand2) == False:
                    return False

            elif operand1 == 'competition':

                # if we have already fetched the discount_dif filter
                if discount_diff_operand1 != None:

                    if not self.check_discount_dif_and_competition(product, operand2, discount_diff_operannd2, discount_diff_operator):
                        return False

                # if we have not fetched the discount_dif filter
                else:
                    competition = operand2
                    

            elif operand1 == 'discount_diff':

                # if we have already fetched the competition filter
                if competition != None:

                    if not self.check_discount_dif_and_competition(product, competition, operand2, operator):
                        return False
                        
                # if we have not fetched the competition filter
                else:
                    discount_diff_operand1 = operand1
                    discount_diff_operannd2 = operand2
                    discount_diff_operator = operator
        
        return True


    def get_discouted_products_list(self):

        """This function is used when the query_type is discounted_products_list
        It traverses through all the products in the data.For each products it applies all the filters in the requests using  the above functions.
        If a product passes all the filters its id is added to a list named result.
        Then the result list is returned in json format."""

        #list will contain the required result
        result = []
        
        #iterating through all the products in json data
        for product in self.product_json:
            
            if self.check_filters(product):
                result.append(product['_id']['$oid'])
                print(100*((product['price']['regular_price']['value'] - product['price']['offer_price']['value'])/product['price']['regular_price']['value']))
                print(product['brand']['name'])                         

        return jsonify({'discounted_products_list' : result}) 

    def get_discounted_products_count_and_avg_discount(self):

        """A variable products_count is used as a counter to count the products that satisfy all the filters.
        Another variable discount sum is used to store the sum  of discounts of all the producs that follow the filters
        It traverses through all the products in the data.
        For each product it calculates discount and applies all the filters in the requests using  the above functions.
        If a product passes all the filters the product_count counter is increased by one and the discount is added to the variable discount_sum.
        After all the products have been traversed the product count and average discount is returned in json format."""

        #list will contain the required result
        result = []

        #initializing variables
        product_count = 0
        discount_sum = 0
        
        #iterating through all the products in json data
        for product in self.product_json:
            
            #calculating discount
            discount = 100*((product['price']['regular_price']['value'] - product['price']['offer_price']['value'])/product['price']['regular_price']['value'])
            
            #if the product follows all the self.filters
            if self.check_filters(product):
                
                product_count+=1
                discount_sum += discount
                print(product['brand']['name'])
                print(discount)      
        print({"discounted_products_count": product_count, "avg_dicount": (discount_sum/product_count if product_count != 0 else discount_sum)})
        return jsonify({"discounted_products_count": product_count, "avg_dicount": (discount_sum/product_count if product_count != 0 else discount_sum)}) 


    def get_expencive_list(self):

        """This function is used when the query_type is expencive_list.
        It traverses through all the products in the data.
        For each product it applies all the filters.
        If the product passes all the filters then it checks if its basket price is greater than any of its competitions.
        if it is so the product id is added to the result list."""


        #list will contain the required result
        result = []
        
        #iterating through all the products in json data
        for product in self.product_json:

            if self.check_filters(product):
                #extract basket price of the product
                basket_price = product['price']['basket_price']['value']
                
                #flag variable
                f1 = 0

                #fetching the basket price of all the similar products, comparing them with the basket price of the product.if anyone of the similar products 
                #have the basket price as defined in the filter product id gets added to the result list
                for website_result in product['similar_products']['website_results']:
                    for knn_item in  product['similar_products']['website_results'][website_result]['knn_items']:
                        similar_product_basket_price = knn_item['_source']['price']['basket_price']['value']

                        if basket_price > similar_product_basket_price:
                            result.append(product['_id']['$oid'])
                            print(str(similar_product_basket_price) + "\t" + str(basket_price) )
                            f1 = 1
                            break
                    if f1 == 1:
                        break

        return jsonify({'expensive_list' : result})

    def get_competition_discount_diff_list(self):

        """This function is used when the query_type is competiton_discount_diff_list.
        It traverses through all the products in the data.
        For each product it applies all the filters.
        If the product passes all the filters then its product id is added to the result list.
        Then the result list is returned in json format."""


        #list will contain the required result
        result = []
        
        #iterating through all the products in json data
        for product in self.product_json:

            #if all the filters are followed by the product
            if self.check_filters(product):
                result.append(product['_id']['$oid'])        
            
        return jsonify({'competition_discount_diff_list' : result}) 

