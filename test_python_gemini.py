from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_vertex_ai_auth():
    """Test authentication with Vertex AI."""
    try:
        # Path to the service account JSON file
        credentials_path = "G:\My Drive\EOC Sindh\Data Cleaning and Analysis App\gen-lang-client-0716792542-144ca618dfbb.json"
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(credentials_path)

        # Initialize Vertex AI client
        client = build("aiplatform", "v1", credentials=credentials)

        print("Vertex AI API client initialized successfully!")
    except Exception as e:
        print(f"Error initializing Vertex AI API client: {e}")

test_vertex_ai_auth()
