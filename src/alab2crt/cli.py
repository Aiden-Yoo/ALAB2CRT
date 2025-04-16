import os
import argparse
import shutil
from crtgen.crt import CRT
from alab2crt.core.session import SessionConfig
from alab2crt.providers.atd import ATDProvider
from alab2crt.providers.act import ACTProvider

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SecureCRT session generator")
    parser.add_argument("-c", "--clean", action="store_true", help="Clean all session directories")
    parser.add_argument("-p", "--provider", choices=["atd", "act"], 
                       help="Provider to use (if not specified, all providers will be used)")
    return parser.parse_args()

def clean_directory(path: str, provider: str) -> None:
    if os.path.exists(path):
        print(f"Deleting directory: {path}")
        shutil.rmtree(path)
        print(f"{provider.upper()} directory deleted.")
    else:
        print(f"{provider.upper()} directory does not exist. Nothing to clean.")

def create_sessions(config: SessionConfig, provider_name: str) -> None:
    if provider_name == "atd":
        provider = ATDProvider(config)
    elif provider_name == "act":
        provider = ACTProvider(config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

    print(f"\nCreating {provider_name.upper()} sessions...")
    jumphost_sessions = provider.create_jumphost_sessions()
    CRT(config.to_dict(), provider_name, jumphost_sessions, is_jumphost=True).run()

    device_sessions = provider.create_child_sessions()
    CRT(config.to_dict(), provider_name, device_sessions).run()
    print(f"{provider_name.upper()} sessions created successfully.")

def main() -> None:
    args = parse_args()
    config_path = os.path.join(os.path.dirname(__file__), "config")
    config = SessionConfig(config_path)

    if args.clean:
        atd_top_path = os.path.join(config.crt_path, config.get_directory_config("atd")["top_dir"])
        clean_directory(atd_top_path, "atd")

        act_top_path = os.path.join(config.crt_path, config.get_directory_config("act")["top_dir"])
        clean_directory(act_top_path, "act")
        return

    if args.provider is None:
        create_sessions(config, "atd")
        create_sessions(config, "act")
    else:
        create_sessions(config, args.provider)

if __name__ == "__main__":
    main() 