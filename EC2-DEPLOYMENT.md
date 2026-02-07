# AWS EC2 Ubuntu Deployment Guide

## Prerequisites Checklist

- [ ] Ubuntu EC2 instance created
- [ ] Security Group allows SSH (port 22) - for you
- [ ] Security Group allows HTTP (port 8501) - for application
- [ ] .pem key file downloaded locally
- [ ] Your EC2 Public IP address
- [ ] OpenAI API key

---

## Phase 1: Prepare Your Local Machine

### For Windows (PowerShell):

```powershell
# 1. Navigate to where your .pem file is located
cd "C:\path\to\your\keys"

# 2. Change key permissions (important for security)
icacls "your-key.pem" /reset
icacls "your-key.pem" /grant "$($env:USERNAME):(F)"
icacls "your-key.pem" /inheritance:r

# 3. Test SSH connection (replace IP)
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP

# If successful, you'll see:
# ubuntu@ip-xxx-xxx-xxx-xxx:~$
```

### For Mac/Linux:

```bash
# 1. Navigate to key location
cd ~/.ssh

# 2. Change key permissions
chmod 400 your-key.pem

# 3. Test connection
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## Phase 2: Configure AWS Security Group

**Important:** Make sure your Security Group allows incoming traffic on port 8501

### Steps:

1. Go to AWS Console → EC2 → Security Groups
2. Find your EC2 instance's Security Group
3. Click "Edit inbound rules"
4. Add these rules:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP or 0.0.0.0/0 | SSH Access |
| Custom TCP | TCP | 8501 | 0.0.0.0/0 | Streamlit App |

5. Save rules

---

## Phase 3: Connect to EC2 and Deploy

### Terminal/PowerShell Commands:

```bash
# 1. SSH into EC2
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP

# 2. Update system (run on EC2)
sudo apt update && sudo apt upgrade -y

# 3. Install Docker and Git
sudo apt install -y docker.io docker-compose git

# 4. Add ubuntu user to docker group (so no sudo needed)
sudo usermod -aG docker ubuntu
newgrp docker

# 5. Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# 6. Clone your repository
cd /home/ubuntu
git clone https://github.com/maniche-arora/LLM_Practice.git
cd LLM_Practice

# 7. Create .env file with your API key
# Option A: Using echo (simple)
echo "OPENAI_API_KEY=your-actual-api-key-here" > .env

# Option B: Using nano editor (safer, review before saving)
nano .env
# Add this line:
# OPENAI_API_KEY=your-actual-api-key-here
# Press Ctrl+X, then Y, then Enter to save

# 8. Build and run with Docker Compose
docker-compose up --build -d

# 9. Check if container is running
docker ps

# 10. View logs
docker-compose logs -f

# 11. Find your public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

---

## Phase 4: Access Your Application

Once deployment is complete:

1. Get your EC2 Public IP:
   ```bash
   # Run this on EC2:
   curl http://169.254.169.254/latest/meta-data/public-ipv4
   ```

2. Open browser and go to:
   ```
   http://YOUR_EC2_PUBLIC_IP:8501
   ```

3. You should see your Resume AI Agent!

---

## Phase 5: Verify Application is Working

```bash
# Check container status
docker ps

# View application logs
docker-compose logs

# Test connectivity to Streamlit
curl http://localhost:8501
```

---

## Common Issues & Solutions

### Issue 1: Permission Denied for Docker

**Error:** `permission denied while trying to connect to Docker daemon`

**Solution:**
```bash
sudo usermod -aG docker ubuntu
# Log out and log back in, or:
newgrp docker
```

### Issue 2: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8501
sudo lsof -i :8501

# Kill it
sudo kill -9 <PID>

# Or change Streamlit port in docker-compose.yml
```

### Issue 3: Cannot Connect to Application

**Checklist:**
- [ ] Security Group allows port 8501
- [ ] Container is running: `docker ps`
- [ ] Logs show no errors: `docker-compose logs`
- [ ] Public IP is correct
- [ ] Try: `curl http://localhost:8501` (from EC2)

### Issue 4: API Key Not Working

**Solution:**
```bash
# Verify .env file has correct key
cat .env

# Restart container
docker-compose restart

# Check logs for errors
docker-compose logs app
```

---

## Useful Docker Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app

# Stop application
docker-compose down

# Restart application
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# Remove containers and volumes
docker-compose down -v

# SSH into running container
docker exec -it resume-analyzer bash

# Check resource usage
docker stats
```

---

## Making Application Persistent (Auto-restart)

The `docker-compose.yml` file already has restart policy. If you want manual systemd service:

```bash
# Create systemd service file
sudo nano /etc/systemd/system/resume-analyzer.service
```

Add this content:
```ini
[Unit]
Description=Resume AI Agent
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/LLM_Practice
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable resume-analyzer.service
sudo systemctl start resume-analyzer.service
```

---

## Setting Up Domain Name (Optional)

If you want a custom domain instead of IP:

1. Buy domain (GoDaddy, Namecheap, etc.)
2. Get your EC2 Elastic IP (AWS Console)
3. Update domain DNS to point to Elastic IP
4. Set up SSL with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --standalone -d yourdomain.com
```

---

## Monitoring & Maintenance

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Monitor logs in real-time
docker-compose logs -f

# Update Docker images
docker pull resume-analyzer:latest

# Clean up unused Docker resources
docker system prune -a
```

---

## Costs & Optimization

- **EC2 t2.micro:** Free tier eligible (1 year)
- **Monthly cost (t2.small):** ~$7-10
- **To reduce costs:**
  - Use t2.micro (free tier)
  - Stop instance when not in use
  - Use AWS Savings Plans

---

## Next Steps

1. ✓ Deploy application
2. Test with sample resumes
3. Monitor performance: `docker stats`
4. Set up monitoring/alerts
5. Consider CDN for faster access (CloudFront)
6. Set up backups of FAISS indexes

---

## Support Commands Cheatsheet

```bash
# SSH back into EC2
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP

# View current status
docker ps

# View recent logs
docker-compose logs --tail 50

# Restart app
docker-compose restart

# Full deployment from scratch
docker-compose down -v && docker-compose up --build -d

# Get new public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

---

## Troubleshooting Checklist

If app not accessible:

1. SSH to EC2: Can you connect?
2. Run `docker ps`: Is container running?
3. Run `docker-compose logs`: Any errors?
4. Check Security Group: Port 8501 allowed?
5. Test locally: `curl http://localhost:8501` (on EC2)
6. Check API key: `cat .env`
7. Check EC2 CPU/Memory: `free -h` and `top`

---

## Questions?

If you encounter any issues during deployment, run:
```bash
# Gather diagnostic info
echo "=== System Info ===" && uname -a
echo "=== Docker Version ===" && docker --version
echo "=== Running Containers ===" && docker ps
echo "=== Recent Logs ===" && docker-compose logs --tail 20
echo "=== Disk Space ===" && df -h
echo "=== Memory ===" && free -h
```

Share this output for debugging.
