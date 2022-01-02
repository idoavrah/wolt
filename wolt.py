from flask import Flask, request, abort
import logging 
from reporting import *

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)-24s %(filename)-20s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()


@app.route('/api/report', methods=['POST'])
def compute():
    try:
        content = request.json
        orders = parseOrdersFromRequest(content)
        guid = generateReport(orders)
    except Exception as e:
        logging.error(e)
        abort(400)
    
    return {"guid": guid}, 200

if __name__ == "__main__":
    app.run(debug=True)
