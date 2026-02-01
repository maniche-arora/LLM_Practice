# Cloud Deployment Guide for Resume AI Agent

## Overview
This guide explains how to deploy the Resume AI Agent to various cloud platforms while securely managing your OpenAI API key.

---

## **Option 1: Heroku (Easiest)**

### Prerequisites:
- Heroku account (https://www.heroku.com)
- Heroku CLI installed

### Steps:

1. **Install Heroku CLI:**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku app:**
   ```bash
   cd "c:\MyGitRepo\Projects\Resume AI agent"
   heroku create your-app-name
   ```

4. **Set Environment Variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your-actual-api-key-here
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **View logs:**
   ```bash
   heroku logs --tail
   ```

---

## **Option 2: Google Cloud Run (Recommended)**

### Prerequisites:
- Google Cloud account
- Google Cloud CLI installed

### Steps:

1. **Install Google Cloud CLI:**
   ```bash
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Create Secret in Secret Manager:**
   ```bash
   echo -n "your-actual-api-key-here" | gcloud secrets create openai-api-key --data-file=-
   ```

4. **Deploy:**
   ```bash
   gcloud run deploy resume-analyzer `
     --source . `
     --platform managed `
     --region us-central1 `
     --allow-unauthenticated `
     --set-env-vars OPENAI_API_KEY=projects/PROJECT_ID/secrets/openai-api-key/versions/latest
   ```

---

## **Option 3: AWS (EC2/ECS)**

### For AWS Secrets Manager:

1. **Create secret in AWS Console:**
   - Go to Secrets Manager
   - Create new secret
   - Name: `openai-api-key`
   - Value: your-actual-api-key-here

2. **Deploy with EC2:**
   ```bash
   # Launch EC2 instance
   # Install Docker
   # Create .env file with OPENAI_API_KEY
   # Run: docker-compose up
   ```

3. **Deploy with ECS:**
   - Use task definition with environment variables
   - Reference secrets from Secrets Manager

---

## **Option 4: Azure App Service**

### Steps:

1. **Create Azure App Service:**
   ```bash
   # Using Azure CLI
   az appservice plan create --name MyPlan --resource-group MyGroup --sku B1
   az webapp create --resource-group MyGroup --plan MyPlan --name resume-analyzer --runtime "PYTHON|3.12"
   ```

2. **Add API Key to Key Vault:**
   - Go to Azure Key Vault
   - Add secret: `openai-api-key`

3. **Configure Environment Variable:**
   ```bash
   az webapp config appsettings set --resource-group MyGroup --name resume-analyzer --settings OPENAI_API_KEY=your-key
   ```

4. **Deploy:**
   ```bash
   # Using Git deployment or GitHub Actions
   git push azure main
   ```

---

## **Option 5: Docker (Any Cloud Provider)**

### Build and Run Locally:

```bash
# Build image
docker build -t resume-analyzer:latest .

# Run with environment variable
docker run -e OPENAI_API_KEY=your-key -p 8501:8501 resume-analyzer:latest
```

### Deploy to Docker Hub:

```bash
# Tag image
docker tag resume-analyzer:latest YOUR_DOCKER_USERNAME/resume-analyzer:latest

# Push to Docker Hub
docker login
docker push YOUR_DOCKER_USERNAME/resume-analyzer:latest
```

---

## **Best Security Practices:**

### ✅ DO:
- Use cloud platform secret managers (Secrets Manager, Key Vault, etc.)
- Set API key as environment variable in deployment platform
- Use HTTPS/SSL for all connections
- Never commit API keys to GitHub
- Regenerate API keys periodically
- Use separate API keys for different environments (dev, staging, prod)
- Implement rate limiting and monitoring

### ❌ DON'T:
- Store API keys in code or config files
- Commit `.env` files to Git
- Use the same API key for development and production
- Share API keys via email or chat
- Hardcode credentials in Docker images

---

## **Environment Variables Setup by Platform:**

| Platform | Method | Command |
|----------|--------|---------|
| Heroku | Config Vars | `heroku config:set OPENAI_API_KEY=...` |
| Google Cloud | Cloud Run | Via Cloud Console or `--set-env-vars` |
| AWS | Lambda | Via Environment Variables in console |
| Azure | App Service | Via Application settings |
| Docker | Environment | `docker run -e OPENAI_API_KEY=...` |
| Local | PowerShell | `$env:OPENAI_API_KEY='...'` |
| Local | Windows CMD | `set OPENAI_API_KEY=...` |
| Local | Linux/Mac | `export OPENAI_API_KEY='...'` |

---

## **Streamlit Specific Configuration:**

Create `~/.streamlit/config.toml` for production:

```toml
[client]
showErrorDetails = false

[server]
headless = true
port = 8501
enableXsrfProtection = true

[logger]
level = "error"
```

---

## **Monitoring & Logging:**

Add application logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

---

## **Cost Optimization:**

- Use cloud credits (free tier)
- Set up auto-scaling
- Use spot instances (AWS) or preemptible VMs (Google Cloud)
- Monitor API usage to avoid unexpected charges

---

## **Questions?**

For more help, check:
- Heroku: https://devcenter.heroku.com/
- Google Cloud: https://cloud.google.com/docs
- AWS: https://docs.aws.amazon.com/
- Azure: https://docs.microsoft.com/azure/
