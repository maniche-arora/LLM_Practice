"""
Configuration file for Resume AI Agent
Set your OpenAI API key via environment variable OPENAI_API_KEY

DEPLOYMENT GUIDE:
- Local: Set environment variable OPENAI_API_KEY before running
- AWS: Use Secrets Manager or Parameter Store
- Google Cloud: Use Secret Manager
- Azure: Use Key Vault
- Heroku: Use Config Vars
"""

import os
import sys

# Get API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Validate that API key is set
if not OPENAI_API_KEY or OPENAI_API_KEY == 'your-api-key-here':
    print("\n" + "="*60)
    print("ERROR: OPENAI_API_KEY environment variable not set!")
    print("="*60)
    print("\nHow to set it:")
    print("  Windows CMD: set OPENAI_API_KEY=your-key-here")
    print("  Windows PowerShell: $env:OPENAI_API_KEY='your-key-here'")
    print("  Linux/Mac: export OPENAI_API_KEY='your-key-here'")
    print("\nFor Cloud Deployment:")
    print("  AWS: Use Secrets Manager or Parameter Store")
    print("  Google Cloud: Use Secret Manager")
    print("  Azure: Use Key Vault")
    print("  Heroku: Use Config Vars")
    print("="*60 + "\n")
    
    # Only raise error in production/cloud environments
    if os.getenv('ENVIRONMENT') == 'production':
        raise ValueError("OPENAI_API_KEY environment variable is required for cloud deployment")

# Ensure it's available in environment
if OPENAI_API_KEY:
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
