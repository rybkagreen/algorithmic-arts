import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

from .utils import (
    find_services,
    get_service_path,
    print_header,
    print_error,
    print_info,
    confirm_action,
)

PROJECT_ROOT = Path(__file__).parent.parent  # platform/
SERVICES_DIR = PROJECT_ROOT / "services"

def _run_cmd(cmd: List[str], cwd: Path, check: bool = True) -> Tuple[int, str]:
    """Run command and return (returncode, stdout+stderr)"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max
        )
        output = result.stdout + result.stderr
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, "Command timed out after 5 minutes"
    except Exception as e:
        return -1, f"Exception: {e}"

def _has_poetry(service_path: Path) -> bool:
    """Check if service uses Poetry (has pyproject.toml + poetry.lock)"""
    return (service_path / "pyproject.toml").exists() and (service_path / "poetry.lock").exists()

def _has_requirements(service_path: Path) -> bool:
    """Check if service has requirements.txt"""
    return (service_path / "requirements.txt").exists()

def init_service(service_name: str, force: bool = False) -> bool:
    """Initialize venv for a single service."""
    svc_path = get_service_path(service_name)
    if not svc_path:
        print_error(f"Service '{service_name}' not found.")
        return False

    venv_path = svc_path / ".venv"
    if venv_path.exists():
        if not force:
            print_error(f".venv already exists in {service_name}. Use --force to overwrite.")
            return False
        print_info(f"Removing existing .venv in {service_name}...")
        try:
            import shutil
            shutil.rmtree(venv_path)
        except Exception as e:
            print_error(f"Failed to remove {venv_path}: {e}")
            return False

    print_info(f"Creating .venv for {service_name}...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=svc_path, check=True)
    except Exception as e:
        print_error(f"Failed to create venv: {e}")
        return False

    # Activate venv
    venv_bin = venv_path / "bin" / "python"
    if not venv_bin.exists():
        print_error("venv created but python not found.")
        return False

    # Install dependencies
    if _has_poetry(svc_path):
        print_info("Using Poetry to install dependencies...")
        rc, out = _run_cmd([str(venv_bin), "-m", "pip", "install", "poetry"], cwd=svc_path)
        if rc != 0:
            print_error(f"Failed to install poetry: {out[:200]}")
            return False
        rc, out = _run_cmd([str(venv_bin), "-m", "poetry", "install", "--no-dev"], cwd=svc_path)
        if rc != 0:
            print_error(f"Poetry install failed: {out[:200]}")
            return False
    elif _has_requirements(svc_path):
        print_info("Using pip to install from requirements.txt...")
        rc, out = _run_cmd([str(venv_bin), "-m", "pip", "install", "-r", "requirements.txt"], cwd=svc_path)
        if rc != 0:
            print_error(f"pip install failed: {out[:200]}")
            return False
    else:
        print_error(f"No dependency manifest found in {service_name} (missing pyproject.toml/poetry.lock or requirements.txt)")
        return False

    print_info(f"✅ .venv initialized for {service_name}")
    return True

def init_all(force: bool = False) -> int:
    """Initialize venv for all services."""
    services = find_services()
    if not services:
        print_error("No services found.")
        return 1

    success_count = 0
    for i, svc in enumerate(services, 1):
        print(f"\n[{i}/{len(services)}] Initializing {svc}...")
        if init_service(svc, force=force):
            success_count += 1
        else:
            print_error(f"❌ Failed to initialize {svc}")

    print_header(f"Summary: {success_count}/{len(services)} services initialized")
    return 0 if success_count == len(services) else 1

def status() -> None:
    """Show status of all service venvs."""
    services = find_services()
    if not services:
        print_error("No services found.")
        return

    print_header("📦 Virtual Environment Status")
    print(f"{'Service':<20} {'.venv':<8} {'Python':<8} {'Deps OK':<8} {'Notes'}")
    print("-" * 70)

    for svc in services:
        svc_path = SERVICES_DIR / svc
        venv_path = svc_path / ".venv"
        venv_exists = venv_path.exists()
        python_version = "—"
        deps_ok = "—"
        notes = ""

        if venv_exists:
            python_bin = venv_path / "bin" / "python"
            if python_bin.exists():
                try:
                    result = subprocess.run([str(python_bin), "--version"], capture_output=True, text=True, timeout=10)
                    python_version = result.stdout.strip().replace("Python ", "")
                except Exception:
                    python_version = "error"
            else:
                notes = "⚠️ python not found"

            # Check if deps are installed (simplified: check site-packages has fastapi or sqlalchemy)
            site_packages = venv_path / "lib" / f"python3.{sys.version_info.minor}" / "site-packages"
            if site_packages.exists():
                # Quick check: look for at least one major dep
                has_fastapi = (site_packages / "fastapi").exists() or (site_packages / "fastapi.pth").exists()
                has_sqla = (site_packages / "sqlalchemy").exists()
                deps_ok = "✅" if (has_fastapi or has_sqla) else "❓"
            else:
                deps_ok = "❌"

        print(f"{svc:<20} {('✅' if venv_exists else '❌'):<8} {python_version:<8} {deps_ok:<8} {notes}")

    print()

def clean_service(service_name: str, dry_run: bool = False) -> bool:
    """Clean venv for a single service."""
    svc_path = get_service_path(service_name)
    if not svc_path:
        print_error(f"Service '{service_name}' not found.")
        return False

    venv_path = svc_path / ".venv"
    if not venv_path.exists():
        print_info(f"No .venv found in {service_name}")
        return True

    if dry_run:
        print_info(f"[DRY RUN] Would remove {venv_path}")
        return True

    if not confirm_action(f"Remove .venv for {service_name}?"):
        return False

    try:
        import shutil
        shutil.rmtree(venv_path)
        print_info(f"✅ Removed {venv_path}")
        return True
    except Exception as e:
        print_error(f"Failed to remove {venv_path}: {e}")
        return False

def clean_all(dry_run: bool = False) -> int:
    """Clean venv for all services."""
    services = find_services()
    if not services:
        print_error("No services found.")
        return 1

    success_count = 0
    for svc in services:
        if clean_service(svc, dry_run=dry_run):
            success_count += 1

    print_header(f"Clean summary: {success_count}/{len(services)}")
    return 0

def use_service(service_name: str) -> None:
    """Print activation command for a service."""
    svc_path = get_service_path(service_name)
    if not svc_path:
        print_error(f"Service '{service_name}' not found.")
        return

    venv_bin = svc_path / ".venv" / "bin"
    if not venv_bin.exists():
        print_error(f".venv not found for {service_name}. Run 'venv init {service_name}' first.")
        return

    print_info(f"To activate {service_name}:")
    print(f"  source {venv_bin}/activate")
    print()
    print_info("Tip: Add this alias to ~/.bashrc:")
    print(f'  alias {service_name}="cd {svc_path} && source .venv/bin/activate"')

# CLI interface (to be called from menu.py)
def cli_entrypoint(args):
    """Entry point for venv commands."""
    if args.command == "init":
        if args.service:
            init_service(args.service, force=args.force)
        else:
            init_all(force=args.force)
    elif args.command == "status":
        status()
    elif args.command == "clean":
        if args.service:
            clean_service(args.service, dry_run=args.dry_run)
        else:
            clean_all(dry_run=args.dry_run)
    elif args.command == "use":
        if args.service:
            use_service(args.service)
        else:
            print_error("Usage: venv use <SERVICE>")
    else:
        print_error("Unknown command")