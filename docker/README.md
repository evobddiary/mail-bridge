# MailDocker - POP3 to IMAP Bridge

A Docker-based email processing system that fetches emails from multiple POP3 accounts, applies custom filtering rules, and delivers them to a local IMAP server.

## Features

- ✅ **Multi-account support** - Configure multiple POP3 accounts
- ✅ **Advanced filtering** - Custom rules for email organization
- ✅ **Push notifications** - Webhook-based notifications for important emails
- ✅ **Docker containerized** - Easy deployment on UNRAID or any Docker host
- ✅ **Comprehensive logging** - Detailed logs for monitoring and debugging
- 🚧 **Web interface** - Configuration and monitoring (in development)
- 🚧 **Email import** - Import from Thunderbird and other clients (planned)

## Quick Start

### 1. Build the Docker Image

```bash
cd docker
chmod +x build.sh
./build.sh
```

### 2. Configure Your Accounts

Edit `config/accounts.yaml`:

```yaml
accounts:
  - name: "personal"
    pop_server: "pop.gmail.com"
    user: "your-email@gmail.com"
    password_env: "PERSONAL_POP_PASS"
    imap_user: "user1"
    ssl: true
    keep: true
```

### 3. Set Environment Variables

```bash
export PERSONAL_POP_PASS="your_actual_password"
export WORK_POP_PASS="your_work_password"
```

### 4. Run with Docker Compose

```bash
docker-compose up -d
```

### 5. Test Configuration

```bash
docker exec mail-bridge-test python3 /scripts/test_config.py
```

### 6. Access Web Interface

Open your browser and navigate to: `http://localhost:8787`

## Configuration

### accounts.yaml Structure

```yaml
accounts:
  - name: "account-name"
    pop_server: "pop.example.com"
    pop_port: 995
    user: "user@example.com"
    password_env: "ENV_VAR_NAME"
    ssl: true
    keep: true
    imap_user: "local_user"

filter_rules:
  - name: "rule-name"
    conditions:
      subject_contains: ["invoice", "receipt"]
      from_contains: ["important@domain.com"]
    action:
      folder: "Invoices"
      push_notify: true
      push_title: "Invoice Received"
```

### Environment Variables

- `PERSONAL_POP_PASS` - Password for personal account
- `WORK_POP_PASS` - Password for work account
- `SECONDARY_POP_PASS` - Password for secondary account

## UNRAID Installation

1. Add the repository URL in UNRAID Docker settings
2. Search for "mail-bridge" template
3. Configure:
   - **Config Path**: `/mnt/user/appdata/mail-bridge/config`
   - **Mail Data Path**: `/mnt/user/appdata/mail-bridge/maildata`
   - **Logs Path**: `/mnt/user/appdata/mail-bridge/logs`
   - Set your password environment variables
4. Start the container

## Email Client Setup

Connect your email client (Thunderbird, iOS Mail, Android) to:

- **Server**: Your UNRAID server IP
- **Port**: 143 (IMAP) or 993 (IMAPS)
- **Username**: The `imap_user` from your configuration
- **Password**: Any password (authentication is static in current setup)

**Web Interface:**
- **URL**: `http://your-server-ip:8787`
- **Features**: Account management, filter rules, system status

## File Structure

```
docker/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Development/testing setup
├── entrypoint.sh          # Container startup script
├── build.sh               # Build script
├── config/
│   ├── accounts.yaml      # Account configuration
│   ├── dovecot.conf       # IMAP server config
│   └── fetchmailrc        # Generated fetchmail config
├── scripts/
│   ├── process_mail.py    # Email processing logic
│   ├── generate_config.py # Config generator
│   └── test_config.py     # Configuration validator
└── unraid-template.xml    # UNRAID template
```

## Development

### Testing

```bash
# Test configuration
docker exec mail-bridge-test python3 /scripts/test_config.py

# View logs
docker logs mail-bridge-test

# Interactive shell for debugging
docker exec -it mail-bridge-test bash
```

### Building

```bash
./build.sh
```

### Monitoring

Logs are available in:
- Docker logs: `docker logs mail-bridge-test`
- File logs: `/logs/` directory
- Real-time processing: `/logs/process_mail.log`

## Roadmap

- [ ] **Phase 1**: Multi-account setup ✅
- [ ] **Phase 2**: IMAP client access
- [ ] **Phase 3**: Web interface for configuration
- [ ] **Phase 4**: Email import from Thunderbird
- [ ] **Phase 5**: Advanced features (ML filtering, integrations)

## Troubleshooting

### Common Issues

1. **Passwords not working**: Ensure environment variables are set correctly
2. **IMAP connection refused**: Check if dovecot is running and ports are mapped
3. **Emails not fetching**: Verify POP3 server settings and SSL configuration
4. **Configuration errors**: Run the test script to validate setup

### Debug Commands

```bash
# Check running processes
docker exec mail-bridge-test ps aux

# Test POP3 connection manually
docker exec mail-bridge-test fetchmail -v --nodetach

# Check mail directories
docker exec mail-bridge-test ls -la /maildata/
```

## Security Notes

- Passwords are stored as environment variables, not in configuration files
- SSL/TLS is used for POP3 connections by default
- IMAP authentication is currently static (will be enhanced in future versions)
- Regular backups of `/maildata` directory are recommended

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
