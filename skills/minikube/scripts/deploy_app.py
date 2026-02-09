#!/usr/bin/env python3
"""
Quick deployment script for applications to Minikube.
Supports deployment, service exposure, and ingress configuration.
"""

import os
import sys
import subprocess
import argparse
import yaml
import tempfile

def run_command(cmd, check=True):
    """Run shell command."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return None, e.stderr

def check_cluster():
    """Check if Minikube cluster is running."""
    stdout, stderr = run_command("minikube status", check=False)
    if stdout and "Running" in stdout:
        return True
    print("❌ Minikube cluster is not running!")
    print("Start it with: minikube start")
    return False

def create_deployment(name, image, replicas, port, namespace, env_vars):
    """Create Kubernetes deployment."""
    print(f"📦 Creating deployment: {name}")

    cmd = f"kubectl create deployment {name} --image={image} --replicas={replicas}"

    if namespace != "default":
        cmd += f" -n {namespace}"

    stdout, stderr = run_command(cmd, check=False)

    if stdout:
        print(f"✓ Deployment created: {name}")

        # Add environment variables if specified
        if env_vars:
            for env_var in env_vars:
                key, value = env_var.split("=", 1)
                env_cmd = f"kubectl set env deployment/{name} {key}={value}"
                if namespace != "default":
                    env_cmd += f" -n {namespace}"
                run_command(env_cmd, check=False)
                print(f"✓ Environment variable set: {key}")

        return True
    else:
        print(f"✗ Failed to create deployment: {stderr}")
        return False

def expose_service(name, port, service_type, target_port, namespace):
    """Expose deployment as service."""
    print(f"🌐 Exposing service: {name}")

    cmd = f"kubectl expose deployment {name} --type={service_type} --port={port}"

    if target_port:
        cmd += f" --target-port={target_port}"

    if namespace != "default":
        cmd += f" -n {namespace}"

    stdout, stderr = run_command(cmd, check=False)

    if stdout or "exposed" in stderr:
        print(f"✓ Service exposed: {name} ({service_type})")
        return True
    else:
        print(f"✗ Failed to expose service: {stderr}")
        return False

def create_ingress(name, host, service_name, service_port, namespace):
    """Create Ingress resource."""
    print(f"🔀 Creating ingress: {name}")

    ingress_yaml = f"""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {name}
  namespace: {namespace}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: {host}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {service_name}
            port:
              number: {service_port}
"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(ingress_yaml)
        temp_file = f.name

    try:
        stdout, stderr = run_command(f"kubectl apply -f {temp_file}", check=False)
        if stdout and "created" in stdout:
            print(f"✓ Ingress created: {name}")
            print(f"  Access at: http://{host}")
            return True
        else:
            print(f"✗ Failed to create ingress: {stderr}")
            return False
    finally:
        os.unlink(temp_file)

def enable_ingress_addon():
    """Enable Minikube ingress addon."""
    print("🔧 Enabling ingress addon...")
    stdout, stderr = run_command("minikube addons enable ingress", check=False)
    if "enabled" in stdout or "was successfully enabled" in stdout:
        print("✓ Ingress addon enabled")
        return True
    elif "already enabled" in stderr:
        print("✓ Ingress addon already enabled")
        return True
    else:
        print(f"✗ Failed to enable ingress: {stderr}")
        return False

def get_service_url(service_name, namespace):
    """Get service URL."""
    cmd = f"minikube service {service_name} --url"
    if namespace != "default":
        cmd += f" -n {namespace}"

    stdout, stderr = run_command(cmd, check=False)
    return stdout if stdout else None

def wait_for_deployment(name, namespace, timeout=120):
    """Wait for deployment to be ready."""
    print(f"⏳ Waiting for deployment to be ready...")

    cmd = f"kubectl wait --for=condition=available --timeout={timeout}s deployment/{name}"
    if namespace != "default":
        cmd += f" -n {namespace}"

    stdout, stderr = run_command(cmd, check=False)
    if stdout and "met" in stdout:
        print(f"✓ Deployment ready: {name}")
        return True
    else:
        print(f"⚠ Deployment may not be ready yet")
        return False

def show_deployment_info(name, namespace):
    """Show deployment information."""
    print(f"\n📊 Deployment Information")
    print("=" * 50)

    # Get pods
    cmd = f"kubectl get pods -l app={name}"
    if namespace != "default":
        cmd += f" -n {namespace}"

    print(f"\n🔹 Pods:")
    run_command(cmd, check=False)

    # Get service
    print(f"\n🔹 Services:")
    cmd = f"kubectl get svc {name}"
    if namespace != "default":
        cmd += f" -n {namespace}"
    run_command(cmd, check=False)

    # Get service URL
    url = get_service_url(name, namespace)
    if url:
        print(f"\n🌐 Service URL: {url}")

    print("\n" + "=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Deploy application to Minikube"
    )

    parser.add_argument(
        "name",
        help="Application/deployment name"
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Container image (e.g., nginx:latest)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=80,
        help="Service port (default: 80)"
    )

    parser.add_argument(
        "--target-port",
        type=int,
        help="Container target port (default: same as --port)"
    )

    parser.add_argument(
        "--replicas",
        type=int,
        default=1,
        help="Number of replicas (default: 1)"
    )

    parser.add_argument(
        "--namespace", "-n",
        default="default",
        help="Kubernetes namespace (default: default)"
    )

    parser.add_argument(
        "--service-type",
        choices=["ClusterIP", "NodePort", "LoadBalancer"],
        default="NodePort",
        help="Service type (default: NodePort)"
    )

    parser.add_argument(
        "--ingress",
        action="store_true",
        help="Create ingress resource"
    )

    parser.add_argument(
        "--host",
        help="Ingress hostname (required if --ingress)"
    )

    parser.add_argument(
        "--env",
        action="append",
        help="Environment variables (KEY=VALUE, can be used multiple times)"
    )

    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for deployment to be ready"
    )

    parser.add_argument(
        "--open",
        action="store_true",
        help="Open service in browser after deployment"
    )

    args = parser.parse_args()

    print("🚀 Minikube Deployment Script")
    print("=" * 50)

    # Check cluster
    if not check_cluster():
        sys.exit(1)

    # Create namespace if not default
    if args.namespace != "default":
        print(f"🔧 Creating namespace: {args.namespace}")
        run_command(f"kubectl create namespace {args.namespace}", check=False)

    # Create deployment
    if not create_deployment(
        args.name,
        args.image,
        args.replicas,
        args.port,
        args.namespace,
        args.env
    ):
        sys.exit(1)

    # Wait for deployment
    if args.wait:
        wait_for_deployment(args.name, args.namespace)

    # Expose service
    if not expose_service(
        args.name,
        args.port,
        args.service_type,
        args.target_port,
        args.namespace
    ):
        sys.exit(1)

    # Create ingress if requested
    if args.ingress:
        if not args.host:
            print("❌ --host is required when using --ingress")
            sys.exit(1)

        enable_ingress_addon()
        create_ingress(
            f"{args.name}-ingress",
            args.host,
            args.name,
            args.port,
            args.namespace
        )

    # Show deployment info
    show_deployment_info(args.name, args.namespace)

    # Open in browser
    if args.open:
        print("\n🌐 Opening service in browser...")
        cmd = f"minikube service {args.name}"
        if args.namespace != "default":
            cmd += f" -n {args.namespace}"
        run_command(cmd, check=False)

    print("\n✅ Deployment complete!")
    print(f"\nUseful commands:")
    print(f"  • View logs: kubectl logs -l app={args.name} -n {args.namespace}")
    print(f"  • Scale: kubectl scale deployment/{args.name} --replicas=3 -n {args.namespace}")
    print(f"  • Delete: kubectl delete deployment,service {args.name} -n {args.namespace}")
    print(f"  • Access: minikube service {args.name} -n {args.namespace}")

if __name__ == "__main__":
    main()
