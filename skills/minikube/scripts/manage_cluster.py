#!/usr/bin/env python3
"""
Minikube cluster management script.
Provides convenience functions for managing clusters, profiles, and resources.
"""

import subprocess
import argparse
import sys
import json

def run_command(cmd, capture=True):
    """Run shell command."""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        return None

def list_profiles():
    """List all Minikube profiles."""
    print("📋 Minikube Profiles")
    print("=" * 60)

    result = run_command("minikube profile list --output=json")
    if not result:
        print("No profiles found")
        return

    try:
        data = json.loads(result)
        profiles = data.get("valid", [])

        if not profiles:
            print("No profiles found")
            return

        for profile in profiles:
            name = profile.get("Name", "N/A")
            status = profile.get("Status", "N/A")
            driver = profile.get("Config", {}).get("Driver", "N/A")
            k8s_version = profile.get("Config", {}).get("KubernetesConfig", {}).get("KubernetesVersion", "N/A")

            print(f"\n🔹 Profile: {name}")
            print(f"   Status: {status}")
            print(f"   Driver: {driver}")
            print(f"   Kubernetes: {k8s_version}")

    except json.JSONDecodeError:
        # Fallback to plain output
        run_command("minikube profile list", capture=False)

    print("\n" + "=" * 60)

def start_profile(profile, **kwargs):
    """Start a Minikube profile."""
    print(f"🚀 Starting profile: {profile}")

    cmd = f"minikube start -p {profile}"

    if kwargs.get("memory"):
        cmd += f" --memory={kwargs['memory']}"
    if kwargs.get("cpus"):
        cmd += f" --cpus={kwargs['cpus']}"
    if kwargs.get("driver"):
        cmd += f" --driver={kwargs['driver']}"
    if kwargs.get("kubernetes_version"):
        cmd += f" --kubernetes-version={kwargs['kubernetes_version']}"

    run_command(cmd, capture=False)
    print(f"✅ Profile '{profile}' started")

def stop_profile(profile):
    """Stop a Minikube profile."""
    print(f"🛑 Stopping profile: {profile}")
    run_command(f"minikube stop -p {profile}", capture=False)
    print(f"✅ Profile '{profile}' stopped")

def delete_profile(profile):
    """Delete a Minikube profile."""
    print(f"🗑️  Deleting profile: {profile}")
    confirm = input(f"Are you sure you want to delete '{profile}'? (yes/no): ")

    if confirm.lower() == "yes":
        run_command(f"minikube delete -p {profile}", capture=False)
        print(f"✅ Profile '{profile}' deleted")
    else:
        print("❌ Deletion cancelled")

def profile_status(profile):
    """Show profile status."""
    print(f"📊 Status for profile: {profile}")
    print("=" * 50)
    run_command(f"minikube status -p {profile}", capture=False)
    print("=" * 50)

def list_addons(profile):
    """List available addons."""
    print(f"📦 Addons for profile: {profile}")
    print("=" * 60)
    run_command(f"minikube addons list -p {profile}", capture=False)
    print("=" * 60)

def enable_addon(profile, addon):
    """Enable an addon."""
    print(f"✨ Enabling addon '{addon}' for profile: {profile}")
    run_command(f"minikube addons enable {addon} -p {profile}", capture=False)
    print(f"✅ Addon '{addon}' enabled")

def disable_addon(profile, addon):
    """Disable an addon."""
    print(f"🚫 Disabling addon '{addon}' for profile: {profile}")
    run_command(f"minikube addons disable {addon} -p {profile}", capture=False)
    print(f"✅ Addon '{addon}' disabled")

def show_dashboard(profile):
    """Open Kubernetes dashboard."""
    print(f"📊 Opening dashboard for profile: {profile}")
    run_command(f"minikube dashboard -p {profile}", capture=False)

def show_services(profile):
    """List all services."""
    print(f"🌐 Services for profile: {profile}")
    print("=" * 60)
    run_command(f"minikube service list -p {profile}", capture=False)
    print("=" * 60)

def get_ip(profile):
    """Get cluster IP."""
    ip = run_command(f"minikube ip -p {profile}")
    if ip:
        print(f"🌐 Cluster IP for '{profile}': {ip}")
        return ip
    return None

def ssh_to_node(profile):
    """SSH into Minikube node."""
    print(f"🔐 SSH into profile: {profile}")
    run_command(f"minikube ssh -p {profile}", capture=False)

def show_logs(profile, follow=False):
    """Show Minikube logs."""
    print(f"📝 Logs for profile: {profile}")
    print("=" * 60)

    cmd = f"minikube logs -p {profile}"
    if follow:
        cmd += " -f"

    run_command(cmd, capture=False)

def pause_cluster(profile):
    """Pause cluster."""
    print(f"⏸️  Pausing profile: {profile}")
    run_command(f"minikube pause -p {profile}", capture=False)
    print(f"✅ Profile '{profile}' paused")

def unpause_cluster(profile):
    """Unpause cluster."""
    print(f"▶️  Unpausing profile: {profile}")
    run_command(f"minikube unpause -p {profile}", capture=False)
    print(f"✅ Profile '{profile}' unpaused")

def docker_env(profile):
    """Show Docker environment command."""
    print(f"🐳 Docker environment for profile: {profile}")
    print("=" * 60)
    print("Run the following command to configure your shell:")
    print()
    run_command(f"minikube docker-env -p {profile}", capture=False)
    print()
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="Manage Minikube clusters and profiles"
    )

    parser.add_argument(
        "--profile", "-p",
        default="minikube",
        help="Profile name (default: minikube)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List profiles
    subparsers.add_parser("list", help="List all profiles")

    # Start
    start_parser = subparsers.add_parser("start", help="Start cluster")
    start_parser.add_argument("--memory", type=int, help="Memory in MB")
    start_parser.add_argument("--cpus", type=int, help="Number of CPUs")
    start_parser.add_argument("--driver", help="Driver to use")
    start_parser.add_argument("--kubernetes-version", help="Kubernetes version")

    # Stop
    subparsers.add_parser("stop", help="Stop cluster")

    # Delete
    subparsers.add_parser("delete", help="Delete cluster")

    # Status
    subparsers.add_parser("status", help="Show cluster status")

    # Addons
    addon_parser = subparsers.add_parser("addons", help="Manage addons")
    addon_parser.add_argument("action", choices=["list", "enable", "disable"])
    addon_parser.add_argument("addon", nargs="?", help="Addon name")

    # Dashboard
    subparsers.add_parser("dashboard", help="Open dashboard")

    # Services
    subparsers.add_parser("services", help="List services")

    # IP
    subparsers.add_parser("ip", help="Get cluster IP")

    # SSH
    subparsers.add_parser("ssh", help="SSH into node")

    # Logs
    logs_parser = subparsers.add_parser("logs", help="Show logs")
    logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow logs")

    # Pause/Unpause
    subparsers.add_parser("pause", help="Pause cluster")
    subparsers.add_parser("unpause", help="Unpause cluster")

    # Docker env
    subparsers.add_parser("docker-env", help="Show Docker environment command")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    print("🎯 Minikube Cluster Manager")
    print("=" * 60)

    # Execute command
    if args.command == "list":
        list_profiles()

    elif args.command == "start":
        start_profile(
            args.profile,
            memory=args.memory,
            cpus=args.cpus,
            driver=args.driver,
            kubernetes_version=args.kubernetes_version
        )

    elif args.command == "stop":
        stop_profile(args.profile)

    elif args.command == "delete":
        delete_profile(args.profile)

    elif args.command == "status":
        profile_status(args.profile)

    elif args.command == "addons":
        if args.action == "list":
            list_addons(args.profile)
        elif args.action == "enable":
            if not args.addon:
                print("Error: addon name required")
                sys.exit(1)
            enable_addon(args.profile, args.addon)
        elif args.action == "disable":
            if not args.addon:
                print("Error: addon name required")
                sys.exit(1)
            disable_addon(args.profile, args.addon)

    elif args.command == "dashboard":
        show_dashboard(args.profile)

    elif args.command == "services":
        show_services(args.profile)

    elif args.command == "ip":
        get_ip(args.profile)

    elif args.command == "ssh":
        ssh_to_node(args.profile)

    elif args.command == "logs":
        show_logs(args.profile, args.follow)

    elif args.command == "pause":
        pause_cluster(args.profile)

    elif args.command == "unpause":
        unpause_cluster(args.profile)

    elif args.command == "docker-env":
        docker_env(args.profile)

if __name__ == "__main__":
    main()
