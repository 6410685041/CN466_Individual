import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

SECRET_KEY = os.environ['FLASK_SECRET_KEY']
app.config['SECRET_KEY'] = SECRET_KEY

from routes.line import line_blueprint
from routes.liff import liff_blueprint

app.register_blueprint(line_blueprint, url_prefix='/line')
app.register_blueprint(liff_blueprint, url_prefix='/liff')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')