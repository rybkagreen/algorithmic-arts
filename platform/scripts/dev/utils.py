from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).parent.parent  # platform/
SERVICES_DIR = PROJECT_ROOT / "services"

def find_services() -> List[str]:
    """Find all service directories with pyproject.toml"""
    services = []
    if SERVICES_DIR.exists():
        for item in SERVICES_DIR.iterdir():
            if item.is_dir() and (item / "pyproject.toml").exists():
                services.append(item.name)
    return sorted(services)

def get_service_path(service_name: str) -> Optional[Path]:
    """Get full path to service directory"""
    path = SERVICES_DIR / service_name
    return path if path.exists() and (path / "pyproject.toml").exists() else None

def confirm_action(prompt: str) -> bool:
    """Simple confirmation dialog"""
    while True:
        resp = input(f"{prompt} (y/N): ").strip().lower()
        if resp in ("", "n", "no"):
            return False
        if resp in ("y", "yes"):
            return True
        print("Please answer 'y' or 'n'.")

def print_header(title: str):
    print(f"\n{'─' * 60}")
    print(f"🔹 {title}")
    print(f"{'─' * 60}")

def print_error(msg: str):
    print(f"\033[31m❌ {msg}\033[0m")

def print_info(msg: str):
    print(f"\033[34mℹ️  {msg}\033[0m")