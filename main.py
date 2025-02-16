import subprocess
import json
import ipaddress
import argparse

def run_kubectl(cmd):
    """Runs a kubectl command and returns the output."""
    try:
        config = ["--kubeconfig", "kubeconfig"]
        cmd += config
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}\n{e.stderr}")
        return None

def get_node_cidrs():
    """Fetches node Pod CIDRs from the Kubernetes cluster."""
    cmd = ["kubectl", "get", "nodes", "-o", "json"]
    output = run_kubectl(cmd)
    if not output:
        return []

    nodes = json.loads(output)
    return [node["spec"].get("podCIDR") for node in nodes["items"] if node["spec"].get("podCIDR")]

def get_pod_ips():
    """Fetches pod IP addresses from the cluster."""
    cmd = ["kubectl", "get", "pods", "-A", "-o", "json"]
    output = run_kubectl(cmd)
    if not output:
        return []

    pods = json.loads(output)
    return [pod["status"].get("podIP") for pod in pods["items"] if pod["status"].get("podIP")]

def check_collisions(cidrs, pod_ips):
    """Check for Pod IP collisions."""
    networks = [ipaddress.ip_network(cidr, strict=False) for cidr in cidrs]
    pod_addresses = [ipaddress.ip_address(ip) for ip in pod_ips]

    collisions = {}
    for pod_ip in pod_addresses:
        matching_subnets = [net for net in networks if pod_ip in net]
        if len(matching_subnets) > 1:
            collisions[str(pod_ip)] = [str(net) for net in matching_subnets]
    
    return collisions

def load_data_from_file(file_path):
    """Loads node CIDRs and Pod IPs from a given file."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("cidrs", []), data.get("pod_ips", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to load file: {e}")
        return [], []

def main():
    parser = argparse.ArgumentParser(description="Check Pod IP conflicts in a Kubernetes cluster.")
    parser.add_argument("--check-collision", metavar="FILE", help="JSON file containing node CIDRs and Pod IPs for collision check")

    args = parser.parse_args()

    print("Fetching cluster IP information...\n")
    node_cidrs = get_node_cidrs()
    pod_ips = get_pod_ips()

    if not node_cidrs:
        print("[ERROR] No node CIDRs found. Check cluster configuration.")
        return

    print(f"All IP Network CIDRs: {node_cidrs}")
    print(f"All Pod IP Addresses: {pod_ips}")

    # Run collision check if --check-collision is provided with a file
    if args.check_collision:
        print("\n[INFO] Collision check enabled.")

        # Load data from the provided file
        print(f"[INFO] Loading data from file: {args.check_collision}")
        file_cidrs, file_pod_ips = load_data_from_file(args.check_collision)

        if not file_cidrs or not file_pod_ips:
            print("[ERROR] Invalid or empty file. Skipping collision check.")
            return

        print(f"\nChecking collisions using data from file {args.check_collision}...\n")
        conflicts = check_collisions(file_cidrs, file_pod_ips)

        if conflicts:
            print("Conflicting Pod IPs Found:")
            for pod_ip, subnets in conflicts.items():
                print(f"  - Pod IP {pod_ip} collides in subnets: {', '.join(subnets)}")
        else:
            print("No conflicts found.")

if __name__ == "__main__":
    main()
