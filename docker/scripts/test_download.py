#!/usr/bin/env python3
"""
MailDocker Test Mode Script
Download only last N emails for testing
"""

import os
import sys
import yaml
import poplib
import email
from pathlib import Path

def download_last_n_emails(account, n=10):
    """Download only last N emails from POP3 account"""
    try:
        pop_server = account.get('pop_server')
        pop_port = account.get('pop_port', 995)
        user = account.get('user')
        password = account.get('password')
        ssl = account.get('ssl', True)
        imap_user = account.get('imap_user')
        
        if ssl:
            pop = poplib.POP3_SSL(pop_server, pop_port)
        else:
            pop = poplib.POP3(pop_server, pop_port)
        
        pop.user(user)
        pop.pass_(password)
        
        # Get total message count
        total_messages = pop.stat()[0]
        print(f"📧 Total messages on server: {total_messages}")
        
        # Download only last N messages
        start_msg = max(1, total_messages - n + 1)
        print(f"📥 Downloading messages {start_msg} to {total_messages} (last {n} emails)")
        
        maildir_path = Path(f"/maildata/{imap_user}/Maildir")
        maildir_path.mkdir(parents=True, exist_ok=True)
        (maildir_path / "cur").mkdir(exist_ok=True)
        (maildir_path / "new").mkdir(exist_ok=True)
        (maildir_path / "tmp").mkdir(exist_ok=True)
        
        downloaded = 0
        for msg_num in range(start_msg, total_messages + 1):
            try:
                # Retrieve message
                raw_msg = b"\n".join(pop.retr(msg_num)[1])
                msg = email.message_from_bytes(raw_msg)
                
                # Generate filename
                import time
                import hashlib
                timestamp = str(int(time.time()))
                content_hash = hashlib.md5(raw_msg).hexdigest()[:8]
                filename = f"{timestamp}.{content_hash}:2,S"
                
                # Save to new directory
                target_file = maildir_path / "new" / filename
                with open(target_file, 'wb') as f:
                    f.write(raw_msg)
                
                downloaded += 1
                subject = msg.get('subject', 'No subject')
                print(f"✅ Downloaded {downloaded}/{n}: {subject[:50]}...")
                
            except Exception as e:
                print(f"❌ Error downloading message {msg_num}: {e}")
        
        pop.quit()
        print(f"🎉 Successfully downloaded {downloaded} emails to {maildir_path}")
        return downloaded
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 test_download.py <account_name> <number_of_emails>")
        sys.exit(1)
    
    account_name = sys.argv[1]
    n = int(sys.argv[2])
    
    # Load config
    config_path = Path("/config/accounts.yaml")
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Find account
    account = None
    for acc in config.get('accounts', []):
        if acc.get('name') == account_name:
            account = acc
            break
    
    if not account:
        print(f"❌ Account '{account_name}' not found")
        sys.exit(1)
    
    print(f"🧪 Test mode: Downloading last {n} emails from {account_name}")
    download_last_n_emails(account, n)

if __name__ == '__main__':
    main()
