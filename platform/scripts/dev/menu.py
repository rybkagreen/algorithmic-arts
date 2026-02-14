
# Try to import rich; fallback to plain print if not available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False

from .utils import find_services, print_error, print_info, confirm_action

def _print_rich_panel(title: str, content: str):
    if RICH_AVAILABLE:
        panel = Panel(content, title=title, border_style="bold blue", padding=(1, 2))
        console.print(panel)
    else:
        print(f"\n{'─' * 60}")
        print(f" {title} ")
        print(f"{'─' * 60}")
        print(content)
        print(f"{'─' * 60}\n")

def _print_menu_options(options: list):
    if RICH_AVAILABLE:
        table = Table(show_header=False, box=None, padding=0)
        for i, (key, label) in enumerate(options, 1):
            table.add_row(f"[bold cyan]{key}[/]", label)
        console.print(table)
    else:
        for i, (key, label) in enumerate(options, 1):
            print(f" [{key}] {label}")

def show_main_menu():
    """Show the main interactive menu."""
    while True:
        _print_rich_panel("🧰 ALGORITHMIC ARTS DEV HUB (v2.1)", 
                         "Interactive developer toolkit — 2026-02-13")

        options = [
            ("1", "📦 Environments (venv, uv, poetry)"),
            ("2", "🚀 Run Services (local or docker)"),
            ("0", "🛑 Exit")
        ]
        _print_menu_options(options)

        try:
            choice = input("\nEnter choice: ").strip()
        except KeyboardInterrupt:
            print("\n")
            break

        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice == "1":
            _menu_environments()
        elif choice == "2":
            _menu_run_services()
        else:
            print_error("Invalid choice. Please enter 0, 1, or 2.")

def _menu_environments():
    _print_rich_panel("📦 Environments", "Manage virtual environments for services")

    options = [
        ("1", "🔍 Status — show venv status for all services"),
        ("2", "➕ Init — create .venv for service(s)"),
        ("3", "🗑️  Clean — remove .venv for service(s)"),
        ("4", "⚡ Use — show activation command"),
        ("0", "Back"),
    ]
    _print_menu_options(options)

    try:
        choice = input("\nEnter choice: ").strip()
    except KeyboardInterrupt:
        return

    if choice == "0":
        return
    elif choice == "1":
        _venv_status()
    elif choice == "2":
        _venv_init()
    elif choice == "3":
        _venv_clean()
    elif choice == "4":
        _venv_use()
    else:
        print_error("Invalid choice.")
    input("\nPress Enter to continue...")

def _venv_status():
    from .venv import status
    status()

def _venv_init():
    from .venv import init_service, init_all
    services = find_services()
    if not services:
        print_error("No services found.")
        return

    print("Available services:")
    for i, svc in enumerate(services, 1):
        print(f" [{i}] {svc}")
    print(" [a] All services")
    print(" [0] Cancel")

    try:
        choice = input("\nSelect service(s): ").strip()
        if choice == "0":
            return
        elif choice == "a":
            if confirm_action("Initialize venv for ALL services?"):
                init_all()
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(services):
                    svc = services[idx]
                    if confirm_action(f"Initialize .venv for '{svc}'?"):
                        init_service(svc)
                else:
                    print_error("Invalid number.")
            except ValueError:
                print_error("Please enter a number or 'a'.")
    except Exception as e:
        print_error(f"Error: {e}")

def _venv_clean():
    from .venv import clean_service, clean_all
    services = find_services()
    if not services:
        print_error("No services found.")
        return

    print("Available services:")
    for i, svc in enumerate(services, 1):
        print(f" [{i}] {svc}")
    print(" [a] All services")
    print(" [0] Cancel")

    try:
        choice = input("\nSelect service(s) to clean: ").strip()
        if choice == "0":
            return
        elif choice == "a":
            if confirm_action("Remove .venv for ALL services?"):
                clean_all()
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(services):
                    svc = services[idx]
                    clean_service(svc)
                else:
                    print_error("Invalid number.")
            except ValueError:
                print_error("Please enter a number or 'a'.")
    except Exception as e:
        print_error(f"Error: {e}")

def _venv_use():
    from .venv import use_service
    services = find_services()
    if not services:
        print_error("No services found.")
        return

    print("Available services:")
    for i, svc in enumerate(services, 1):
        print(f" [{i}] {svc}")
    print(" [0] Cancel")

    try:
        choice = input("\nSelect service to get activation command: ").strip()
        if choice == "0":
            return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(services):
                svc = services[idx]
                use_service(svc)
            else:
                print_error("Invalid number.")
        except ValueError:
            print_error("Please enter a number.")
    except Exception as e:
        print_error(f"Error: {e}")

def _menu_run_services():
    services = find_services()
    if not services:
        print_error("No services found. Expected: platform/services/*/pyproject.toml")
        input("Press Enter to return...")
        return

    _print_rich_panel("🚀 Run Services", "Select a service to run")
    
    # Show services with numbers
    for i, svc in enumerate(services, 1):
        print(f" [{i}] {svc}")
    print(" [0] Back")

    try:
        choice = input("\nEnter service number: ").strip()
        if choice == "0":
            return
        idx = int(choice) - 1
        if 0 <= idx < len(services):
            service_name = services[idx]
            _confirm_and_run(service_name)
        else:
            print_error("Invalid number.")
    except ValueError:
        print_error("Please enter a number.")

    input("Press Enter to return...")

def _confirm_and_run(service_name: str):
    print_info(f"Ready to run '{service_name}'")
    if confirm_action(f"Run {service_name} in local mode?"):
        print(f"\n▶️  Starting {service_name} locally (mock)...")
        print("   (In full version: activates .venv and runs uvicorn)")
    else:
        print_info("Cancelled.")

# Optional: add entry point for non-interactive usage later
if __name__ == "__main__":
    show_main_menu()