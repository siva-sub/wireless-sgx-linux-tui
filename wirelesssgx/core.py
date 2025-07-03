"""Core functionality adapted from naungsai.py for Wireless@SGx registration"""

import sys
import os
import requests
import datetime
import codecs
from typing import Dict, Optional, Tuple
from Crypto.Cipher import AES


# ISP Configuration
ISP_CONFIG = {
    "singtel": {
        "essa_url": "https://singtel-wsg.singtel.com/essa_r12",
        "api_password": "",
        "create_api_versions": ("2.6", "2.8"),
        "retrieve_api_versions": ("2.0", "2.6")
    },
    "starhub": {
        "essa_url": "https://api.wifi.starhub.net.sg/essa_r12",
        "api_password": "5t4rHUB4p1",
        "create_api_versions": ("2.6", "2.8"),
        "retrieve_api_versions": ("2.0", "2.6")
    },
}

DEFAULT_ISP = "singtel"
DEFAULT_TRANSID = b"053786654500000000000000"
RC_SUCCESS = 1100


class WirelessSGXError(Exception):
    """Base exception for Wireless@SGx errors"""
    pass


class HTTPError(WirelessSGXError):
    """HTTP request errors"""
    pass


class ServerError(WirelessSGXError):
    """Server response errors"""
    pass


class ValidationError(WirelessSGXError):
    """Validation errors"""
    pass


class WirelessSGXClient:
    """Client for Wireless@SGx registration and authentication"""
    
    def __init__(self, isp: str = DEFAULT_ISP):
        if isp not in ISP_CONFIG:
            raise ValueError(f"Invalid ISP: {isp}. Choose from: {list(ISP_CONFIG.keys())}")
        self.isp = isp
        self.config = ISP_CONFIG[isp]
        self.transid = DEFAULT_TRANSID
        
    def _validate_response(self, resp: dict, key: str, val=None) -> None:
        """Validate server response"""
        if key not in resp:
            raise ValidationError(f"Server response missing key: {key}")
        if val is not None and resp[key] != val:
            raise ValidationError(f"Unexpected value for {key}: {resp[key]} != {val}")
    
    def _check_for_error(self, resp: dict) -> None:
        """Check if response contains an error"""
        self._validate_response(resp, "status")
        self._validate_response(resp["status"], "resultcode")
        
        rc = int(resp["status"]["resultcode"])
        if rc != RC_SUCCESS:
            msg = resp.get("body", {}).get("message", "Unknown error")
            raise ServerError(f"Server error (code {rc}): {msg}")
    
    def request_registration(self, mobile: str, dob: str, 
                           salutation: str = "Mr", name: str = "Some Person",
                           gender: str = "m", country: str = "SG",
                           email: str = "nonexistent@noaddresshere.com",
                           retrieve_mode: bool = False) -> str:
        """Request registration/retrieve and return success code"""
        
        api = "retrieve_user_r12x2a" if retrieve_mode else "create_user_r12x1a"
        api_version = self.config["retrieve_api_versions"][0] if retrieve_mode else self.config["create_api_versions"][0]
        
        params = {
            "api": api,
            "api_password": self.config["api_password"],
            "salutation": salutation,
            "name": name,
            "gender": gender,
            "dob": dob,
            "mobile": mobile,
            "nationality": country,
            "email": email,
            "tid": self.transid.decode() if isinstance(self.transid, bytes) else self.transid,
        }
        
        # Debug logging
        import json
        debug_params = {k: (v.decode() if isinstance(v, bytes) else v) for k, v in params.items() if k != 'api_password'}
        print(f"DEBUG: Making request to {self.config['essa_url']}")
        print(f"DEBUG: With params: {json.dumps(debug_params, indent=2)}")
        
        try:
            r = requests.get(self.config["essa_url"], params=params, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            raise HTTPError(f"Failed to make registration request: {e}")
        
        try:
            resp = r.json()
            print(f"DEBUG: Response: {json.dumps(resp, indent=2)}")
        except ValueError:
            raise ValidationError("Invalid JSON response from server")
        
        self._check_for_error(resp)
        self._validate_response(resp, "api", api)
        self._validate_response(resp, "version", api_version)
        self._validate_response(resp, "body")
        self._validate_response(resp["body"], "success_code")
        
        return resp["body"]["success_code"]
    
    def validate_otp(self, mobile: str, dob: str, otp: str,
                     success_code: str, retrieve_mode: bool = False) -> Dict:
        """Validate OTP and return credentials"""
        
        api = "retrieve_user_r12x2b" if retrieve_mode else "create_user_r12x1b"
        api_version = self.config["retrieve_api_versions"][1] if retrieve_mode else self.config["create_api_versions"][1]
        
        params = {
            "api": api,
            "api_password": self.config["api_password"],
            "dob": dob,
            "mobile": mobile,
            "otp": otp,
            "success_code": success_code,
            "tid": self.transid.decode() if isinstance(self.transid, bytes) else self.transid
        }
        
        try:
            r = requests.get(self.config["essa_url"], params=params, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            raise HTTPError(f"Failed to validate OTP: {e}")
        
        try:
            resp = r.json()
        except ValueError:
            raise ValidationError("Invalid JSON response from server")
        
        self._check_for_error(resp)
        self._validate_response(resp, "api", api)
        self._validate_response(resp, "version", api_version)
        self._validate_response(resp, "body")
        
        required_fields = ["userid", "enc_userid", "tag_userid", 
                          "enc_password", "tag_password", "iv"]
        for field in required_fields:
            self._validate_response(resp["body"], field)
        
        def hexdecode(s):
            return codecs.decode(bytes(s, "utf8"), encoding="hex")
        
        return {
            "userid": bytes(resp["body"]["userid"], "utf8"),
            "enc_userid": hexdecode(resp["body"]["enc_userid"]),
            "tag_userid": hexdecode(resp["body"]["tag_userid"]),
            "enc_password": hexdecode(resp["body"]["enc_password"]),
            "tag_password": hexdecode(resp["body"]["tag_password"]),
            "nonce": bytes(resp["body"]["iv"], "utf8")
        }
    
    def decrypt_credentials(self, encrypted_data: Dict, otp: str) -> Tuple[str, str]:
        """Decrypt credentials and return username, password"""
        
        decryption_date = datetime.datetime.now()
        try_dates = [
            decryption_date,
            decryption_date + datetime.timedelta(1),
            decryption_date + datetime.timedelta(-1)
        ]
        
        for date in try_dates:
            key = self._build_decrypt_key(date, otp)
            try:
                decrypted_userid = self._decrypt(
                    key,
                    encrypted_data["nonce"],
                    encrypted_data["tag_userid"],
                    encrypted_data["enc_userid"]
                )
                
                if decrypted_userid == encrypted_data["userid"]:
                    password = self._decrypt(
                        key,
                        encrypted_data["nonce"],
                        encrypted_data["tag_password"],
                        encrypted_data["enc_password"]
                    )
                    
                    return (
                        encrypted_data["userid"].decode(),
                        password.decode()
                    )
            except Exception:
                continue
        
        raise ValidationError("Failed to decrypt credentials. Invalid OTP or date mismatch.")
    
    def _build_decrypt_key(self, date: datetime.datetime, otp: str) -> bytes:
        """Build decryption key from date, transid, and OTP"""
        date_hex = b"%03x" % int(date.strftime("%e%m").strip())
        otp_hex = b"%05x" % int(otp)
        key_hex = date_hex + self.transid + otp_hex
        return codecs.decode(key_hex, "hex")
    
    def _decrypt(self, key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
        """Decrypt using AES-CCM"""
        aes = AES.new(key, AES.MODE_CCM, nonce)
        aes.update(tag)
        return aes.decrypt(ciphertext)