from crud import Crud
from flask import jsonify


class RoutesHelper:
    @staticmethod
    def get_all_elements(table_name):
        handler = Crud(table_name)
        cols = handler.get_columns()
        elements_list = handler.get_all_elements()
        elements = []
        for element in elements_list:
            elements.append({cols[x]: element[x] for x in range(len(cols))})    
        return jsonify(data = elements)
    
    @staticmethod
    def insert_element(table_name, json_items):
        handler = Crud(table_name)
        cols = []
        values = []
        
        for col, value in json_items:
            if col == 'id' or col == 'updated_at':
                pass
            else:
                cols.append(col)
                values.append(value)
        print(cols)
        print(values)
        handler.insert(cols, values)
        return cols, values

    @staticmethod
    def update_element(table_name, json_items, id_value):
        handler = Crud(table_name)
        cols = []
        values = []

        for col, value in json_items:
            if col == 'updated_at' or col == 'id':
                pass
            else:
                cols.append(col)
                values.append(value)
    
        handler.update_element(id_value, cols, values, 'id')

    @staticmethod
    def remove_dicts_from_list(data):
        return [item for item in data if not isinstance(item, dict)]

    @staticmethod
    def get_prices(result):
        products_id = []
        for association in result:
            products_id.append(association.get('id_product'))
        prices_rows = []
        for product in products_id:
            handler = Crud('prices')
            prices = handler.get_elements_by_string_field('product_id', product)
            for row in prices:
                prices_rows.append({key:row[key] for key in row})
        for element in prices_rows:
            handler = Crud('supermarket')
            supermarket = handler.get_element_by_pk(element['supermarket_id'], 'id')
            element['supermarket_id'] = supermarket['name']
            
        most_recent_by_supermarket = {}

        for item in prices_rows:
            supermarket_id = item['supermarket_id']
            if supermarket_id in most_recent_by_supermarket:
                if item['updated_at'] > most_recent_by_supermarket[supermarket_id]['updated_at']:
                    most_recent_by_supermarket[supermarket_id] = item
            else:
                most_recent_by_supermarket[supermarket_id] = item
        most_recent_items = list(most_recent_by_supermarket.values())
        return most_recent_items