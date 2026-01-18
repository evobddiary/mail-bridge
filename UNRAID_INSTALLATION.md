# MailDocker UNRAID Installation Guide

## Prerequisites

1. **UNRAID Server** with Docker enabled
2. **Community Applications** plugin installed
3. **At least 2GB RAM** and **10GB storage** available

## Step 1: Enable Docker on UNRAID

1. Go to **Settings** → **Docker**
2. Enable Docker: **Yes**
3. Set Docker vDisk size (recommended: 20GB)
4. Click **Apply**
5. Wait for Docker to start

## Step 2: Install Community Applications

1. Go to **Apps** tab in UNRAID
2. If not installed, click **Install Community Applications**
3. Wait for plugin to install

## Step 3: Create AppData Directory

1. Open **Terminal** in UNRAID (or use SSH)
2. Create the MailDocker appdata directory:
```bash
mkdir -p /mnt/user/appdata/mail-bridge
mkdir -p /mnt/user/appdata/mail-bridge/config
mkdir -p /mnt/user/appdata/mail-bridge/maildata
mkdir -p /mnt/user/appdata/mail-bridge/logs
```

## Step 4: Copy Configuration Files

### Option A: Using UNRAID Shares (Recommended)

1. Copy the entire `docker` folder to your UNRAID server
2. Place it in `/mnt/user/appdata/mail-bridge/`
3. Your structure should look like:
```
/mnt/user/appdata/mail-bridge/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── entrypoint.sh
│   ├── build.sh
│   ├── config/
│   ├── scripts/
│   └── web/
├── config/          (for runtime config)
├── maildata/         (for email storage)
└── logs/            (for logs)
```

### Option B: Manual File Creation

1. Create the files directly in `/mnt/user/appdata/mail-bridge/`
2. Copy the contents from each file in the repository

## Step 5: Build Docker Image

1. Open **Terminal** in UNRAID
2. Navigate to the docker directory:
```bash
cd /mnt/user/appdata/mail-bridge/docker
```

3. Make the build script executable:
```bash
chmod +x build.sh
```

4. Build the Docker image:
```bash
./build.sh
```

## Step 6: Create Docker Container

### Method A: Using UNRAID Docker GUI (Recommended)

1. Go to **Docker** tab in UNRAID
2. Click **Add Container**
3. Fill in the configuration:

#### Basic Settings:
- **Name**: `mail-bridge`
- **Repository**: `mail-bridge:latest`
- **Network Type**: `bridge`

#### Repository URL:
- Click **Advanced View**
- **Repository**: `mail-bridge:latest`

#### Volume Mappings:
| Container Path | Host Path | Access Mode |
|---------------|-----------|-------------|
| `/config` | `/mnt/user/appdata/mail-bridge/config` | `RW` |
| `/maildata` | `/mnt/user/appdata/mail-bridge/maildata` | `RW` |
| `/logs` | `/mnt/user/appdata/mail-bridge/logs` | `RW` |
| `/scripts` | `/mnt/user/appdata/mail-bridge/docker/scripts` | `RO` |
| `/app/web` | `/mnt/user/appdata/mail-bridge/docker/web` | `RO` |

#### Port Mappings:
| Container Port | Host Port | Protocol |
|---------------|-----------|----------|
| `8787` | `8787` | `TCP` |
| `143` | `143` | `TCP` (optional) |
| `993` | `993` | `TCP` (optional) |

#### Environment Variables:
| Variable | Value | Description |
|----------|-------|-------------|
| `PERSONAL_POP_PASS` | `your_password` | Personal email password |
| `WORK_POP_PASS` | `your_work_password` | Work email password |
| `SECONDARY_POP_PASS` | `your_secondary_password` | Secondary email password |

#### Post Arguments:
```
/entrypoint.sh
```

#### Extra Parameters:
```
--memory=512m --cpu-shares=512
```

4. Click **Apply**
5. Wait for the container to start

### Method B: Using Docker Compose

1. Create a `docker-compose.override.yml` file:
```yaml
version: '3.8'
services:
  mail-bridge:
    image: mail-bridge:latest
    container_name: mail-bridge
    restart: unless-stopped
    
    environment:
      - PERSONAL_POP_PASS=${PERSONAL_POP_PASS}
      - WORK_POP_PASS=${WORK_POP_PASS}
      - SECONDARY_POP_PASS=${SECONDARY_POP_PASS}
    
    volumes:
      - /mnt/user/appdata/mail-bridge/config:/config
      - /mnt/user/appdata/mail-bridge/maildata:/maildata
      - /mnt/user/appdata/mail-bridge/logs:/logs
      - /mnt/user/appdata/mail-bridge/docker/scripts:/scripts:ro
      - /mnt/user/appdata/mail-bridge/docker/web:/app/web:ro
    
    ports:
      - "8787:8787"
      - "143:143"
      - "993:993"
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

2. Run in terminal:
```bash
cd /mnt/user/appdata/mail-bridge/docker
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## Step 7: Configure MailDocker

1. **Access Web Interface**:
   - Open browser: `http://your-unraid-ip:8787`
   - You should see the MailDocker dashboard

2. **Add Your First Account**:
   - Click **Accounts** tab
   - Click **Add New Account**
   - Fill in your POP3 details
   - Set environment variable name for password
   - Click **Add Account**

3. **Set Password Environment Variables**:
   - Go to **Docker** tab in UNRAID
   - Click on `mail-bridge` container
   - Click **Edit**
   - Add your actual passwords in **Environment Variables** section
   - Click **Apply**

4. **Test Connection**:
   - In the web interface, click **Test** next to your account
   - Verify connection works

## Step 8: Connect Email Client

1. **IMAP Server Settings**:
   - **Server**: Your UNRAID IP address
   - **Port**: 143 (IMAP) or 993 (IMAPS)
   - **Username**: The IMAP user you configured (e.g., `user1`)
   - **Password**: Any password (static authentication)

2. **Recommended Clients**:
   - **Thunderbird** (Desktop)
   - **iOS Mail** (iPhone/iPad)
   - **Android Email** (Android)

## Step 9: Set Up Filters

1. Go to **Filters** tab in web interface
2. Click **Add New Rule**
3. Create rules for:
   - Moving invoices to "Invoices" folder
   - Priority emails to "Priority" folder
   - Newsletters to "Archive" folder

## Step 10: Monitor and Maintain

1. **Check Status**:
   - Visit **Status** tab in web interface
   - Monitor service health
   - View recent logs

2. **Backup Configuration**:
   ```bash
   # Backup appdata regularly
   tar -czf mail-bridge-backup-$(date +%Y%m%d).tar.gz /mnt/user/appdata/mail-bridge
   ```

3. **Update Container**:
   - Rebuild image with new code
   - Stop and remove old container
   - Create new container with updated image

## Troubleshooting

### Container Won't Start
1. Check Docker logs: **Docker** tab → Click container → **Logs**
2. Verify all volume mappings exist
3. Check environment variables are set correctly

### Can't Access Web Interface
1. Verify port 8787 is not blocked by firewall
2. Check if container is running
3. Try accessing via `http://localhost:8787` from UNRAID itself

### POP3 Connection Fails
1. Verify POP3 server settings
2. Check if password environment variable is set
3. Test connection using **Test** button in web interface

### No Emails Received
1. Check fetchmail logs
2. Verify POP3 account has emails
3. Check if emails are being filtered to different folders

## Security Recommendations

1. **Use Strong Passwords** for email accounts
2. **Enable SSL/TLS** for all POP3 connections
3. **Regular Backups** of `/mnt/user/appdata/mail-bridge`
4. **Monitor Logs** for suspicious activity
5. **Update Regularly** with security patches

## Performance Tuning

1. **Memory**: Increase if processing many emails
2. **CPU**: Adjust shares based on system load
3. **Storage**: Use SSD for better performance
4. **Network**: Ensure stable connection to POP3 servers

## Support

1. **Check Logs** in web interface first
2. **UNRAID Forums** for Docker-specific issues
3. **GitHub Issues** for application bugs
4. **Documentation** in README.md

---

**Congratulations! 🎉** Your MailDocker system is now running on UNRAID!

You can now:
- Access the web interface at `http://your-unraid-ip:8787`
- Add multiple POP3 accounts
- Set up email filtering rules
- Connect your favorite email client
- Monitor system status and logs
