import os
from typing import Dict, List, Any
from alab2crt.core.session import Session, SessionConfig

class ATDProvider:
    def __init__(self, config: SessionConfig) -> None:
        self.config = config
        self.provider_config = config.get_provider_config("atd")
        self.directory_config = config.get_directory_config("atd")

    def _clean_lab_name(self, lab: str | None) -> str | None:
        if lab is None:
            return None
        return lab.removesuffix("-eos.topo.testdrive.arista.com")

    def create_jumphost_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        sessions: Dict[str, List[Dict[str, Any]]] = {}
        for atd in self.provider_config["atd"]:
            lab = self._clean_lab_name(atd["lab"])
            if lab is None:
                continue
            jumphost_host = f"{lab}-eos.topo.testdrive.arista.com"
            jumphost_dir = self.directory_config["jumphost_dir"]

            session = Session(
                file_name=f"{jumphost_host}.ini",
                host=jumphost_host,
                protocol="SSH2",
                port="22",
                jumphost=None,
                username=atd["username"],
                password=atd["password"]
            )
            sessions.setdefault(os.path.join(lab, jumphost_dir), []).append(session.to_dict())
        return sessions

    def create_child_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        sessions: Dict[str, List[Dict[str, Any]]] = {}
        top_dir = self.directory_config["top_dir"]
        jumphost_dir = self.directory_config["jumphost_dir"]
        types = self.provider_config.get("type", {})

        for atd in self.provider_config["atd"]:
            lab = self._clean_lab_name(atd["lab"])
            if lab is None:
                continue
            topology = atd.get("topology")
            if topology is None:
                continue
            jumphost_host_file = f"{lab}-eos.topo.testdrive.arista.com"
            jumphost_full_path = os.path.join(top_dir, lab, jumphost_dir, jumphost_host_file)

            devices = types.get(topology, {})
            for device_name, last_octet in devices.items():
                host_ip = f"192.168.0.{last_octet}"
                session = Session(
                    file_name=f"{device_name}_{host_ip}.ini",
                    host=host_ip,
                    protocol="SSH2",
                    port="22",
                    jumphost=jumphost_full_path,
                    username=atd["username"],
                    password=atd["password"]
                )
                sessions.setdefault(lab, []).append(session.to_dict())
        return sessions 