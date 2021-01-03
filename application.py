from flask import Flask, jsonify, request, Response
import json
import pymysql as mysql
from flask_cors import CORS
from werkzeug.utils import secure_filename
import itertools
import os
import uuid
import boto3
from botocore.client import Config
import flask

application = app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)
# ACCESS_KEY_ID = "AKIA5B7QKZSSL3ENLXG5"
# ACCESS_SECRET_KEY = "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"

host_url = 'testdb.cfhyep7ezte5.ap-south-1.rds.amazonaws.com'
db_name = 'roshana_db'
user = 'sunny'
password = 'pranay1999'


def db_connection(url, databaseName, username, password):
    connection = mysql.connect(host=url,
                               database=databaseName,
                               user=username,
                               password=password)
    return connection


@app.route('/get/products')
def get_products():
    product_list = {}
    connection_obj = db_connection(host_url, db_name, user, password)
    cursor = connection_obj.cursor()
    sql = "select productData.productId, productData.categoryId, productData.productPrice, productData.productName, productData.productDescription, GROUP_CONCAT( productImages.URL ) as 'URLS' \
           from productData \
           inner join  productImages on (productData.productId = productImages.productId) \
           group by productData.productId;"
    # sql = "select * from product;"
    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)
    cursor.close()
    connection_obj.close()

    for i in result:
        if i[1] in product_list:
            product_list[i[1]].append(
                {'product_id': i[0], 'price': i[2], 'name': i[3], 'description': i[4], 'imageurls': i[5].split(',')})
        else:
            product_list[i[1]] = [
                {'product_id': i[0], 'price': i[2], 'name': i[3], 'description': i[4], 'imageurls': i[5].split(',')}]

    return product_list


@app.route('/get/category')
def get_category():
    category_list = {}
    connection_obj = db_connection(host_url, db_name, user, password)
    cursor = connection_obj.cursor()
    sql = "SELECT * FROM categories"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    connection_obj.close()
    print(result)
    for i in result:
        category_list[i[0]] = i[1]
    print(category_list)
    return category_list


@app.route('/get/product', methods=['GET', 'POST'])
def get_product():
    content = request.json
    connection_obj = db_connection(host_url, db_name, user, password)
    cursor = connection_obj.cursor()
    sql = """select productData.productId, productData.categoryId, productData.productPrice, productData.productName, productData.productDescription, GROUP_CONCAT( productImages.URL ) as 'URLS' \
            from productData \
            inner join  productImages on (productData.productId = productImages.productId) \
            where productData.productId = (%s) \
            group by productData.productId;"""
    value = (content['productId'],)
    cursor.execute(sql, value)
    result = cursor.fetchall()
    cursor.close()
    connection_obj.close()
    # print(result)
    product_details = {}
    for i in result:
        product_details = {'product_id': i[0], 'category_id': i[1], 'productName': i[3], 'productPrice': i[2],
                           'productDescription': i[4], 'URLS': i[5].split(',')}
    print(product_details)
    connection_obj = db_connection(host_url, db_name, user, password)
    cursor = connection_obj.cursor()
    sql = """select group_concat(productImages.URL) as URLS from productImages where productImages.productId = (%s);"""
    value = (content['productId'],)
    cursor.execute(sql, value)
    result = cursor.fetchall()
    cursor.close()
    connection_obj.close()
    product_images = []
    test1 = {}
    for i in result[0][0].split(','):
        product_images.append({'image': i, 'thumbImage': i})
    for i in result[0][0].split(','):
        product_images.append({'image': i, 'thumbImage': i})
    product_details['urls'] = product_images
    return product_details


@app.route('/get/cartlist', methods=['GET', 'POST'])
def getCartList():
    content = request.json
    print(content['cartlist'])
    product_id_list = []
    size_list = []
    for i in content['cartlist']:
        product_id_list.append(i[:len(i) - 3])
        size_list.append(i[-3:])
    print(product_id_list)
    print(size_list)
    size_list = [size.replace('_', '').capitalize() for size in size_list]
    connection_obj = db_connection(host_url, db_name, user, password)
    cursor = connection_obj.cursor()
    if len(product_id_list) == 1:
        sql = """select productData.productId, productData.categoryId, productData.productPrice, productData.productName, productData.productDescription, GROUP_CONCAT( productImages.URL ) as 'URLS'
            from productData
            inner join  productImages on (productData.productId = productImages.productId)
            where productData.productId = {}
            group by productData.productId;""".format(product_id_list[0])
    else:
        sql = """select productData.productId, productData.categoryId, productData.productPrice, productData.productName, productData.productDescription, GROUP_CONCAT( productImages.URL ) as 'URLS'
        from productData
        inner join  productImages on (productData.productId = productImages.productId)
        where productData.productId in {}
        group by productData.productId;""".format(tuple(product_id_list))
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    connection_obj.close()
    print(result)
    total = 0
    response = {}
    for i in range(len(product_id_list)):
        for j in result:
            if int(product_id_list[i]) == j[0]:
                product_id = j[0]
                price = j[2]
                product_name = j[3]
                product_image = j[5].split(',')[0]
                if 'cart' in response:
                    response['cart'].append({'ProductSize':size_list[i], 'productId': product_id, 'productPrice': price, 'productName': product_name, 'productImage': product_image})
                else:
                    response['cart'] = [{'ProductSize':size_list[i], 'productId': product_id, 'productPrice': price, 'productName': product_name, 'productImage': product_image}]
                total += j[2]
    response['sub_total'] = total
    response['total'] = total + 40
    print(response)
    print('total', total)
    return response


@app.route('/test')
def test():
    connection_obj = db_connection(host_url, db_name, user, password)
    cursor = connection_obj.cursor()
    value = ['1', '3', '4']
    sql = """select productData.productId, productData.categoryId, productData.productPrice, productData.productName, productData.productDescription, GROUP_CONCAT( productImages.URL ) as 'URLS'
from productData
inner join  productImages on (productData.productId = productImages.productId)
where productData.productId in {}
group by productData.productId;""".format(tuple(value))
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    connection_obj.close()
    print(result)
    return "check"


@app.route('/')
def hello():
    x = {'updated_file': 1}
    return jsonify(x)


if __name__ == '__main__':
    app.run()
