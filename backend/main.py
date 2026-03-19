import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Zeabur requires the app to listen on the PORT environment variable
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
