'''

from app import app

@app.route('/gabor', methods=["GET"])
def index():
    return 'Hello World!'

'''