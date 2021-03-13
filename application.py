from flask import Flask, jsonify, request, Response, render_template, flash, redirect, url_for
import json
from werkzeug.utils import secure_filename
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
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
UPLOAD_FOLDER = '.'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
                    response['cart'].append(
                        {'ProductSize': size_list[i], 'productId': product_id, 'productPrice': price,
                         'productName': product_name, 'productImage': product_image})
                else:
                    response['cart'] = [{'ProductSize': size_list[i], 'productId': product_id, 'productPrice': price,
                                         'productName': product_name, 'productImage': product_image}]
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


# Internal website server code starts here !!!!!

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


@app.route('/test/html')
def test_html():
    return render_template("index.html", last_updated=dir_last_updated('./static'))


@app.route('/no/one/is/allowed/here/add/product', methods=['POST', 'GET'])
def add_product():
    if flask.request.method == 'GET':
        connection_obj = db_connection(host_url, db_name, user, password)
        cursor = connection_obj.cursor()
        sql = "SELECT * FROM categories;"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        connection_obj.close()
        return render_template("addProduct.html", last_updated=dir_last_updated('./static'), category=result,
                               len=len(result))
    else:
        productName = request.form.get('productName')
        price = request.form.get('price')
        productCategory = request.form.get('productCategory')
        productDescription = request.form.get('productDescription')
        connection_obj = db_connection(host_url, db_name, user, password)
        cursor = connection_obj.cursor()
        sql = "insert into productData (categoryId, productName, productDescription, productPrice) values (%s, %s, %s, %s);"
        value = (productCategory, productName, productDescription, price)
        cursor.execute(sql, value)
        connection_obj.commit()
        files = flask.request.files.getlist("images")
        ACCESS_KEY_ID = 'AKIAIQXZ3KXIV32JCYZA'
        ACCESS_SECRET_KEY = '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'
        BUCKET_NAME = 'anhsor'
        sql = "select productId from productData where productId = (select max(productId) from productData);"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

        print(files)

        for file in files:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            ext = file.filename.split(".")
            ext = ext[::-1]
            print(ext)

            FILE_NAME = path
            data = open(FILE_NAME, 'rb')

            # FILE_NAME = str(uuid.uuid4()) + "." + ext[1]
            FILE_NAME = str(uuid.uuid4()) + str(result[0][0]) + "." + ext[0]
            # print(FILE_NAME)
            content_type = request.mimetype
            s3.Bucket(BUCKET_NAME).put_object(Key=FILE_NAME, Body=data, ACL='public-read')
            data.close()
            sql = "insert into productImages (productId, URL) values (%s, %s);"
            url = "https://anhsor.s3.us-east-2.amazonaws.com/" + FILE_NAME
            value = (result[0][0], url)
            cursor.execute(sql, value)
            connection_obj.commit()
            os.remove(path)
            print('done')
        cursor.close()
        connection_obj.close()
        flash('product Added')
        return redirect(url_for('test_html'))


@app.route('/no/one/is/allowed/here/view/products', methods=['POST', 'GET'])
def viewproducts():
    connection_obj = db_connection(host_url, db_name, user, password)
    cursor = connection_obj.cursor()
    sql = "select productData.productId, productData.categoryId, productData.productPrice, productData.productName, productData.productDescription, GROUP_CONCAT( productImages.URL ) as 'URLS', categories.categoryName   \
               from productData \
               inner join  productImages on (productData.productId = productImages.productId) \
               inner join categories on (productData.categoryId = categories.categoryId)\
               group by productData.productId;"
    cursor.execute(sql)
    result = cursor.fetchall()
    images = []
    for i in result:
        temp = i[5].split(',')
        images.append(temp[0])
    return render_template('viewProducts.html', last_updated=dir_last_updated('./static'), result=result, len=len(result), images=images)


@app.route('/somanytesting', methods=['POST', 'GET'])
def somanytesting():
    x = {'updated_file': 2}
    return jsonify(x)


@app.route('/')
def hello():
    x = {'updated_file': 1}
    return jsonify(x)


if __name__ == '__main__':
    app.run()
