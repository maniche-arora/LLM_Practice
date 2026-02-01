"""
Configuration file for Resume AI Agent
Set your OpenAI API key here or use environment variable OPENAI_API_KEY
"""

import os

# Set your OpenAI API key here
# Replace 'your-api-key-here' with your actual OpenAI API key
# Example: OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxx"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

# Alternative: Set it directly in this file (not recommended for security)
# Uncomment and set your key below:
# OPENAI_API_KEY = "your-actual-api-key-here"

# Set environment variable if not already set
if OPENAI_API_KEY and OPENAI_API_KEY != 'your-api-key-here':
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
