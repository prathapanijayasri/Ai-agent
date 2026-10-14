from backend.app import create_app
from backend.app.config import Config

app = create_app()

if __name__ == "__main__":
    print(f"Starting MediBot AI on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
