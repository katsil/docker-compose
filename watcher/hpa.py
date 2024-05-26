import requests
import os
import subprocess

PROMETHEUS_URL = "http://localhost:10090/api/v1/query"
CPU_QUERY = 'sum(rate(container_cpu_usage_seconds_total{container_label_com_docker_compose_service="flask-app"}[1m]))'
MEMORY_QUERY = 'sum(container_memory_usage_bytes{container_label_com_docker_compose_service="flask-app"})'
CPU_THRESHOLD = 0.0004 # Adjust the CPU threshold as needed
MEMORY_THRESHOLD = 500 * 1024 * 1024  # Adjust the memory threshold as needed (in bytes)
MAX_REPLICAS = 5
MIN_REPLICAS = 1

def get_prometheus_metric(query):
    response = requests.get(PROMETHEUS_URL, params={'query': query})
    results = response.json()['data']['result']
    if results:
        print(float(results[0]['value'][1]))
        return float(results[0]['value'][1])
    return 0.0

def scale_service(service_name, replicas):
    os.system(f'docker-compose up --scale {service_name}={replicas} -d')
    os.system("docker-compose exec -T nginx nginx -s reload")
    print("Nginx reloaded.")

def main():
    cpu_usage = get_prometheus_metric(CPU_QUERY)
    memory_usage = get_prometheus_metric(MEMORY_QUERY)

    current_replicas = int(os.popen('docker-compose ps -q flask-app | wc -l').read().strip())
    print(current_replicas)
    if cpu_usage > CPU_THRESHOLD or memory_usage > MEMORY_THRESHOLD:
        if current_replicas < MAX_REPLICAS:
            new_replicas = current_replicas + 1
            scale_service('flask-app', new_replicas)
            print(f"Scaled up to {new_replicas} replicas due to high load.")
    elif cpu_usage < (CPU_THRESHOLD / 2) and memory_usage < (MEMORY_THRESHOLD / 2):
        if current_replicas > MIN_REPLICAS:
            new_replicas = current_replicas - 1
            scale_service('flask-app', new_replicas)
            print(f"Scaled down to {new_replicas} replicas due to low load.")

if __name__ == "__main__":
    main()