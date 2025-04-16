import os
import platform
import getpass
import yaml
from dataclasses import dataclass, field
from typing import Dict, Optional

OS = platform.system()
USER_NAME = getpass.getuser()

@dataclass
class SessionConfig:
    config_path: str
    base_config: Dict = field(default_factory=dict)
    atd_config: Dict = field(default_factory=dict)
    act_config: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.base_config = self._load_config("base.yml")
        self.atd_config = self._load_config("atd.yml")
        self.act_config = self._load_config("act.yml")

    def _load_config(self, filename: str) -> dict:
        config_file = os.path.join(self.config_path, filename)
        with open(config_file, "r", encoding="UTF-8") as f:
            return yaml.safe_load(f)

    @property
    def crt_path(self) -> str:
        return self.base_config.get("crt_path") or self._default_session_path()

    @staticmethod
    def _default_session_path() -> str:
        if OS == "Windows":
            return f"C:\\Documents and Settings\\{USER_NAME}\\Application Data\\VanDyke\\Config\\Sessions"
        elif OS == "Darwin":
            return f"/Users/{USER_NAME}/Library/Application Support/VanDyke/SecureCRT/Config/Sessions"
        else:
            raise Exception("[Error] Unsupported operating system.")

    def get_directory_config(self, provider: str) -> Dict:
        return self.base_config["directory"][provider]

    def get_provider_config(self, provider: str) -> Dict:
        if provider == "atd":
            return self.atd_config
        elif provider == "act":
            return self.act_config
        raise ValueError(f"Unknown provider: {provider}")

    def to_dict(self) -> Dict:
        return {
            "crt_path": self.crt_path,
            "directory": self.base_config["directory"],
            "atd": self.atd_config,
            "act": self.act_config
        }

@dataclass
class Session:
    file_name: str
    host: str
    protocol: str
    port: str
    username: str
    password: str
    jumphost: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "file_name": self.file_name,
            "host": self.host,
            "protocol": self.protocol,
            "port": self.port,
            "jumphost": self.jumphost,
            "username": self.username,
            "password": self.password
        } 