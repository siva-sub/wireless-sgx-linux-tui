"""CLI commands for managing Wireless@SGx"""

import click
import sys
from .storage import SecureStorage
from .network import NetworkManager, NetworkConfigError
from textual.widgets import Button, Label, Static
from textual.containers import Container, Vertical


@click.group()
def cli():
    """Wireless@SGx management commands"""
    pass


@cli.command()
def show():
    """Show saved credentials"""
    storage = SecureStorage()
    creds = storage.get_credentials()
    
    if not creds:
        click.echo("No saved credentials found.")
        return
    
    click.echo("\n🔐 Saved Wireless@SGx Credentials:")
    click.echo("─" * 40)
    click.echo(f"Username: {creds['username']}")
    click.echo(f"Password: {'*' * len(creds['password'])}")
    click.echo(f"ISP: {creds['isp']}")
    click.echo("─" * 40)
    
    # Check if auto-connect is enabled
    network = NetworkManager()
    try:
        network_manager = network.detect_network_manager()
        if network_manager == "networkmanager":
            # Check if connection exists and has autoconnect
            import subprocess
            result = subprocess.run(
                ["nmcli", "-t", "-f", "connection.autoconnect", "con", "show", "Wireless@SGx"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip() == "yes":
                click.echo("✅ Auto-connect: Enabled")
            else:
                click.echo("❌ Auto-connect: Disabled")
        else:
            click.echo("ℹ️  Auto-connect: Available for NetworkManager only")
    except:
        pass
    
    click.echo("\nOptions:")
    click.echo("  wirelesssgx connect     - Connect using saved credentials")
    click.echo("  wirelesssgx autoconnect - Enable auto-connect")
    click.echo("  wirelesssgx forget      - Delete saved credentials")


@cli.command()
def connect():
    """Connect using saved credentials"""
    storage = SecureStorage()
    creds = storage.get_credentials()
    
    if not creds:
        click.echo("❌ No saved credentials found. Run 'wirelesssgx' to set up.")
        return 1
    
    network = NetworkManager()
    click.echo(f"🔄 Connecting to Wireless@SGx using saved credentials...")
    
    try:
        # Configure network
        if network.configure_network(creds['username'], creds['password']):
            click.echo("✅ Network configured successfully!")
            
            # Try to connect immediately with NetworkManager
            try:
                import subprocess
                subprocess.run(
                    ["nmcli", "connection", "up", "Wireless@SGx"],
                    capture_output=True,
                    check=True
                )
                click.echo("✅ Connected to Wireless@SGx!")
            except:
                click.echo("ℹ️  Network configured. Connection will be established when in range.")
        else:
            click.echo("❌ Failed to configure network")
            return 1
            
    except NetworkConfigError as e:
        click.echo(f"❌ Error: {str(e)}")
        return 1


@cli.command()
def autoconnect():
    """Enable auto-connect for Wireless@SGx"""
    storage = SecureStorage()
    creds = storage.get_credentials()
    
    if not creds:
        click.echo("❌ No saved credentials found. Run 'wirelesssgx' to set up.")
        return 1
    
    network = NetworkManager()
    
    try:
        network_manager = network.detect_network_manager()
        
        if network_manager != "networkmanager":
            click.echo("❌ Auto-connect is only available with NetworkManager")
            click.echo("ℹ️  Your system uses: " + network_manager)
            return 1
        
        # First ensure the connection is configured
        click.echo("🔄 Configuring auto-connect for Wireless@SGx...")
        
        if network.configure_network(creds['username'], creds['password']):
            # The connection is created with autoconnect=yes by default
            click.echo("✅ Auto-connect enabled!")
            click.echo("\nWireless@SGx will now connect automatically when in range.")
            click.echo("To disable auto-connect, run: nmcli connection modify Wireless@SGx connection.autoconnect no")
        else:
            click.echo("❌ Failed to enable auto-connect")
            return 1
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        return 1


@cli.command()
def forget():
    """Delete saved credentials"""
    storage = SecureStorage()
    
    if not storage.has_credentials():
        click.echo("No saved credentials to delete.")
        return
    
    # Confirm deletion
    if click.confirm("Are you sure you want to delete saved credentials?"):
        if storage.delete_credentials():
            click.echo("✅ Credentials deleted successfully")
            
            # Also try to remove network configuration
            try:
                import subprocess
                subprocess.run(
                    ["nmcli", "connection", "delete", "Wireless@SGx"],
                    capture_output=True
                )
            except:
                pass
        else:
            click.echo("❌ Failed to delete credentials")
            return 1
    else:
        click.echo("Cancelled.")


@cli.command()
def status():
    """Check connection status"""
    network = NetworkManager()
    
    if network.test_connection():
        click.echo("✅ Connected to Wireless@SGx")
        
        # Show connection details if using NetworkManager
        try:
            import subprocess
            result = subprocess.run(
                ["nmcli", "-t", "-f", "IP4.ADDRESS,GENERAL.STATE", "con", "show", "Wireless@SGx"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if "IP4.ADDRESS" in line:
                        ip = line.split(':')[1]
                        click.echo(f"IP Address: {ip}")
                    elif "GENERAL.STATE" in line:
                        state = line.split(':')[1]
                        click.echo(f"State: {state}")
        except:
            pass
    else:
        click.echo("❌ Not connected to Wireless@SGx")
        
        storage = SecureStorage()
        if storage.has_credentials():
            click.echo("\nYou have saved credentials. Try:")
            click.echo("  wirelesssgx connect - to connect now")
        else:
            click.echo("\nNo saved credentials. Run 'wirelesssgx' to set up.")


if __name__ == "__main__":
    cli()