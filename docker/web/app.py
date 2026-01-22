#!/usr/bin/env python3
"""
MailDocker Web Interface
Flask application for managing POP3 accounts and configuration
"""

import os
import sys
import yaml
import subprocess
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

# Add scripts to path for imports
sys.path.append('/scripts')
from password_manager import PasswordManager

app = Flask(__name__)
app.secret_key = 'mail-bridge-secret-key-change-in-production'

# Configuration
CONFIG_PATH = '/config/accounts.yaml'
LOG_PATH = '/logs'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.config_path = CONFIG_PATH
        self.password_manager = PasswordManager()
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Decrypt passwords in accounts
                if 'accounts' in config:
                    for account in config['accounts']:
                        if 'encrypted_password' in account:
                            try:
                                account['password'] = self.password_manager.decrypt(account['encrypted_password'])
                            except Exception as e:
                                logging.error(f"Failed to decrypt password for {account.get('name', 'unknown')}: {e}")
                                account['password'] = ''
                return config or {}
        except FileNotFoundError:
            return {'accounts': [], 'settings': {}, 'filter_rules': []}
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {'accounts': [], 'settings': {}, 'filter_rules': []}
    
    def save_config(self, config):
        """Save configuration to YAML file with encrypted passwords"""
        try:
            # Encrypt passwords before saving
            if 'accounts' in config:
                for account in config['accounts']:
                    if 'password' in account and account['password']:
                        # Encrypt the password
                        encrypted = self.password_manager.encrypt(account['password'])
                        account['encrypted_password'] = encrypted
                        # Remove plain text password from saved config
                        del account['password']
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def test_pop3_connection(self, account):
        """Test POP3 connection for an account"""
        try:
            import socket
            import ssl
            import poplib
            
            pop_server = account.get('pop_server')
            pop_port = account.get('pop_port', 995)
            user = account.get('user')
            password = account.get('password', '')  # Password is already decrypted in load_config()
            use_ssl = account.get('ssl', True)
            
            if not all([pop_server, user, password]):
                missing = []
                if not pop_server: missing.append("POP3 server")
                if not user: missing.append("username") 
                if not password: missing.append("password")
                return False, f"Missing required fields: {', '.join(missing)}"
            
            if use_ssl:
                pop = poplib.POP3_SSL(pop_server, pop_port)
            else:
                pop = poplib.POP3(pop_server, pop_port)
            
            pop.user(user)
            pop.pass_(password)
            
            # Get welcome message and stats
            welcome = pop.getwelcome()
            message_count = pop.stat()[0]
            
            pop.quit()
            
            success_msg = f"Connected successfully! Found {message_count} messages on server."
            return True, success_msg
            
            return True, f"Connected successfully. {message_count} messages on server."
            
        except Exception as e:
            # Include password in error message for debugging (remove in production)
            error_msg = f"Connection failed: {str(e)}"
            if password:
                error_msg += f" | Password used: '{password}'"
            else:
                error_msg += " | No password provided"
            return False, error_msg
    
    def restart_services(self):
        """Restart mail services after configuration change"""
        try:
            # Regenerate fetchmail config
            result = subprocess.run(
                ['python3', '/scripts/generate_config.py'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Config generation failed: {result.stderr}"
            
            # Restart fetchmail (if running)
            # Note: In production, this would need proper service management
            return True, "Configuration updated successfully"
            
        except Exception as e:
            return False, f"Restart failed: {str(e)}"

config_manager = ConfigManager()

@app.route('/')
def index():
    """Main dashboard"""
    config = config_manager.load_config()
    accounts = config.get('accounts', [])
    
    # Get basic stats
    total_accounts = len(accounts)
    active_accounts = sum(1 for acc in accounts if acc.get('enabled', True))
    
    return render_template('dashboard.html', 
                         accounts=accounts,
                         total_accounts=total_accounts,
                         active_accounts=active_accounts)

@app.route('/accounts')
def accounts():
    """Account management page"""
    config = config_manager.load_config()
    accounts = config.get('accounts', [])
    return render_template('accounts.html', accounts=accounts)

@app.route('/accounts/add', methods=['GET', 'POST'])
def add_account():
    """Add new account"""
    if request.method == 'POST':
        config = config_manager.load_config()
        
        account = {
            'name': request.form.get('name'),
            'pop_server': request.form.get('pop_server'),
            'pop_port': int(request.form.get('pop_port', 995)),
            'user': request.form.get('user'),
            'password': request.form.get('password', ''),  # Store password for encryption
            'ssl': request.form.get('ssl') == 'on',
            'keep': request.form.get('keep') == 'on',
            'imap_user': request.form.get('imap_user'),
            'enabled': request.form.get('enabled') == 'on',
            'folders': {
                'inbox': 'INBOX',
                'invoices': 'Invoices',
                'priority': 'Priority'
            }
        }
        
        # Validate required fields
        required_fields = ['name', 'pop_server', 'user', 'password', 'imap_user']
        if not all(account.get(field) for field in required_fields):
            flash('Please fill in all required fields', 'error')
            return render_template('account_form.html', account=account, action='add')
        
        # Add to configuration
        config['accounts'].append(account)
        
        if config_manager.save_config(config):
            flash('Account added successfully', 'success')
            return redirect(url_for('accounts'))
        else:
            flash('Failed to save account', 'error')
    
    return render_template('account_form.html', account={}, action='add')

@app.route('/accounts/edit/<account_name>', methods=['GET', 'POST'])
def edit_account(account_name):
    """Edit existing account"""
    config = config_manager.load_config()
    accounts = config.get('accounts', [])
    
    # Find the account
    account = None
    for i, acc in enumerate(accounts):
        if acc.get('name') == account_name:
            account = acc
            account_index = i
            break
    
    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('accounts'))
    
    if request.method == 'POST':
        # Update account data
        account.update({
            'name': request.form.get('name'),
            'pop_server': request.form.get('pop_server'),
            'pop_port': int(request.form.get('pop_port', 995)),
            'user': request.form.get('user'),
            'password': request.form.get('password', ''),  # Store password for encryption
            'ssl': request.form.get('ssl') == 'on',
            'keep': request.form.get('keep') == 'on',
            'imap_user': request.form.get('imap_user'),
            'enabled': request.form.get('enabled') == 'on',
        })
        
        # Update in configuration
        accounts[account_index] = account
        config['accounts'] = accounts
        
        if config_manager.save_config(config):
            flash('Account updated successfully', 'success')
            return redirect(url_for('accounts'))
        else:
            flash('Failed to save account', 'error')
    
    return render_template('account_form.html', account=account, action='edit')

@app.route('/accounts/delete/<account_name>')
def delete_account(account_name):
    """Delete account"""
    config = config_manager.load_config()
    accounts = config.get('accounts', [])
    
    # Remove the account
    accounts = [acc for acc in accounts if acc.get('name') != account_name]
    config['accounts'] = accounts
    
    if config_manager.save_config(config):
        flash('Account deleted successfully', 'success')
    else:
        flash('Failed to delete account', 'error')
    
    return redirect(url_for('accounts'))

@app.route('/accounts/test/<account_name>')
def test_account(account_name):
    """Test POP3 connection"""
    config = config_manager.load_config()
    accounts = config.get('accounts', [])
    
    # Find the account
    account = None
    for acc in accounts:
        if acc.get('name') == account_name:
            account = acc
            break
    
    if not account:
        return jsonify({'success': False, 'message': 'Account not found'})
    
    success, message = config_manager.test_pop3_connection(account)
    return jsonify({'success': success, 'message': message})

@app.route('/filters')
def filters():
    """Filter rules management"""
    config = config_manager.load_config()
    filter_rules = config.get('filter_rules', [])
    return render_template('filters.html', filter_rules=filter_rules)

@app.route('/status')
def status():
    """System status page"""
    # Get service status
    try:
        # Check if fetchmail is running
        result = subprocess.run(['pgrep', '-f', 'fetchmail'], 
                              capture_output=True, text=True)
        fetchmail_running = bool(result.stdout.strip())
    except:
        fetchmail_running = False
    
    # Get recent logs
    recent_logs = []
    try:
        with open(f'{LOG_PATH}/process_mail.log', 'r') as f:
            lines = f.readlines()
            recent_logs = lines[-10:]  # Last 10 lines
    except:
        recent_logs = ["No logs available"]
    
    return render_template('status.html', 
                         fetchmail_running=fetchmail_running,
                         recent_logs=recent_logs)

@app.route('/api/config')
def api_config():
    """API endpoint for configuration"""
    config = config_manager.load_config()
    return jsonify(config)

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """API endpoint to restart services"""
    success, message = config_manager.restart_services()
    return jsonify({'success': success, 'message': message})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('/app/templates', exist_ok=True)
    os.makedirs('/app/static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=8787, debug=True)
