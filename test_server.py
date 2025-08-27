import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint response:")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_list_docs_endpoint():
    """Test the list documents endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/list-docs")
        print("List docs endpoint response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing list-docs endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Testing FastAPI server...")
    print("=" * 50)
    
    # Test root endpoint
    if test_root_endpoint():
        print(" Root endpoint working!")
    else:
        print(" Root endpoint failed!")
    
    print("\n" + "=" * 50)
    
    # Test list docs endpoint
    if test_list_docs_endpoint():
        print(" List docs endpoint working!")
    else:
        print(" List docs endpoint failed!")
    
    print("\n" + "=" * 50)
    print("Server is running! You can access:")
    print("- API Documentation: http://127.0.0.1:8000/docs")
    print("- Alternative Docs: http://127.0.0.1:8000/redoc")
    print("- Root endpoint: http://127.0.0.1:8000/")
