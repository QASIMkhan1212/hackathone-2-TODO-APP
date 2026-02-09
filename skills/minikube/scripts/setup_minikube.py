#!/usr/bin/env python3
"""
Minikube setup and configuration script.
Automates installation verification and cluster setup.
"""

import os
import sys
import subprocess
import platform
import argparse

def run_command(cmd, capture=True, check=True):
    """Run shell command and return output."""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return None
    except subprocess.CalledProcessError as e:
        if check:
            print(f"Error running command: {cmd}")
            print(f"Error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        return None

def check_prerequisite(command, name):
    """Check if a prerequisite is installed."""
    result = run_command(f"command -v {command} || where {command}", check=False)
    if result:
        version = run_command(f"{command} --version 2>&1 | head -1", check=False)
        print(f"✓ {name} is installed: {version}")
        return True
    else:
        print(f"✗ {name} is not installed")
        return False

def check_prerequisites():
    """Check all prerequisites."""
    print("Checking prerequisites...")
    print("-" * 50)

    checks = {
        "minikube": check_prerequisite("minikube", "Minikube"),
        "kubectl": check_prerequisite("kubectl", "kubectl"),
        "docker": check_prerequisite("docker", "Docker")
    }

    print("-" * 50)

    if not checks["minikube"]:
        print("\n❌ Minikube is not installed!")
        print("Install from: https://minikube.sigs.k8s.io/docs/start/")
        return False

    if not checks["docker"]:
        print("\n⚠ Docker is not installed (recommended)")
        print("Install from: https://www.docker.com/products/docker-desktop")
        print("Note: VirtualBox or other drivers can be used as alternatives")

    return True

def get_system_resources():
    """Get available system resources."""
    try:
        # Get CPU count
        cpu_count = os.cpu_count() or 2

        # Get available memory (simplified)
        if platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                mem_kb = int(f.readline().split()[1])
                mem_mb = mem_kb // 1024
        else:
            # Default for Windows/macOS
            mem_mb = 8192

        return cpu_count, mem_mb
    except:
        return 2, 4096

def configure_cluster(profile, memory, cpus, disk_size, k8s_version, driver):
    """Configure and start Minikube cluster."""
    print(f"\n🚀 Starting Minikube cluster: {profile}")
    print("-" * 50)
    print(f"Profile: {profile}")
    print(f"Memory: {memory}MB")
    print(f"CPUs: {cpus}")
    print(f"Disk: {disk_size}")
    print(f"Kubernetes: {k8s_version}")
    print(f"Driver: {driver}")
    print("-" * 50)

    # Build start command
    cmd_parts = [
        "minikube", "start",
        f"-p {profile}",
        f"--memory={memory}",
        f"--cpus={cpus}",
        f"--disk-size={disk_size}",
    ]

    if k8s_version:
        cmd_parts.append(f"--kubernetes-version={k8s_version}")

    if driver:
        cmd_parts.append(f"--driver={driver}")

    cmd = " ".join(cmd_parts)

    print(f"\nExecuting: {cmd}\n")
    result = run_command(cmd, capture=False, check=False)

    # Check if successful
    status = run_command(f"minikube status -p {profile}", check=False)
    if status and "Running" in status:
        print(f"\n✅ Cluster '{profile}' started successfully!")
        return True
    else:
        print(f"\n❌ Failed to start cluster '{profile}'")
        return False

def enable_addons(profile, addons):
    """Enable Minikube addons."""
    if not addons:
        return

    print(f"\n📦 Enabling addons for profile: {profile}")
    print("-" * 50)

    for addon in addons:
        print(f"Enabling {addon}...")
        result = run_command(
            f"minikube addons enable {addon} -p {profile}",
            capture=False,
            check=False
        )

    print("✅ Addons enabled")

def show_cluster_info(profile):
    """Display cluster information."""
    print(f"\n📊 Cluster Information: {profile}")
    print("=" * 50)

    # Status
    print("\n🔍 Status:")
    run_command(f"minikube status -p {profile}", capture=False, check=False)

    # IP
    ip = run_command(f"minikube ip -p {profile}", check=False)
    if ip:
        print(f"\n🌐 Cluster IP: {ip}")

    # Profile info
    print(f"\n📋 Profile: {profile}")
    run_command(f"minikube profile {profile}", capture=False, check=False)

    # Kubectl context
    print("\n🔧 kubectl context set to:")
    run_command("kubectl config current-context", capture=False, check=False)

    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print(f"  • Access dashboard: minikube dashboard -p {profile}")
    print(f"  • View services: minikube service list -p {profile}")
    print(f"  • SSH into node: minikube ssh -p {profile}")
    print(f"  • Stop cluster: minikube stop -p {profile}")
    print(f"  • Delete cluster: minikube delete -p {profile}")

def main():
    parser = argparse.ArgumentParser(
        description="Setup and configure Minikube cluster"
    )

    parser.add_argument(
        "--profile", "-p",
        default="minikube",
        help="Cluster profile name (default: minikube)"
    )

    parser.add_argument(
        "--memory",
        type=int,
        default=4096,
        help="Memory allocation in MB (default: 4096)"
    )

    parser.add_argument(
        "--cpus",
        type=int,
        default=2,
        help="CPU allocation (default: 2)"
    )

    parser.add_argument(
        "--disk-size",
        default="20g",
        help="Disk size (default: 20g)"
    )

    parser.add_argument(
        "--kubernetes-version",
        help="Kubernetes version (e.g., v1.28.0)"
    )

    parser.add_argument(
        "--driver",
        choices=["docker", "virtualbox", "kvm2", "hyperv", "vmware"],
        help="Driver to use"
    )

    parser.add_argument(
        "--addons",
        nargs="+",
        default=["dashboard", "metrics-server"],
        help="Addons to enable (default: dashboard metrics-server)"
    )

    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip prerequisite checks"
    )

    parser.add_argument(
        "--no-addons",
        action="store_true",
        help="Don't enable any addons"
    )

    args = parser.parse_args()

    print("🎯 Minikube Setup Script")
    print("=" * 50)

    # Check prerequisites
    if not args.skip_check:
        if not check_prerequisites():
            sys.exit(1)

    # Show system resources
    cpus, mem_mb = get_system_resources()
    print(f"\n💻 System Resources:")
    print(f"  Available CPUs: {cpus}")
    print(f"  Available Memory: ~{mem_mb}MB")

    # Configure cluster
    success = configure_cluster(
        args.profile,
        args.memory,
        args.cpus,
        args.disk_size,
        args.kubernetes_version,
        args.driver
    )

    if not success:
        sys.exit(1)

    # Enable addons
    if not args.no_addons:
        enable_addons(args.profile, args.addons)

    # Show cluster info
    show_cluster_info(args.profile)

if __name__ == "__main__":
    main()
