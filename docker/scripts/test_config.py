#!/usr/bin/env python3
"""
Test script to validate accounts.yaml configuration
"""

import yaml
import os
import sys

def test_config():
    """Test the accounts configuration"""
    config_path = "/config/accounts.yaml"
    
    print("=== Testing MailDocker Configuration ===")
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    try:
        # Load and parse YAML
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ Configuration file loaded successfully")
        
        # Check required sections
        if 'accounts' not in config:
            print("❌ No 'accounts' section found")
            return False
        
        accounts = config['accounts']
        print(f"✅ Found {len(accounts)} account(s)")
        
        # Validate each account
        for i, account in enumerate(accounts, 1):
            print(f"\n--- Account {i}: {account.get('name', 'unnamed')} ---")
            
            required_fields = ['pop_server', 'user', 'password_env', 'imap_user']
            missing_fields = [field for field in required_fields if not account.get(field)]
            
            if missing_fields:
                print(f"❌ Missing required fields: {', '.join(missing_fields)}")
                return False
            
            # Check environment variables
            password_env = account.get('password_env')
            if password_env not in os.environ:
                print(f"⚠️  Environment variable {password_env} not set")
            else:
                print(f"✅ Environment variable {password_env} is set")
            
            print(f"✅ POP3 Server: {account['pop_server']}:{account.get('pop_port', 995)}")
            print(f"✅ User: {account['user']}")
            print(f"✅ IMAP User: {account['imap_user']}")
            print(f"✅ SSL: {account.get('ssl', True)}")
            print(f"✅ Keep: {account.get('keep', True)}")
        
        # Check filter rules
        if 'filter_rules' in config:
            rules = config['filter_rules']
            print(f"\n✅ Found {len(rules)} filter rule(s)")
            
            for i, rule in enumerate(rules, 1):
                print(f"--- Rule {i}: {rule.get('name', 'unnamed')} ---")
                if 'conditions' in rule and 'action' in rule:
                    print("✅ Rule has conditions and actions")
                else:
                    print("❌ Rule missing conditions or actions")
                    return False
        
        # Test fetchmail generation
        print(f"\n--- Testing fetchmail generation ---")
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "/scripts/generate_config.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Fetchmail configuration generated successfully")
                print(f"Output: {result.stdout}")
            else:
                print(f"❌ Failed to generate fetchmail config: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing fetchmail generation: {e}")
            return False
        
        print(f"\n🎉 All tests passed!")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML syntax: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
