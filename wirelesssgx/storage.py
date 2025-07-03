"""Secure storage module for Wireless@SGx credentials"""

import json
import keyring
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet
import base64
import os


class StorageError(Exception):
    """Storage related errors"""
    pass


class SecureStorage:
    """Securely store and retrieve Wireless@SGx credentials"""
    
    def __init__(self):
        self.service_name = "wirelesssgx"
        self.username_key = "username"
        self.password_key = "password"
        self.config_key = "config"
        self.fallback_file = Path.home() / ".config" / "wirelesssgx" / "credentials.enc"
        
    def save_credentials(self, username: str, password: str, isp: str = "singtel") -> bool:
        """Save credentials securely"""
        try:
            # Try keyring first
            keyring.set_password(self.service_name, self.username_key, username)
            keyring.set_password(self.service_name, self.password_key, password)
            
            # Save additional config
            config = {"isp": isp, "last_connection": "success"}
            keyring.set_password(self.service_name, self.config_key, json.dumps(config))
            
            return True
            
        except Exception as e:
            # Fallback to encrypted file
            return self._save_to_file(username, password, isp)
    
    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Retrieve stored credentials"""
        try:
            # Try keyring first
            username = keyring.get_password(self.service_name, self.username_key)
            password = keyring.get_password(self.service_name, self.password_key)
            config_str = keyring.get_password(self.service_name, self.config_key)
            
            if username and password:
                config = json.loads(config_str) if config_str else {"isp": "singtel"}
                return {
                    "username": username,
                    "password": password,
                    "isp": config.get("isp", "singtel")
                }
                
        except Exception:
            pass
        
        # Try fallback file
        return self._load_from_file()
    
    def delete_credentials(self) -> bool:
        """Delete stored credentials"""
        try:
            # Delete from keyring
            keyring.delete_password(self.service_name, self.username_key)
            keyring.delete_password(self.service_name, self.password_key)
            keyring.delete_password(self.service_name, self.config_key)
        except:
            pass
        
        # Delete file if exists
        if self.fallback_file.exists():
            self.fallback_file.unlink()
            
        return True
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for fallback storage"""
        key_file = self.fallback_file.parent / ".key"
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            key_file.write_bytes(key)
            # Make key file readable only by owner
            os.chmod(key_file, 0o600)
            return key
    
    def _save_to_file(self, username: str, password: str, isp: str) -> bool:
        """Save credentials to encrypted file (fallback)"""
        try:
            self.fallback_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Encrypt credentials
            key = self._get_or_create_key()
            f = Fernet(key)
            
            data = {
                "username": username,
                "password": password,
                "isp": isp
            }
            
            encrypted_data = f.encrypt(json.dumps(data).encode())
            
            # Write encrypted data
            self.fallback_file.write_bytes(encrypted_data)
            # Make file readable only by owner
            os.chmod(self.fallback_file, 0o600)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Failed to save credentials: {str(e)}")
    
    def _load_from_file(self) -> Optional[Dict[str, str]]:
        """Load credentials from encrypted file (fallback)"""
        if not self.fallback_file.exists():
            return None
            
        try:
            key = self._get_or_create_key()
            f = Fernet(key)
            
            encrypted_data = self.fallback_file.read_bytes()
            decrypted_data = f.decrypt(encrypted_data)
            
            return json.loads(decrypted_data.decode())
            
        except Exception:
            return None
    
    def has_credentials(self) -> bool:
        """Check if credentials are stored"""
        return self.get_credentials() is not None