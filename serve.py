from waitress import serve
from app import app
import socket

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    host_ip = get_ip_address()
    port = 5000
    
    print(f"=== Production Server Started (Waitress) ===")
    print(f"Local:   http://localhost:{port}")
    print(f"Network: http://{host_ip}:{port}")
    print(f"============================================")
    
    serve(app, host='0.0.0.0', port=port)
