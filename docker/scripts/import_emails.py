#!/usr/bin/env python3
"""
MailDocker Email Import Script
Import emails from .eml or .mbox files into Dovecot maildirs
"""

import os
import sys
import email
import mailbox
import shutil
from pathlib import Path
import argparse

def import_eml_file(eml_file, target_maildir, imap_user):
    """Import a single .eml file into Dovecot maildir"""
    try:
        with open(eml_file, 'r', encoding='utf-8') as f:
            msg = email.message_from_file(f)
        
        # Generate unique filename
        import time
        import hashlib
        timestamp = str(int(time.time()))
        content_hash = hashlib.md5(msg.as_bytes().encode()).hexdigest()[:8]
        filename = f"{timestamp}.{content_hash}:2,S"
        
        # Deliver to cur directory (new messages)
        cur_dir = Path(target_maildir) / imap_user / "Maildir" / "cur"
        cur_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = cur_dir / filename
        with open(target_file, 'wb') as f:
            f.write(msg.as_bytes().encode())
        
        print(f"✅ Imported: {eml_file} -> {target_file}")
        return True
    except Exception as e:
        print(f"❌ Error importing {eml_file}: {e}")
        return False

def import_mbox_file(mbox_file, target_maildir, imap_user):
    """Import emails from .mbox file into Dovecot maildir"""
    try:
        mbox = mailbox.mbox(mbox_file)
        imported = 0
        
        for message in mbox:
            # Generate unique filename
            import time
            import hashlib
            timestamp = str(int(time.time()))
            content_hash = hashlib.md5(message.as_bytes().encode()).hexdigest()[:8]
            filename = f"{timestamp}.{content_hash}:2,S"
            
            # Deliver to cur directory
            cur_dir = Path(target_maildir) / imap_user / "Maildir" / "cur"
            cur_dir.mkdir(parents=True, exist_ok=True)
            
            target_file = cur_dir / filename
            with open(target_file, 'wb') as f:
                f.write(message.as_bytes().encode())
            
            imported += 1
            if imported % 100 == 0:
                print(f"📧 Imported {imported} messages...")
        
        print(f"✅ Successfully imported {imported} messages from {mbox_file}")
        return True
    except Exception as e:
        print(f"❌ Error importing {mbox_file}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Import emails into MailDocker')
    parser.add_argument('source', help='Source file or directory')
    parser.add_argument('--user', required=True, help='IMAP user (e.g., user1)')
    parser.add_argument('--maildir', default='/maildata', help='MailDocker maildir path')
    
    args = parser.parse_args()
    
    source = Path(args.source)
    maildir = Path(args.maildir)
    imap_user = args.user
    
    print(f"📧 Importing emails for user: {imap_user}")
    print(f"📁 Target maildir: {maildir}")
    print(f"📂 Source: {source}")
    
    if source.is_file():
        if source.suffix.lower() == '.mbox':
            import_mbox_file(source, maildir, imap_user)
        elif source.suffix.lower() == '.eml':
            import_eml_file(source, maildir, imap_user)
        else:
            print(f"❌ Unsupported file format: {source.suffix}")
    elif source.is_dir():
        # Import all .eml files in directory
        imported = 0
        for eml_file in source.glob('*.eml'):
            if import_eml_file(eml_file, maildir, imap_user):
                imported += 1
        print(f"✅ Successfully imported {imported} .eml files")
    else:
        print(f"❌ Source not found: {source}")

if __name__ == '__main__':
    main()
