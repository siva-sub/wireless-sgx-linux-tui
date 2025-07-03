"""Network configuration module for Wireless@SGx"""

import os
import subprocess
import uuid
from pathlib import Path
from typing import Optional, Tuple


class NetworkConfigError(Exception):
    """Network configuration errors"""
    pass


class NetworkManager:
    """Handle network configuration for Wireless@SGx"""
    
    def __init__(self):
        self.connection_name = "Wireless@SGx"
        self.ssid = "Wireless@SGx"
        
    def detect_network_manager(self) -> str:
        """Detect which network manager is in use"""
        # Check for NetworkManager
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "NetworkManager"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "networkmanager"
        except FileNotFoundError:
            pass
        
        # Check for systemd-networkd
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "systemd-networkd"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "systemd-networkd"
        except FileNotFoundError:
            pass
        
        # Check for wpa_supplicant directly
        if Path("/etc/wpa_supplicant").exists():
            return "wpa_supplicant"
        
        raise NetworkConfigError("No supported network manager found")
    
    def configure_network(self, username: str, password: str) -> bool:
        """Configure network with credentials"""
        network_manager = self.detect_network_manager()
        
        if network_manager == "networkmanager":
            return self._configure_networkmanager(username, password)
        elif network_manager == "systemd-networkd":
            return self._configure_systemd_networkd(username, password)
        elif network_manager == "wpa_supplicant":
            return self._configure_wpa_supplicant(username, password)
        
        return False
    
    def _configure_networkmanager(self, username: str, password: str) -> bool:
        """Configure NetworkManager connection"""
        try:
            # Remove existing connection if exists
            subprocess.run(
                ["nmcli", "connection", "delete", self.connection_name],
                capture_output=True
            )
        except:
            pass
        
        # Create new connection
        cmd = [
            "nmcli", "connection", "add",
            "type", "wifi",
            "con-name", self.connection_name,
            "ifname", "*",
            "ssid", self.ssid,
            "wifi-sec.key-mgmt", "wpa-eap",
            "802-1x.eap", "peap",
            "802-1x.phase2-auth", "mschapv2",
            "802-1x.identity", username,
            "802-1x.password", password,
            "802-1x.anonymous-identity", "",
            "connection.autoconnect", "yes"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            raise NetworkConfigError(f"Failed to configure NetworkManager: {e.stderr}")
    
    def _configure_systemd_networkd(self, username: str, password: str) -> bool:
        """Configure systemd-networkd with wpa_supplicant"""
        # Generate wpa_supplicant configuration
        wpa_config = f'''network={{
    ssid="{self.ssid}"
    key_mgmt=WPA-EAP
    eap=PEAP
    phase2="auth=MSCHAPV2"
    identity="{username}"
    password="{password}"
    anonymous_identity=""
}}'''
        
        # Write wpa_supplicant config
        wpa_config_path = Path("/etc/wpa_supplicant/wpa_supplicant-wlan0.conf")
        try:
            wpa_config_path.parent.mkdir(parents=True, exist_ok=True)
            wpa_config_path.write_text(wpa_config)
            
            # Enable and start wpa_supplicant service
            subprocess.run(
                ["systemctl", "enable", "wpa_supplicant@wlan0.service"],
                check=True
            )
            subprocess.run(
                ["systemctl", "restart", "wpa_supplicant@wlan0.service"],
                check=True
            )
            
            return True
        except Exception as e:
            raise NetworkConfigError(f"Failed to configure systemd-networkd: {str(e)}")
    
    def _configure_wpa_supplicant(self, username: str, password: str) -> bool:
        """Configure wpa_supplicant directly"""
        # Similar to systemd-networkd but without systemd
        wpa_config = f'''ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1

network={{
    ssid="{self.ssid}"
    key_mgmt=WPA-EAP
    eap=PEAP
    phase2="auth=MSCHAPV2"
    identity="{username}"
    password="{password}"
    anonymous_identity=""
}}'''
        
        wpa_config_path = Path("/etc/wpa_supplicant/wpa_supplicant.conf")
        try:
            wpa_config_path.write_text(wpa_config)
            return True
        except Exception as e:
            raise NetworkConfigError(f"Failed to configure wpa_supplicant: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test if connected to Wireless@SGx"""
        try:
            # Check with nmcli first
            result = subprocess.run(
                ["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith("yes:") and self.ssid in line:
                    return True
                    
        except:
            pass
        
        # Check with iwconfig
        try:
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True
            )
            
            if self.ssid in result.stdout:
                return True
                
        except:
            pass
        
        return False
    
    def get_manual_config_instructions(self, username: str, password: str) -> str:
        """Get manual configuration instructions"""
        return f"""Manual Network Configuration Instructions:

1. Open your network settings
2. Add a new WiFi connection
3. Use these settings:
   
   SSID: {self.ssid}
   Security: WPA & WPA2 Enterprise
   Authentication: Protected EAP (PEAP)
   Anonymous identity: (leave blank)
   CA certificate: (No CA certificate is required)
   PEAP version: Automatic
   Inner authentication: MSCHAPv2
   Username: {username}
   Password: {password}

4. Save and connect to the network"""