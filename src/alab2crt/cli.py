#!/usr/bin/env python

import os
import argparse
import shutil
from typing import Dict, List, Any
from crtgen.crt import CRT
from alab2crt.core.session import SessionConfig
from alab2crt.providers.atd import ATDProvider

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SecureCRT session generator")
    parser.add_argument("-c", "--clean", action="store_true", help="Clean all session directories")
    parser.add_argument("-p", "--provider", default="atd", help="Provider to use (default: atd)")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    config_path = os.path.join(os.path.dirname(__file__), "config")
    config = SessionConfig(config_path)

    if args.provider == "atd":
        provider = ATDProvider(config)
        atd_top_path = os.path.join(config.crt_path, config.get_directory_config("atd")["top_dir"])

        if args.clean:
            if os.path.exists(atd_top_path):
                print(f"Deleting directory: {atd_top_path}")
                shutil.rmtree(atd_top_path)
                print("ATD directory deleted.")
            else:
                print("ATD directory does not exist. Nothing to clean.")
            return

        jumphost_sessions = provider.create_jumphost_sessions()
        CRT(config.to_dict(), "atd", jumphost_sessions, is_jumphost=True).run()

        device_sessions = provider.create_child_sessions()
        CRT(config.to_dict(), "atd", device_sessions).run()
    else:
        raise ValueError(f"Unknown provider: {args.provider}")

if __name__ == "__main__":
    main() 