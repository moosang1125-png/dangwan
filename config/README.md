# Configuration template for Dangwan

# Google Sheets API Setup:
# 1. Go to https://console.cloud.google.com/
# 2. Create a new project or select existing one
# 3. Enable Google Sheets API
# 4. Create OAuth 2.0 credentials (Desktop application)
# 5. Download credentials and save as 'config/credentials.json'

# Directory Structure:
# config/
#   credentials.json  - Google API credentials (you need to provide this)
#   token.pickle      - Generated after first authentication
# cache/
#   *.json            - Cached PDF extraction results
#   document_context.json - Processing context for multi-part PDFs
