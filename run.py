from app import create_app
from dotenv import load_dotenv
import os

app = create_app()
load_dotenv()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)