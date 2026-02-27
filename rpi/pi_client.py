from rpi_bridge import app
from config import PI_ID, RPI_BRIDGE_HOST, RPI_BRIDGE_PORT

if __name__ == "__main__":
    print(f"Starting Pi bridge for {PI_ID} on http://{RPI_BRIDGE_HOST}:{RPI_BRIDGE_PORT}")
    print("Endpoints: GET /health, GET /challenge")
    app.run(host=RPI_BRIDGE_HOST, port=RPI_BRIDGE_PORT, debug=False)
