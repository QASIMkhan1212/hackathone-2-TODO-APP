# Docker Networking Reference

Complete guide to Docker networking for container communication and security.

## Network Types

### Bridge Network (Default)

```yaml
# Default bridge - containers can communicate via IP
services:
  app:
    networks:
      - default

# Custom bridge - containers communicate via service name
services:
  app:
    networks:
      - mynetwork

networks:
  mynetwork:
    driver: bridge
```

### Host Network

```yaml
# Container shares host's network stack
services:
  app:
    network_mode: host
    # No port mapping needed - uses host ports directly
```

### None Network

```yaml
# No network access
services:
  isolated:
    network_mode: none
```

### Container Network

```yaml
# Share another container's network
services:
  sidecar:
    network_mode: service:app
```

## Network Configuration

### Basic Network Definition

```yaml
networks:
  frontend:
    driver: bridge

  backend:
    driver: bridge
    internal: true  # No external access

  external:
    external: true  # Use pre-existing network
    name: my-external-network
```

### Advanced Configuration

```yaml
networks:
  custom:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: custom_bridge
      com.docker.network.bridge.enable_ip_masquerade: "true"

    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          ip_range: 172.28.5.0/24
          gateway: 172.28.5.254
          aux_addresses:
            host1: 172.28.1.5
            host2: 172.28.1.6

    labels:
      - "com.example.description=Custom network"
```

## Service Network Configuration

### Multiple Networks

```yaml
services:
  app:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend  # Only accessible from backend

  nginx:
    networks:
      - frontend  # Public facing
```

### Network Aliases

```yaml
services:
  api:
    networks:
      frontend:
        aliases:
          - api.local
          - api-service
      backend:
        aliases:
          - internal-api
```

### Static IP Assignment

```yaml
services:
  app:
    networks:
      mynetwork:
        ipv4_address: 172.28.0.10
        ipv6_address: 2001:db8::10

networks:
  mynetwork:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
        - subnet: 2001:db8::/64
```

### Priority

```yaml
services:
  app:
    networks:
      frontend:
        priority: 1000  # Higher = preferred for default route
      backend:
        priority: 100
```

## DNS Configuration

### Custom DNS

```yaml
services:
  app:
    dns:
      - 8.8.8.8
      - 8.8.4.4
    dns_search:
      - example.com
    dns_opt:
      - timeout:3
      - attempts:3
```

### Extra Hosts

```yaml
services:
  app:
    extra_hosts:
      - "host.docker.internal:host-gateway"
      - "db.local:172.28.0.5"
      - "api.external:192.168.1.100"
```

## Port Configuration

### Port Mapping

```yaml
services:
  app:
    ports:
      # HOST:CONTAINER
      - "8080:8000"

      # Bind to specific interface
      - "127.0.0.1:8080:8000"

      # Random host port
      - "8000"

      # Port range
      - "8000-8010:8000-8010"

      # UDP
      - "5000:5000/udp"

      # Long syntax
      - target: 8000
        published: 8080
        protocol: tcp
        mode: host
```

### Expose (Internal Only)

```yaml
services:
  app:
    expose:
      - "8000"
      - "9000"
    # These ports are only accessible to linked services
```

## Network Patterns

### Frontend/Backend Isolation

```yaml
services:
  # Public facing
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - frontend
    depends_on:
      - app

  # Application tier
  app:
    build: .
    networks:
      - frontend
      - backend
    depends_on:
      - db

  # Database tier (isolated)
  db:
    image: postgres:16-alpine
    networks:
      - backend
    # No ports exposed to host

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

### Service Mesh Pattern

```yaml
services:
  # API Gateway
  gateway:
    image: kong:latest
    ports:
      - "8000:8000"
      - "8443:8443"
    networks:
      - public
      - mesh

  # Service A
  service-a:
    build: ./services/a
    networks:
      - mesh
    labels:
      - "mesh.service=service-a"
      - "mesh.port=8000"

  # Service B
  service-b:
    build: ./services/b
    networks:
      - mesh
    labels:
      - "mesh.service=service-b"
      - "mesh.port=8000"

  # Service Discovery
  consul:
    image: consul:latest
    networks:
      - mesh
    ports:
      - "8500:8500"

networks:
  public:
    driver: bridge
  mesh:
    driver: bridge
    internal: true
```

### Database Per Service

```yaml
services:
  users-service:
    build: ./users
    networks:
      - api
      - users-db-net

  users-db:
    image: postgres:16-alpine
    networks:
      - users-db-net  # Only users-service can access

  orders-service:
    build: ./orders
    networks:
      - api
      - orders-db-net

  orders-db:
    image: postgres:16-alpine
    networks:
      - orders-db-net  # Only orders-service can access

  gateway:
    build: ./gateway
    ports:
      - "80:80"
    networks:
      - api

networks:
  api:
    driver: bridge
  users-db-net:
    driver: bridge
    internal: true
  orders-db-net:
    driver: bridge
    internal: true
```

## Network Commands

### Inspect Networks

```bash
# List networks
docker network ls

# Inspect network
docker network inspect mynetwork

# View container's network
docker inspect --format='{{json .NetworkSettings.Networks}}' container_name
```

### Manage Networks

```bash
# Create network
docker network create mynetwork
docker network create --driver bridge --subnet 172.28.0.0/16 mynetwork

# Connect/disconnect container
docker network connect mynetwork container_name
docker network disconnect mynetwork container_name

# Remove network
docker network rm mynetwork

# Remove unused networks
docker network prune
```

### Debug Networking

```bash
# Check connectivity
docker exec app ping db
docker exec app nslookup db

# View routing
docker exec app ip route

# Check ports
docker port container_name
docker exec app netstat -tlnp
```

## Security Best Practices

### Network Isolation

```yaml
networks:
  # Public-facing only
  frontend:
    driver: bridge

  # Internal services
  backend:
    driver: bridge
    internal: true  # No external access

  # Highly sensitive
  secure:
    driver: bridge
    internal: true
    driver_opts:
      encrypted: "true"  # Encrypt traffic (Swarm mode)
```

### Limit Container Network

```yaml
services:
  app:
    cap_drop:
      - NET_RAW  # Prevent raw socket access
    sysctls:
      - net.ipv4.ip_forward=0
```

### Network Policies

```bash
# At Docker daemon level
# /etc/docker/daemon.json
{
  "icc": false,  # Disable inter-container communication
  "iptables": true
}
```

## Troubleshooting

### Common Issues

```bash
# Container can't resolve service name
# Check if on same network
docker network inspect mynetwork | grep -A 20 Containers

# Port already in use
lsof -i :8000
docker ps --filter "publish=8000"

# Container can't reach external
# Check DNS
docker exec app cat /etc/resolv.conf
docker exec app ping 8.8.8.8

# Firewall blocking
# Check iptables rules
sudo iptables -L -n | grep DOCKER
```

### Network Debugging Container

```yaml
services:
  debug:
    image: nicolaka/netshoot
    network_mode: service:app  # Share app's network
    command: sleep infinity
    # Then: docker-compose exec debug <command>
    # Available tools: ping, curl, dig, nslookup, tcpdump, iftop
```
