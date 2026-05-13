# Google Indexing API Configuration

# Sitemap URL
SITEMAP_URL = "https://example.com/sitemap.xml"

# Service Account JSON file path
SERVICE_ACCOUNT_PATH = "service_account.json"

# Pending URLs file
PENDING_FILE = "pending_urls.txt"

# API Endpoints
ENDPOINT_PUBLISH = "https://indexing.googleapis.com/v3/urlNotifications:publish"
ENDPOINT_METADATA = "https://indexing.googleapis.com/v3/urlNotifications/metadata"

# API Scopes
SCOPES = ["https://www.googleapis.com/auth/indexing"]

# Rate limiting
DAILY_LIMIT = 150  # Daily URL submission limit default is 200, but using 150 to be safe and account for any retries
REQUESTS_PER_MINUTE = 20  # API rate limit: requests per minute default is 60 but using 20 to be safe and account for any retries
WAIT_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE  # Automatic wait between requests (1 second)
