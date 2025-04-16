import os
import json
import time
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from alab2crt.core.session import Session, SessionConfig

class ACTProvider:
    def __init__(self, config: SessionConfig) -> None:
        self.config = config
        self.provider_config = config.get_provider_config("act")["act"]
        self.directory_config = config.get_directory_config("act")
        self.api_url = self.provider_config["api_url"]
        self.api_key = self.provider_config["api_key"]
        self.act_username = self.provider_config["act_username"]
        self._token: Optional[str] = None
        self._token_expiration: Optional[int] = None
        self._token_file = Path.home() / ".alab2crt" / "act_token.json"
        self._load_token()

    def _load_token(self) -> None:
        try:
            if self._token_file.exists():
                with open(self._token_file, "r") as f:
                    token_data = json.load(f)
                    current_time = int(time.time())
                    
                    if token_data["expiration"] > current_time + 60:
                        self._token = token_data["token"]
                        self._token_expiration = token_data["expiration"]
        except Exception:
            pass

    def _save_token(self, token: str, expiration: int) -> None:
        try:
            self._token_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._token_file, "w") as f:
                json.dump({
                    "token": token,
                    "expiration": expiration
                }, f)
        except Exception:
            pass

    def _get_auth_token(self) -> str:
        current_time = int(time.time())
        
        if self._token and self._token_expiration and current_time < self._token_expiration - 60:
            return self._token

        url = f"{self.api_url}/rest/v1/auth/login"
        response = requests.post(url, json={"api_key": self.api_key})
        response.raise_for_status()
        
        auth_data = response.json()
        self._token = auth_data["token"]
        self._token_expiration = auth_data["expiration"]
        
        self._save_token(self._token, self._token_expiration)
        
        return self._token

    def _get_labs(self) -> List[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {self._get_auth_token()}"}
        url = f"{self.api_url}/rest/v1/labs?user={self.act_username}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["result"]

    def _get_lab_details(self, lab_id: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self._get_auth_token()}"}
        url = f"{self.api_url}/rest/v1/labs/{lab_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def create_jumphost_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.provider_config["api_key"] or not self.provider_config["act_username"]:
            print("Skipping ACT labs: API key or username is not configured")
            return {}
        
        sessions: Dict[str, List[Dict[str, Any]]] = {}
        labs = self._get_labs()

        for lab in labs:
            lab_name = lab["name"]
            lab_details = self._get_lab_details(lab["id"])
            
            if not lab_details.get("devices"):
                print(f"Skipping lab {lab_name} - no devices found")
                continue

            cvp_devices = lab_details["devices"].get("cvp", [])
            if not cvp_devices:
                print(f"Skipping lab {lab_name} - no CVP device found")
                continue

            for cvp in cvp_devices:
                if cvp["state"] != "Running":
                    print(f"Skipping CVP in lab {lab_name} - not running")
                    continue

                session = Session(
                    file_name=f"{lab_name}_cvp.ini",
                    host=cvp["internal_ip"],
                    protocol="SSH2",
                    port="22",
                    jumphost=None,
                    username=cvp["shell_logins"][0]["username"],
                    password=cvp["shell_logins"][0]["password"]
                )
                sessions.setdefault(os.path.join(lab_name, self.directory_config["jumphost_dir"]), []).append(session.to_dict())

        return sessions

    def create_child_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.provider_config["api_key"] or not self.provider_config["act_username"]:
            print("Skipping ACT labs: API key or username is not configured")
            return {}

        sessions: Dict[str, List[Dict[str, Any]]] = {}
        labs = self._get_labs()

        for lab in labs:
            lab_name = lab["name"]
            lab_details = self._get_lab_details(lab["id"])
            
            if not lab_details.get("devices"):
                print(f"Skipping lab {lab_name} - no devices found")
                continue

            cvp_devices = lab_details["devices"].get("cvp", [])
            if not cvp_devices:
                print(f"Skipping lab {lab_name} - no CVP device found")
                continue

            if cvp_devices[0]["state"] != "Running":
                print(f"Skipping lab {lab_name} - CVP not running")
                continue

            cvp = cvp_devices[0]
            jumphost_path = os.path.join(
                self.directory_config["top_dir"],
                lab_name,
                self.directory_config["jumphost_dir"],
                f"{lab_name}_cvp"
            )

            for device_type, devices in lab_details["devices"].items():
                if device_type == "cvp":
                    continue

                if not devices:
                    continue

                for device in devices:
                    if device["state"] != "Running":
                        print(f"Skipping device {device['hostname']} in lab {lab_name} - not running")
                        continue

                    session = Session(
                        file_name=f"{lab_name}_{device['hostname']}.ini",
                        host=device["internal_ip"],
                        protocol="SSH2",
                        port="22",
                        jumphost=jumphost_path,
                        username=device["shell_logins"][0]["username"],
                        password=device["shell_logins"][0]["password"]
                    )
                    sessions.setdefault(lab_name, []).append(session.to_dict())

        return sessions 