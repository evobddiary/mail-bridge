# MailDocker UNRAID Installation - GitHub Methods

Since your code is on GitHub, you can install MailDocker on UNRAID much more easily using these methods:

## Method 1: Community Applications (Easiest)

### Step 1: Add Repository to CA
1. Go to **Apps** → **Community Applications**
2. Click **Settings** (gear icon)
3. Add this repository URL:
   ```
   https://github.com/your-username/MailDocker
   ```
4. Click **Add**
5. Wait for the repository to be indexed

### Step 2: Install from CA
1. Search for "MailDocker" in Community Applications
2. Click **Install**
3. Configure:
   - Set your email passwords as environment variables
   - Adjust port if needed (default: 8787)
   - Set storage paths
4. Click **Apply**

## Method 2: Docker Hub + CA Template

### Step 1: Build and Push to Docker Hub
```bash
# Build the image
docker build -t your-username/mail-bridge:latest .

# Push to Docker Hub
docker push your-username/mail-bridge:latest
```

### Step 2: Create CA Template
Create `template.xml` in your GitHub repository:

```xml
<?xml version="1.0"?>
<Container version="2">
  <Name>mail-bridge</Name>
  <Repository>your-username/mail-bridge</Repository>
  <Registry>https://hub.docker.com/r/your-username/mail-bridge</Registry>
  <Network>bridge</Network>
  <Privileged>false</Privileged>
  
  <Support>https://github.com/your-username/MailDocker/issues</Support>
  <Project>https://github.com/your-username/MailDocker</Project>
  <Overview>MailDocker - POP3 to IMAP bridge with web interface</Overview>
  <Category>Productivity:Mail:</Category>
  
  <Config Name="Config Path" Target="/config" Default="/mnt/user/appdata/mail-bridge/config" Mode="rw" Type="Path" Display="always" Required="true" />
  <Config Name="Mail Data Path" Target="/maildata" Default="/mnt/user/appdata/mail-bridge/maildata" Mode="rw" Type="Path" Display="always" Required="true" />
  <Config Name="Logs Path" Target="/logs" Default="/mnt/user/appdata/mail-bridge/logs" Mode="rw" Type="Path" Display="always" Required="true" />
  
  <Config Name="Personal POP Password" Target="PERSONAL_POP_PASS" Default="" Mode="" Type="Variable" Display="always" Required="false" />
  <Config Name="Work POP Password" Target="WORK_POP_PASS" Default="" Mode="" Type="Variable" Display="always" Required="false" />
  <Config Name="Secondary POP Password" Target="SECONDARY_POP_PASS" Default="" Mode="" Type="Variable" Display="always" Required="false" />
  
  <Config Name="Web Port" Target="8787" Default="8787" Mode="tcp" Type="Port" Display="always" Required="true" />
  
  <PostArgs>/entrypoint.sh</PostArgs>
  <ExtraParams>--memory=512m --cpu-shares=512</ExtraParams>
</Container>
```

### Step 3: Install from CA
1. The template will appear in Community Applications
2. Click **Install** and configure
3. Set your passwords and paths
4. Click **Apply**

## Method 3: GitHub Container Registry

### Step 1: Use GitHub Actions to Build
Create `.github/workflows/docker.yml`:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v3
      with:
        context: ./docker
        push: true
        tags: |
          ghcr.io/${{ github.repository }}:latest
          ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### Step 2: Update Template to Use GHCR
```xml
<Repository>ghcr.io/your-username/mail-bridge</Repository>
<Registry>https://github.com/your-username/MailDocker/pkgs/container/mail-bridge</Registry>
```

## Method 4: One-Click Install Script

### Step 1: Create Install Script
Create `install.sh` in your GitHub repository:

```bash
#!/bin/bash

# MailDocker UNRAID One-Click Install Script
REPO="your-username/MailDocker"
APPDATA="/mnt/user/appdata/mail-bridge"

echo "Installing MailDocker on UNRAID..."

# Create directories
mkdir -p "$APPDATA"/{config,maildata,logs}

# Download and extract
cd /tmp
wget https://github.com/$REPO/archive/main.zip
unzip main.zip
cp -r MailDocker-main/docker/* "$APPDATA/"

# Build image
cd "$APPDATA"
docker build -t mail-bridge:latest .

# Create container
docker run -d \
  --name mail-bridge \
  --restart unless-stopped \
  -p 8787:8787 \
  -v "$APPDATA/config:/config" \
  -v "$APPDATA/maildata:/maildata" \
  -v "$APPDATA/logs:/logs" \
  mail-bridge:latest

echo "MailDocker installed! Access at http://$(hostname -I | cut -d' ' -f1):8787"
```

### Step 2: Run Install Script
```bash
# In UNRAID terminal
curl -sSL https://raw.githubusercontent.com/your-username/MailDocker/main/install.sh | bash
```

## Method 5: Docker Compose from GitHub

### Step 1: Create docker-compose.yml
Create `docker-compose.unraid.yml`:

```yaml
version: '3.8'
services:
  mail-bridge:
    image: ghcr.io/your-username/mail-bridge:latest
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
    
    ports:
      - "8787:8787"
      - "143:143"
      - "993:993"
    
    extra_params:
      - "--memory=512m"
      - "--cpu-shares=512"
```

### Step 2: One-Command Deploy
```bash
# In UNRAID terminal
curl -sSL https://raw.githubusercontent.com/your-username/MailDocker/main/docker-compose.unraid.yml > docker-compose.yml
docker-compose up -d
```

## Method 6: Unraid Plugin (Advanced)

### Step 1: Create Plugin Structure
```
MailDocker.plg
├── plugin/
│   ├── install.sh
│   ├── remove.sh
│   └── files/
│       ├── icon.png
│       └── template.xml
└── plugins/
```

### Step 2: Plugin Install Script
```bash
#!/bin/bash

# MailDocker UNRAID Plugin Installer
echo "Installing MailDocker plugin..."

# Create directories
mkdir -p /usr/local/emhttp/plugins/MailDocker

# Download files
wget -O /usr/local/emhttp/plugins/MailDocker/MailDocker.plg \
  https://github.com/your-username/MailDocker/raw/main/MailDocker.plg

# Install plugin
/usr/local/emhttp/plugins/dynamix.docker.manager/include/DockerMan.php --install MailDocker

echo "Plugin installed! Check your Docker tab."
```

## Recommended Approach: Method 2 (Docker Hub + CA)

This is the most user-friendly approach:

1. **Push to Docker Hub** once
2. **Create CA template** once  
3. **Users install with one click** from Community Applications
4. **Automatic updates** when you push new versions

### Quick Setup for Method 2:

```bash
# One-time setup
docker build -t your-username/mail-bridge:latest ./docker
docker push your-username/mail-bridge:latest

# Add template.xml to your GitHub repo
# Users can now install from CA with one click!
```

## Benefits of GitHub-Based Installation:

✅ **No manual file copying**  
✅ **Automatic updates**  
✅ **Version control**  
✅ **Easy distribution**  
✅ **Professional appearance**  
✅ **Community visibility**  

## Next Steps:

1. Choose your preferred method
2. Set up the infrastructure (Docker Hub/GHCR)
3. Create the template/plugin files
4. Test the installation process
5. Share with the UNRAID community!

The **Docker Hub + Community Applications** method is highly recommended for the best user experience.
