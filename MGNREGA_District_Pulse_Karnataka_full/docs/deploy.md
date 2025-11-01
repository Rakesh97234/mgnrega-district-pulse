# Deployment Guide (EC2 Ubuntu 22.04)

## Prerequisites
- EC2 Ubuntu 22.04 instance (2 vCPU, 4GB RAM)
- SSH access
- Domain (optional)

## 1) Install Docker & Docker Compose
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git golang-go
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker

## 2) Clone repo on EC2
git clone <your-repo> && cd MGNREGA_District_Pulse_Karnataka_full/infra

## 3) Place Karnataka GeoJSON
Put karnataka_districts.geojson into infra/data/

## 4) Start containers (dev)
docker compose up -d --build

## 5) Load DB schema
# Enter postgres container and run schema
docker exec -it $(docker ps -q -f ancestor=postgis/postgis:13-3.3) bash -c "psql -U postgres -d mgnrega -f /schema/schema.sql"

## 6) Load districts (use load_districts.sh)
./load_districts.sh data/karnataka_districts.geojson

## 7) Run ETL (recommended via systemd timer)
# Option A: Run ETL once in container
docker compose run --rm etl
# Option B (recommended): enable systemd timer on host (files provided in infra/systemd)

## 8) Configure Nginx & SSL
If you have a domain, run certbot to obtain certificate and enable HTTPS.

## 9) Visit the app
http://<EC2_IP> (or https://yourdomain)
