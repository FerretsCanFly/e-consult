"""Development configuration that can be imported at startup."""

import os

# Development mode
os.environ['DEVELOPMENT'] = 'true'

# MongoDB Configuration
os.environ['MONGODB_URI'] = 'mongodb://localhost:27017'  # Local MongoDB instance
os.environ['MONGODB_DATABASE'] = 'econsult'  # Your database name
os.environ['MONGODB_COLLECTION'] = 'documents'  # Your collection name
os.environ['MONGODB_SEARCH_INDEX'] = 'default'  # Your search index name

# Azure OpenAI Configuration (replace with your values)
os.environ['AZURE_ENDPOINT'] = 'https://your-endpoint.openai.azure.com/'
os.environ['AZURE_MODEL_NAME'] = 'gpt-35-turbo'  # or your model name
os.environ['AZURE_DEPLOYMENT'] = 'your-deployment-name'
os.environ['AZURE_API_KEY'] = 'your-api-key'
os.environ['AZURE_API_VERSION'] = '2023-05-15'

# Vector Search Configuration
os.environ['VECTOR_SEARCH_NUM_CANDIDATES'] = '150'
os.environ['VECTOR_SEARCH_LIMIT'] = '10'

