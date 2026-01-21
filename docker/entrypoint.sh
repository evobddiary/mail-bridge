#!/bin/sh
set -e

echo "=== mail-bridge starting ==="

# 0. Check Dovecot version
echo "Checking Dovecot version..."
dovecot --version 2>/dev/null || echo "dovecot command not available"
dpkg -l | grep dovecot | head -5

# 1. Generate fetchmail configuration from YAML
echo "Generating fetchmail configuration..."
python3 /scripts/generate_config.py

# 2. Проверка дали config файловете са налични
if [ ! -f /config/dovecot.conf ]; then
    echo "ERROR: /config/dovecot.conf not found"
    exit 1
fi

if [ ! -f /config/fetchmailrc ]; then
    echo "ERROR: /config/fetchmailrc not found"
    exit 1
fi

# 3. Create necessary mail directories
echo "Creating mail directories..."
mkdir -p /maildata/user1 /maildata/user2 /maildata/user3
mkdir -p /maildata/user1/INBOX /maildata/user1/Invoices /maildata/user1/Priority
mkdir -p /maildata/user2/INBOX /maildata/user2/Work /maildata/user2/Reports
mkdir -p /maildata/user3/INBOX /maildata/user3/Archive

# 4. Set proper permissions
chown -R 1000:1000 /maildata
chmod -R 755 /maildata

# 5. Стартиране на dovecot
echo "Starting dovecot..."
echo "Dovecot version information:"
dovecot --version 2>/dev/null || echo "dovecot command not available"
doveconf --version 2>/dev/null || echo "doveconf version check failed"
echo "Configuration file:"
cat /config/dovecot.conf

# Check if Dovecot is already running
if pgrep dovecot > /dev/null; then
    echo "Dovecot is already running, stopping it first..."
    pkill -9 dovecot 2>/dev/null || true
    sleep 2
fi

# Clean up any existing socket files
echo "Cleaning up socket files..."
rm -rf /var/run/dovecot/*
mkdir -p /var/run/dovecot

# Start Dovecot
echo "Starting Dovecot..."
dovecot -c /config/dovecot.conf

# Wait a moment and check if Dovecot started successfully
sleep 3
if pgrep dovecot > /dev/null; then
    echo "Dovecot started successfully"
else
    echo "Dovecot failed to start"
fi

# 6. Стартиране на web интерфейса (background)
echo "Starting web interface..."
cd /app/web
python3 app.py &
WEB_PID=$!

# 7. Стартиране на fetchmail (foreground!)
echo "Starting fetchmail..."
exec fetchmail -f /config/fetchmailrc --nodetach --verbose
