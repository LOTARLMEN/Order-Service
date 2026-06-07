import subprocess
import sys
import os

KUBECONFIG = r"C:\Users\VALERIY\.kube\order-service"
NAMESPACE = "student-lotarlmen-order-service"
CONTEXT = "student-lotarlmen-order-service-context"

def run_kubectl(args):
    env = os.environ.copy()
    env["KUBECONFIG"] = KUBECONFIG
    cmd = ["kubectl", "--context", CONTEXT, "--namespace", NAMESPACE] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_logs(search_term, tail=100):
    # Find pods
    output = run_kubectl(["get", "pods", "--no-headers"])
    lines = output.strip().split("\n")
    pods = [line.split()[0] for line in lines if search_term in line]
    
    if not pods:
        print(f"No pods found matching '{search_term}'")
        return

    # Use the first pod found
    pod_name = pods[0]
    print(f"--- Logs for pod: {pod_name} ---")
    logs = run_kubectl(["logs", pod_name, f"--tail={tail}"])
    print(logs)

def list_pods():
    output = run_kubectl(["get", "pods"])
    print(output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python k8s_ops.py <cmd> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "logs":
        term = sys.argv[2] if len(sys.argv) > 2 else ""
        tail = sys.argv[3] if len(sys.argv) > 3 else 100
        get_logs(term, tail)
    elif cmd == "pods":
        list_pods()
    else:
        print(f"Unknown command: {cmd}")
