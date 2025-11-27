print("Python is working")
import sys
print(sys.version)
try:
    import flask
    print("Flask is installed")
except ImportError:
    print("Flask is NOT installed")
