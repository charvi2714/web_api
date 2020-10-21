from flask import Flask, jsonify, request, Response
import json
from flask_cors import CORS
from werkzeug.utils import secure_filename
import itertools
import os
import uuid
import boto3
from botocore.client import Config
import flask

application = app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def hello_world():
    x = {'userId': 1}
    return jsonify(x)


if __name__ == '__main__':
    app.run()
