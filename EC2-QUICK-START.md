# AWS EC2 Deployment - Quick Start Checklist

## Pre-Deployment (5 minutes)

### Local Machine Setup
- [ ] Download `.pem` key file
- [ ] Save to safe location (e.g., `C:\AWS_Keys\`)
- [ ] Note the file permissions are restricted
- [ ] Open Terminal/PowerShell

### AWS Console Preparation
- [ ] Note your EC2 Instance **Public IP Address**
- [ ] Go to Security Groups
- [ ] Add inbound rule for port **8501** (TCP, anywhere `0.0.0.0/0`)
- [ ] Add inbound rule for port **22** (SSH, your IP or anywhere)
- [ ] Click "Apply Rules"

### Prepare API Key
- [ ] Have your **OpenAI API Key** ready
- [ ] (Already regenerated the exposed one? If not, do it now)

---

## Deployment (10 minutes)

### Step 1: Connect to EC2 (2 minutes)

**Windows PowerShell:**
```powershell
ssh -i "C:\AWS_Keys\your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

**Mac/Linux:**
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

✅ You should see: `ubuntu@ip-xxx-xxx-xxx-xxx:~$`

---

### Step 2: Install Docker (3 minutes)

Copy-paste this entire block:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git
sudo usermod -aG docker ubuntu
sudo systemctl start docker
sudo systemctl enable docker
```

✅ No errors should appear

---

### Step 3: Clone & Deploy (3 minutes)

Copy-paste this entire block:

```bash
cd /home/ubuntu
git clone https://github.com/maniche-arora/LLM_Practice.git
cd LLM_Practice
echo "OPENAI_API_KEY=YOUR-API-KEY-HERE" > .env
docker-compose up --build -d
```

**⚠️ IMPORTANT:** Replace `YOUR-API-KEY-HERE` with your actual OpenAI API key

✅ Last line should show: "Docker Compose is now in the stopping phase"

---

### Step 4: Verify Deployment (2 minutes)

```bash
docker ps
```

✅ Should show `resume-analyzer` container running

```bash
docker-compose logs
```

✅ Should end with `Streamlit app running on...`

---

## Access Your Application

Get your public IP:
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

Then visit in browser:
```
http://YOUR_EC2_PUBLIC_IP:8501
```

✅ You should see the Resume AI Agent interface!

---

## Troubleshooting Quick Fixes

### App not loading?
```bash
# Check if container is running
docker ps

# View errors
docker-compose logs -f

# Restart
docker-compose restart
```

### Permission denied?
```bash
newgrp docker
docker ps
```

### Port 8501 not accessible?
- AWS Console → Security Groups → Inbound Rules
- Add: Custom TCP, Port 8501, Source 0.0.0.0/0

### API key not working?
```bash
# Check .env file
cat .env

# Restart
docker-compose restart

# Check logs
docker-compose logs
```

---

## Useful Commands Reference

```bash
# View logs (live)
docker-compose logs -f

# Stop app
docker-compose down

# Restart app
docker-compose restart

# Rebuild (if you made changes)
docker-compose up --build -d

# SSH into container (advanced)
docker exec -it resume-analyzer bash

# Get EC2 IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Check container stats
docker stats

# View recent 20 logs
docker-compose logs --tail 20
```

---

## Cost Information

| Instance Type | Monthly Cost | Suitable For |
|---------------|-------------|-------------|
| t2.micro (free tier) | $0/month (1 year) | Development/Demo |
| t2.small | ~$7/month | Light production |
| t2.medium | ~$14/month | Regular production |

Free tier includes: 750 hours/month of t2.micro

---

## Security Reminders

✅ Do:
- [ ] Keep `.env` file secure (never share)
- [ ] Use EC2 Security Groups to restrict access
- [ ] Regularly check application logs
- [ ] Update system: `sudo apt update && sudo apt upgrade`

❌ Don't:
- [ ] Never push `.env` to GitHub
- [ ] Don't open port 8501 to world if sensitive
- [ ] Don't share `.pem` key file
- [ ] Don't hardcode API key in code

---

## Next: Manual Step-by-Step?

**Tell me:**
1. Your EC2 Instance **Public IP**
2. You're using a **Linux/Mac/Windows** machine
3. You have the **`.pem` key file** ready

Then I'll guide you through EACH command one by one with explanations!

---

## Still Issues? Run This Diagnostic

```bash
uname -a
docker --version
docker ps
docker-compose logs --tail 30
free -h
df -h
```

Share the output if you need help!
