# MailDocker - Quick Start Guide for UNRAID

## 🚀 One-Command Installation

### Prerequisites
- UNRAID server with Docker enabled
- Git installed (usually pre-installed on UNRAID)
- Internet connection

### Installation Steps

1. **SSH into your UNRAID server:**
```bash
ssh root@your-unraid-ip
```

2. **Clone the repository:**
```bash
cd /mnt/user/appdata
git clone https://github.com/evobddiary/mail-bridge.git
cd mail-bridge
```

3. **Run the deployment script:**
```bash
chmod +x deploy.sh
./deploy.sh
```

That's it! The script will:
- ✅ Pull latest changes
- ✅ Stop any existing container
- ✅ Build the Docker image
- ✅ Start the container
- ✅ Show you the web interface URL

## 🌐 Access Your MailDocker

After deployment completes, open your browser:
```
http://your-unraid-ip:8787
```

## 📋 Configuration

### 1. Add Your First POP3 Account

1. Click **Accounts** tab
2. Click **Add New Account**
3. Fill in:
   - **Name**: Personal Gmail (or any name)
   - **POP3 Server**: pop.gmail.com
   - **Port**: 995
   - **Email**: your-email@gmail.com
   - **Password Env Variable**: PERSONAL_POP_PASS
   - **IMAP User**: user1
   - **SSL**: Enabled
   - **Keep**: Enabled

4. Click **Add Account**

### 2. Set Password Environment Variable

**Option A: Via Docker (Recommended)**
```bash
docker stop mail-bridge
docker rm mail-bridge

# Then run deploy.sh with environment variables:
docker run -d \
    --name mail-bridge \
    --restart unless-stopped \
    -p 8787:8787 \
    -p 143:143 \
    -e PERSONAL_POP_PASS="your_actual_password" \
    -v /mnt/user/appdata/mail-bridge/docker/config:/config \
    -v /mnt/user/appdata/mail-bridge/docker/maildata:/maildata \
    -v /mnt/user/appdata/mail-bridge/docker/logs:/logs \
    -v /mnt/user/appdata/mail-bridge/docker/scripts:/scripts:ro \
    -v /mnt/user/appdata/mail-bridge/docker/web:/app/web:ro \
    mail-bridge:latest
```

**Option B: Edit accounts.yaml directly**
```bash
nano /mnt/user/appdata/mail-bridge/docker/config/accounts.yaml
# Add your accounts and passwords
```

### 3. Test Connection

In the web interface:
1. Go to **Accounts** tab
2. Click **Test** button next to your account
3. Verify connection works

## 📧 Connect Your Email Client

### IMAP Settings:
- **Server**: Your UNRAID IP address
- **Port**: 143 (or 993 for SSL)
- **Username**: user1 (or the IMAP user you configured)
- **Password**: Any password (authentication is static)

### Supported Clients:
- Thunderbird (Desktop)
- iOS Mail (iPhone/iPad)
- Android Email
- Outlook
- Any IMAP-compatible client

## 🔧 Common Commands

```bash
# View logs
docker logs mail-bridge

# View live logs
docker logs -f mail-bridge

# Restart container
docker restart mail-bridge

# Stop container
docker stop mail-bridge

# Update to latest version
cd /mnt/user/appdata/mail-bridge
./deploy.sh
```

## 🐛 Troubleshooting

### Container keeps restarting
```bash
# Check logs for errors
docker logs mail-bridge --tail 50

# Common issues:
# 1. Dovecot configuration error - Check /config/dovecot.conf
# 2. Missing directories - Run deploy.sh again
# 3. Port conflicts - Check if ports 8787, 143, 993 are available
```

### Can't access web interface
```bash
# Check if container is running
docker ps | grep mail-bridge

# Check if port is accessible
curl http://localhost:8787

# Check firewall settings on UNRAID
```

### Emails not being fetched
```bash
# Check fetchmail logs
docker logs mail-bridge | grep fetchmail

# Verify POP3 settings in web interface
# Test connection using the Test button
```

### Configuration errors
```bash
# View current configuration
cat /mnt/user/appdata/mail-bridge/docker/config/dovecot.conf

# Reset to default
cd /mnt/user/appdata/mail-bridge
git reset --hard HEAD
./deploy.sh
```

## 📁 File Structure

```
/mnt/user/appdata/mail-bridge/
├── deploy.sh              # Main deployment script
├── docker/
│   ├── Dockerfile         # Docker image definition
│   ├── entrypoint.sh      # Container startup script
│   ├── config/
│   │   ├── accounts.yaml  # Your POP3 accounts
│   │   ├── dovecot.conf   # IMAP server config
│   │   └── fetchmailrc    # Generated fetchmail config
│   ├── maildata/          # Email storage (Maildir format)
│   ├── logs/              # Application logs
│   ├── scripts/           # Python processing scripts
│   └── web/               # Web interface files
```

## 🔒 Security Notes

- Passwords are stored as environment variables, not in config files
- SSL/TLS is used for POP3 connections by default
- Regular backups of `/mnt/user/appdata/mail-bridge` are recommended
- Keep the system updated with `./deploy.sh`

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs first:**
   ```bash
   docker logs mail-bridge --tail 100
   ```

2. **Verify configuration:**
   ```bash
   docker exec mail-bridge cat /config/dovecot.conf
   ```

3. **Test manually:**
   ```bash
   docker exec -it mail-bridge bash
   # Then test components individually
   ```

4. **Report issues:**
   - GitHub: https://github.com/evobddiary/mail-bridge/issues
   - Include logs and configuration (remove passwords!)

## 🎉 Success!

Your MailDocker system is now running! You can:
- ✅ Fetch emails from multiple POP3 accounts
- ✅ Access them via IMAP on any device
- ✅ Manage accounts via web interface
- ✅ Set up email filtering rules
- ✅ Receive push notifications (coming soon)

Enjoy your self-hosted email system! 📧
