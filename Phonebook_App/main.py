import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from database import DatabaseManager
from models import Contact, User
from validators import validate_phone, validate_email, validate_username, validate_password

console = Console()
db = DatabaseManager()

# ─────────────────────────────────────────────
#  Auth screens
# ─────────────────────────────────────────────

def auth_menu() -> User:
    """Show login/register menu and return authenticated User."""
    while True:
        console.print(Panel("[bold cyan]PHONEBOOK MANAGEMENT SYSTEM[/bold cyan]", expand=False))
        console.print("1. [green]Login[/green]")
        console.print("2. [yellow]Register new account[/yellow]")
        console.print("0. [dim]Exit[/dim]")

        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2"])

        if choice == "0":
            console.print("[bold green]Goodbye![/bold green]")
            sys.exit(0)

        elif choice == "1":
            user = login_flow()
            if user:
                return user

        elif choice == "2":
            register_flow()


def login_flow() -> User | None:
    console.print("\n[bold cyan]--- Login ---[/bold cyan]")
    user_name = Prompt.ask("Username")
    password = Prompt.ask("Password", password=True)

    user = db.login_user(user_name, password)
    if user:
        console.print(f"[bold green]Welcome, {user.user_name}![/bold green]")
        return user
    else:
        console.print("[bold red]Invalid username or password![/bold red]")
        return None


def register_flow():
    console.print("\n[bold cyan]--- Register Account ---[/bold cyan]")

    while True:
        user_name = Prompt.ask("Username (≥3 chars, letters/digits/underscore)")
        if validate_username(user_name):
            break
        console.print("[bold red]Invalid username! Must be ≥3 characters (a-z, 0-9, _).[/bold red]")

    while True:
        password = Prompt.ask("Password (≥6 characters)", password=True)
        if validate_password(password):
            break
        console.print("[bold red]Password must be at least 6 characters![/bold red]")

    confirm_pw = Prompt.ask("Confirm password", password=True)
    if password != confirm_pw:
        console.print("[bold red]Passwords do not match![/bold red]")
        return

    user = db.register_user(user_name, password)
    if user:
        console.print("[bold green]Registration successful! Please login.[/bold green]")
    else:
        console.print("[bold red]Username already exists![/bold red]")


# ─────────────────────────────────────────────
#  Main menu (after login)
# ─────────────────────────────────────────────

def display_menu(user: User):
    console.print(f"\n[bold cyan]=== {user.user_name.upper()}'S PHONEBOOK ===[/bold cyan]")
    console.print("1. [green]Add new contact[/green]")
    console.print("2. [yellow]Edit contact[/yellow]")
    console.print("3. [red]Delete contact[/red]")
    console.print("4. [blue]Search (Name/Phone)[/blue]")
    console.print("5. [magenta]View all contacts[/magenta]")
    console.print("6. [cyan]Filter by category[/cyan]")
    console.print("7. [bright_green]Manage categories[/bright_green]")
    console.print("0. [dim]Logout[/dim]")


# ─────────────────────────────────────────────
#  Category management
# ─────────────────────────────────────────────

def category_menu(user: User):
    """Sub-menu for managing categories."""
    while True:
        console.print("\n[bold bright_green]--- Manage Categories ---[/bold bright_green]")
        show_categories(user)
        console.print("\n1. [green]Add new category[/green]")
        console.print("2. [red]Delete category[/red]")
        console.print("0. [dim]Go back[/dim]")

        choice = Prompt.ask("Select an option", choices=["0", "1", "2"])

        if choice == "0":
            return

        elif choice == "1":
            cate_name = Prompt.ask("Enter new category name")
            if not cate_name.strip():
                console.print("[bold red]Category name cannot be empty![/bold red]")
                continue
            result = db.add_category(cate_name.strip(), user.userid)
            if result:
                console.print(f"[bold green]Category '{result.cate_name}' added![/bold green]")
            else:
                console.print("[bold red]Failed to add category![/bold red]")

        elif choice == "2":
            categories = db.get_categories(user.userid)
            if not categories:
                console.print("[bold yellow]No categories found![/bold yellow]")
                continue
            try:
                cate_id = int(Prompt.ask("Enter category ID to delete"))
                if Confirm.ask(f"Are you sure you want to delete category ID {cate_id}?"):
                    if db.delete_category(cate_id, user.userid):
                        console.print("[bold green]Category deleted! Contacts in this category are now uncategorized.[/bold green]")
                    else:
                        console.print(f"[bold red]Category ID {cate_id} not found![/bold red]")
            except ValueError:
                console.print("[bold red]ID must be an integer![/bold red]")


def show_categories(user: User):
    """Display all categories for current user."""
    categories = db.get_categories(user.userid)
    if not categories:
        console.print("[dim]No categories yet.[/dim]")
        return

    table = Table(show_header=True, header_style="bold bright_green")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Category Name")
    for cat in categories:
        table.add_row(str(cat.cate_id), cat.cate_name)
    console.print(table)


def pick_category(user: User) -> int | None:
    """Show categories and let user pick one. Returns cate_id or None."""
    categories = db.get_categories(user.userid)
    if not categories:
        console.print("[dim]No categories available. Skipping categorization.[/dim]")
        return None

    console.print("\n[bold]Select a category:[/bold]")
    for i, cat in enumerate(categories, 1):
        console.print(f"  {i}. {cat.cate_name}")
    console.print(f"  0. No category")

    while True:
        try:
            idx = int(Prompt.ask("Enter number", default="0"))
            if idx == 0:
                return None
            if 1 <= idx <= len(categories):
                return categories[idx - 1].cate_id
            console.print(f"[bold red]Please choose between 0 and {len(categories)}![/bold red]")
        except ValueError:
            console.print("[bold red]Please enter a number![/bold red]")


# ─────────────────────────────────────────────
#  Contact helpers
# ─────────────────────────────────────────────

def input_contact_data(user: User, existing_contact=None) -> Contact:
    """Prompt user for contact data."""
    name = Prompt.ask("Full Name", default=existing_contact.contact_name if existing_contact else None)

    while True:
        phone = Prompt.ask(
            "Phone Number (+84... or 0...)",
            default=existing_contact.phone if existing_contact else None,
        )
        if validate_phone(phone):
            break
        console.print("[bold red]Error:[/bold red] Invalid phone number! Example: 0987654321 or +84987654321.")

    while True:
        email = Prompt.ask(
            "Email (leave blank if none)",
            default=existing_contact.email if existing_contact else "",
        )
        if not email or validate_email(email):
            break
        console.print("[bold red]Invalid email address![/bold red]")

    address = Prompt.ask("Address", default=existing_contact.address if existing_contact else "")

    cate_id = pick_category(user)

    contact_id = existing_contact.contact_id if existing_contact else None
    return Contact(contact_id, name, phone, email, address, user.userid, cate_id)


def display_contacts(contacts):
    """Render a list of contacts as a Rich table."""
    if not contacts:
        console.print("[bold yellow]No contacts found![/bold yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Name")
    table.add_column("Phone")
    table.add_column("Email")
    table.add_column("Address")
    table.add_column("Category")

    for c in contacts:
        table.add_row(
            str(c.contact_id),
            c.contact_name,
            c.phone,
            c.email or "",
            c.address or "",
            c.cate_name or "—",
        )
    console.print(table)


# ─────────────────────────────────────────────
#  App loop
# ─────────────────────────────────────────────

def main_loop(user: User):
    """Main menu loop after successful authentication."""
    while True:
        display_menu(user)
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3", "4", "5", "6", "7"])

        if choice == "0":
            console.print("[bold green]Logged out successfully![/bold green]")
            return  # back to auth menu

        elif choice == "1":
            console.print("\n[bold cyan]--- Add New Contact ---[/bold cyan]")
            new_contact = input_contact_data(user)
            if db.add_contact(new_contact):
                console.print("[bold green]Contact added successfully![/bold green]")
            else:
                console.print("[bold red]Phone number already exists in phonebook![/bold red]")

        elif choice == "2":
            console.print("\n[bold cyan]--- Edit Contact ---[/bold cyan]")
            try:
                contact_id = int(Prompt.ask("Enter contact ID to edit"))
                contacts = db.get_all_contacts(user.userid)
                target = next((c for c in contacts if c.contact_id == contact_id), None)

                if target:
                    updated = input_contact_data(user, target)
                    if db.update_contact(updated):
                        console.print("[bold green]Contact updated successfully![/bold green]")
                    else:
                        console.print("[bold red]Update failed (phone number may already be taken).[/bold red]")
                else:
                    console.print(f"[bold red]Contact ID {contact_id} not found.[/bold red]")
            except ValueError:
                console.print("[bold red]ID must be an integer.[/bold red]")

        elif choice == "3":
            console.print("\n[bold cyan]--- Delete Contact ---[/bold cyan]")
            try:
                contact_id = int(Prompt.ask("Enter contact ID to delete"))
                if Confirm.ask(f"Are you sure you want to delete contact ID {contact_id}?"):
                    if db.delete_contact(contact_id, user.userid):
                        console.print("[bold green]Contact deleted successfully![/bold green]")
                    else:
                        console.print(f"[bold red]Contact ID {contact_id} not found.[/bold red]")
            except ValueError:
                console.print("[bold red]ID must be an integer.[/bold red]")

        elif choice == "4":
            console.print("\n[bold cyan]--- Search Contacts ---[/bold cyan]")
            query = Prompt.ask("Enter name or phone number to search")
            results = db.search_contacts(query, user.userid)
            display_contacts(results)

        elif choice == "5":
            console.print("\n[bold cyan]--- All Contacts ---[/bold cyan]")
            contacts = db.get_all_contacts(user.userid)
            display_contacts(contacts)

        elif choice == "6":
            console.print("\n[bold cyan]--- Filter by Category ---[/bold cyan]")
            categories = db.get_categories(user.userid)
            if not categories:
                console.print("[bold yellow]No categories yet! Please create one first.[/bold yellow]")
                continue

            show_categories(user)
            try:
                cate_id = int(Prompt.ask("Enter category ID to filter"))
                results = db.filter_by_category(cate_id, user.userid)
                display_contacts(results)
            except ValueError:
                console.print("[bold red]ID must be an integer![/bold red]")

        elif choice == "7":
            category_menu(user)


def main():
    while True:
        user = auth_menu()
        main_loop(user)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program terminated![/bold red]")
        sys.exit(0)
