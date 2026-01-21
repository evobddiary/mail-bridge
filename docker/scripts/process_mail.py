#!/usr/bin/env python3

import sys
import email
import subprocess
import yaml
import os
import logging
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/logs/process_mail.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MailProcessor:
    def __init__(self, config_path="/config/accounts.yaml"):
        self.config = self.load_config(config_path)
        self.filter_rules = self.config.get('filter_rules', [])
        self.push_settings = self.config.get('settings', {}).get('push_notifications', {})
        
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def send_push_notification(self, title, body, source="mail-bridge"):
        """Send push notification via webhook"""
        if not self.push_settings.get('enabled', False):
            return
            
        webhook_url = self.push_settings.get('webhook_url')
        if not webhook_url:
            logger.warning("Push notification enabled but no webhook URL configured")
            return
            
        try:
            timeout = self.push_settings.get('timeout', 5)
            response = requests.post(
                webhook_url,
                json={
                    "title": title,
                    "body": body,
                    "source": source,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=timeout
            )
            logger.info(f"Push notification sent: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
    
    def apply_filter_rules(self, msg):
        """Apply filtering rules to determine folder and actions"""
        subject = (msg.get("Subject") or "").lower()
        from_addr = (msg.get("From") or "").lower()
        body = ""
        
        # Extract body text for content filtering
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore').lower()
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore').lower()
            except:
                pass
        
        # Default folder and settings
        folder = "INBOX"
        mark_as = None
        push_notify = False
        push_title = "New Email"
        push_body = msg.get("Subject", "(no subject)")
        
        # Apply each rule
        for rule in self.filter_rules:
            rule_name = rule.get('name', 'unnamed')
            conditions = rule.get('conditions', {})
            action = rule.get('action', {})
            
            # Check if conditions match
            matches = True
            
            # Subject conditions
            if 'subject_contains' in conditions:
                subject_terms = conditions['subject_contains']
                if isinstance(subject_terms, str):
                    subject_terms = [subject_terms]
                if not any(term.lower() in subject for term in subject_terms):
                    matches = False
            
            # From conditions
            if 'from_contains' in conditions:
                from_terms = conditions['from_contains']
                if isinstance(from_terms, str):
                    from_terms = [from_terms]
                if not any(term.lower() in from_addr for term in from_terms):
                    matches = False
            
            # Body conditions
            if 'body_contains' in conditions:
                body_terms = conditions['body_contains']
                if isinstance(body_terms, str):
                    body_terms = [body_terms]
                if not any(term.lower() in body for term in body_terms):
                    matches = False
            
            # If rule matches, apply action
            if matches:
                logger.info(f"Filter rule '{rule_name}' matched")
                
                if 'folder' in action:
                    folder = action['folder']
                
                if 'mark_as' in action:
                    mark_as = action['mark_as']
                
                if 'push_notify' in action:
                    push_notify = action['push_notify']
                
                if 'push_title' in action:
                    push_title = action['push_title']
                
                # Break after first matching rule (can be changed for multiple rules)
                break
        
        return folder, mark_as, push_notify, push_title, push_body

def main():
    # Get IMAP user from command line argument
    if len(sys.argv) < 2:
        logger.error("Missing IMAP user argument")
        sys.exit(1)
    
    imap_user = sys.argv[1]
    
    # Read raw email from stdin
    try:
        raw_message = sys.stdin.read()
        msg = email.message_from_string(raw_message)
    except Exception as e:
        logger.error(f"Failed to parse email: {e}")
        sys.exit(1)
    
    # Initialize processor
    processor = MailProcessor()
    
    # Apply filtering rules
    folder, mark_as, push_notify, push_title, push_body = processor.apply_filter_rules(msg)
    
    logger.info(f"Processing email for {imap_user} -> folder: {folder}")
    
    # Add custom headers if needed
    if mark_as:
        msg["X-Marked-As"] = mark_as
    
    msg["X-Processed-By"] = "mail-bridge"
    msg["X-Processed-At"] = datetime.now().isoformat()
    
    # Send push notification if needed
    if push_notify:
        processor.send_push_notification(push_title, push_body)
    
    # Deliver to dovecot
    try:
        proc = subprocess.Popen(
            [
                "dovecot-lda",
                "-d", imap_user,
                "-m", folder
            ],
            stdin=subprocess.PIPE
        )
        proc.communicate(msg.as_bytes())
        
        if proc.returncode == 0:
            logger.info(f"Successfully delivered to {folder}")
        else:
            logger.error(f"Delivery failed with code {proc.returncode}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error delivering mail: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
