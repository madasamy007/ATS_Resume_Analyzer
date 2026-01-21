"""Test DNS resolution for SMTP server"""
import socket
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    print("Testing DNS resolution for smtp.gmail.com...")
    ip = socket.gethostbyname('smtp.gmail.com')
    print(f"SUCCESS: DNS resolution successful: smtp.gmail.com -> {ip}")
except socket.gaierror as e:
    print(f"FAILED: DNS resolution failed: {e}")
    print("\nPossible causes:")
    print("1. No internet connection")
    print("2. DNS server issues")
    print("3. Firewall blocking DNS")
    print("4. Proxy/VPN interference")
except Exception as e:
    print(f"ERROR: {e}")

