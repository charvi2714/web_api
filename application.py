from flask import Flask

application = app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World! hi'

if __name__ == '__main__':
    app.run()
