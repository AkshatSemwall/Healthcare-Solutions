from app import app
from datetime import datetime
from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)