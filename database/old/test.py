print("Testing Python execution...")

try:
    import requests
    print("✓ requests module found")
except ImportError:
    print("✗ requests module not found - need to install")

try:
    import bs4
    print("✓ beautifulsoup4 module found")
except ImportError:
    print("✗ beautifulsoup4 module not found - need to install")

try:
    import pandas
    print("✓ pandas module found")
except ImportError:
    print("✗ pandas module not found - need to install")

print("Test completed!")
