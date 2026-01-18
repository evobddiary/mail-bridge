#!/usr/bin/env python3
"""
Generate fetchmail configuration from accounts.yaml
"""

import yaml
import os
import sys
from pathlib import Path

def load_accounts_config(config_path="/config/accounts.yaml"):
    """Load accounts configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file {config_path} not found", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in {config_path}: {e}", file=sys.stderr)
        sys.exit(1)

def generate_fetchmailrc(config):
    """Generate fetchmailrc content from configuration"""
    lines = []
    
    # Global settings
    settings = config.get('settings', {})
    check_interval = settings.get('check_interval', 300)
    
    lines.extend([
        f"# Generated fetchmail configuration",
        f"# Check interval: {check_interval} seconds",
        f"set daemon {check_interval}",
        f"set syslog",
        f"set no bouncemail",
        f"set no spambounce",
        "",
    ])
    
    # Generate account configurations
    accounts = config.get('accounts', [])
    
    for account in accounts:
        name = account.get('name', 'unnamed')
        pop_server = account.get('pop_server')
        pop_port = account.get('pop_port', 995)
        user = account.get('user')
        password_env = account.get('password_env')
        ssl = account.get('ssl', True)
        keep = account.get('keep', True)
        imap_user = account.get('imap_user')
        
        if not all([pop_server, user, password_env, imap_user]):
            print(f"WARNING: Skipping incomplete account {name}", file=sys.stderr)
            continue
            
        lines.extend([
            f"# === {name.upper()} ACCOUNT ===",
            f"poll {pop_server} protocol POP3",
            f"  port {pop_port}",
            f'  user "{user}"',
            f'  password "${password_env}"',
        ])
        
        if ssl:
            lines.append("  ssl")
        
        if keep:
            lines.append("  keep")
        else:
            lines.append("  no keep")
            
        # Use Python script for mail delivery
        lines.append(f'  mda "/scripts/process_mail.py {imap_user}"')
        lines.append("")
    
    return '\n'.join(lines)

def main():
    """Main function"""
    config_path = "/config/accounts.yaml"
    output_path = "/config/fetchmailrc"
    
    # Load configuration
    config = load_accounts_config(config_path)
    
    # Generate fetchmailrc
    fetchmailrc_content = generate_fetchmailrc(config)
    
    # Write to output file
    try:
        with open(output_path, 'w') as f:
            f.write(fetchmailrc_content)
        
        # Set proper permissions (only readable by owner)
        os.chmod(output_path, 0o600)
        
        print(f"Generated {output_path} successfully")
        print(f"Configured {len(config.get('accounts', []))} accounts")
        
    except IOError as e:
        print(f"ERROR: Could not write {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
