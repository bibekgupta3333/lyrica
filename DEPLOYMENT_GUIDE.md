# Deployment Guide
## Lyrica - Agentic Song Lyrics Generator

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [AWS Infrastructure Setup](#aws-infrastructure-setup)
5. [Terraform Configuration](#terraform-configuration)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Helm Charts](#helm-charts)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Monitoring & Logging](#monitoring--logging)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools & Versions

```bash
# System Requirements
- OS: Linux/macOS/Windows with WSL2
- RAM: 16GB minimum (32GB recommended)
- Disk: 50GB free space
- CPU: 4 cores minimum (8 cores recommended)

# Required Software
docker --version              # Docker 24.0+
docker-compose --version      # Docker Compose 2.20+
kubectl version --client      # Kubernetes CLI 1.28+
helm version                  # Helm 3.12+
terraform --version           # Terraform 1.6+
aws --version                 # AWS CLI 2.13+
python --version              # Python 3.11+
node --version                # Node.js 18+
ollama --version              # Ollama 0.1.17+
```

### AWS Account Setup

```bash
# 1. Create AWS Account
# Visit: https://aws.amazon.com/

# 2. Create IAM User with Administrator Access
# Navigate to IAM -> Users -> Add User
# Attach policy: AdministratorAccess

# 3. Configure AWS CLI
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json

# 4. Verify configuration
aws sts get-caller-identity
```

---

## Local Development Setup

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/lyrica.git
cd lyrica

# Verify structure
tree -L 2
```

### Step 2: Install Ollama & Models

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# For macOS with Homebrew
brew install ollama

# Start Ollama service
ollama serve &

# Pull required models
ollama pull llama3           # 7B model (~4GB)
ollama pull mistral          # 7B model (~4GB)

# Verify installation
ollama list

# Test model
ollama run llama3 "Hello, write a short verse"
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
# Application
APP_NAME=Lyrica
APP_VERSION=1.0.0
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lyrica_dev
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379/0

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION=lyrics_embeddings

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Security
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:19006"]

# Logging
LOG_LEVEL=INFO
EOF

# Run database migrations
alembic upgrade head

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test the API
curl http://localhost:8000/api/v1/health
```

### Step 4: Frontend Web Setup

```bash
# Navigate to web directory
cd ../web

# Install dependencies
npm install
# or
yarn install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_APP_NAME=Lyrica
NEXT_PUBLIC_ENVIRONMENT=development
EOF

# Run development server
npm run dev
# or
yarn dev

# Open browser
# http://localhost:3000
```

### Step 5: Frontend Mobile Setup

```bash
# Navigate to mobile directory
cd ../mobile

# Install dependencies
npm install
# or
yarn install

# Create .env file
cat > .env << EOF
API_URL=http://localhost:8000/api/v1
WS_URL=ws://localhost:8000/ws
APP_NAME=Lyrica
ENVIRONMENT=development
EOF

# Start Metro bundler
npx expo start

# Run on iOS
npx expo run:ios

# Run on Android
npx expo run:android
```

---

## Docker Deployment

### Project Docker Structure

```
lyrica/
├── backend/
│   ├── Dockerfile
│   └── docker-compose.yml
├── web/
│   └── Dockerfile
├── mobile/
│   └── Dockerfile
└── docker-compose.yml (root)
```

### Step 1: Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Web Dockerfile

```dockerfile
# web/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Install dependencies
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build Next.js
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### Step 3: Ollama Dockerfile

```dockerfile
# ollama/Dockerfile
FROM ollama/ollama:latest

# Copy model pull script
COPY pull-models.sh /pull-models.sh
RUN chmod +x /pull-models.sh

# Pull models at build time (optional, can be done at runtime)
# RUN /pull-models.sh

EXPOSE 11434

CMD ["ollama", "serve"]
```

```bash
# ollama/pull-models.sh
#!/bin/bash
set -e

echo "Pulling Ollama models..."

ollama pull llama3
ollama pull mistral

echo "Models pulled successfully!"
```

### Step 4: Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.9'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: lyrica-postgres
    environment:
      POSTGRES_DB: lyrica_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - lyrica-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: lyrica-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - lyrica-network

  # ChromaDB Vector Store
  chromadb:
    image: chromadb/chroma:latest
    container_name: lyrica-chromadb
    environment:
      CHROMA_SERVER_HOST: 0.0.0.0
      CHROMA_SERVER_HTTP_PORT: 8000
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - lyrica-network

  # Ollama Service
  ollama:
    build:
      context: ./ollama
      dockerfile: Dockerfile
    container_name: lyrica-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      OLLAMA_HOST: 0.0.0.0
    # Uncomment for GPU support
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]
    networks:
      - lyrica-network

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: lyrica-backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/lyrica_dev
      REDIS_URL: redis://redis:6379/0
      OLLAMA_BASE_URL: http://ollama:11434
      CHROMADB_HOST: chromadb
      CHROMADB_PORT: 8000
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_cache:/app/.cache
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      chromadb:
        condition: service_healthy
      ollama:
        condition: service_started
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - lyrica-network

  # Next.js Frontend
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    container_name: lyrica-web
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
      NEXT_PUBLIC_WS_URL: ws://localhost:8000/ws
    ports:
      - "3000:3000"
    volumes:
      - ./web:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    networks:
      - lyrica-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  chromadb_data:
    driver: local
  ollama_data:
    driver: local
  backend_cache:
    driver: local

networks:
  lyrica-network:
    driver: bridge
```

### Step 5: Run Docker Compose

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Stop services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Run specific service
docker-compose up postgres redis -d

# Execute command in container
docker-compose exec backend python --version
docker-compose exec postgres psql -U postgres -d lyrica_dev

# Scale services
docker-compose up --scale backend=3
```

---

## AWS Infrastructure Setup

### Architecture Overview

```
AWS Account
├── VPC (10.0.0.0/16)
│   ├── Public Subnets (10.0.1.0/24, 10.0.2.0/24)
│   │   ├── NAT Gateway
│   │   └── Application Load Balancer
│   └── Private Subnets (10.0.10.0/24, 10.0.11.0/24)
│       ├── EKS Worker Nodes
│       ├── RDS PostgreSQL
│       └── ElastiCache Redis
├── EKS Cluster
│   ├── Node Group (t3.large, 2-10 nodes)
│   └── Fargate Profile (optional)
├── RDS PostgreSQL (db.t3.medium)
├── ElastiCache Redis (cache.t3.micro)
├── S3 Buckets
│   ├── Static Assets
│   ├── Backups
│   └── Terraform State
├── ECR (Container Registry)
├── CloudFront (CDN)
├── Route53 (DNS)
└── CloudWatch (Monitoring)
```

### Step 1: Create S3 Bucket for Terraform State

```bash
# Create S3 bucket for Terraform state
export AWS_REGION=us-east-1
export PROJECT_NAME=lyrica
export STATE_BUCKET="${PROJECT_NAME}-terraform-state"

aws s3 mb s3://${STATE_BUCKET} --region ${AWS_REGION}

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ${STATE_BUCKET} \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ${STATE_BUCKET} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name ${PROJECT_NAME}-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region ${AWS_REGION}
```

---

## Terraform Configuration

### Project Structure

```
infrastructure/
├── terraform/
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── terraform.tfvars
│   │   │   └── backend.tf
│   │   ├── staging/
│   │   └── production/
│   ├── modules/
│   │   ├── vpc/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── eks/
│   │   ├── rds/
│   │   ├── elasticache/
│   │   ├── s3/
│   │   └── ecr/
│   └── scripts/
│       ├── apply.sh
│       └── destroy.sh
```

### Step 1: Backend Configuration

```hcl
# infrastructure/terraform/environments/production/backend.tf
terraform {
  backend "s3" {
    bucket         = "lyrica-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "lyrica-terraform-locks"
  }

  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}
```

### Step 2: VPC Module

```hcl
# infrastructure/terraform/modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-vpc"
    }
  )
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name                                           = "${var.project_name}-public-${count.index + 1}"
      "kubernetes.io/role/elb"                      = "1"
      "kubernetes.io/cluster/${var.cluster_name}"   = "shared"
    }
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.tags,
    {
      Name                                           = "${var.project_name}-private-${count.index + 1}"
      "kubernetes.io/role/internal-elb"             = "1"
      "kubernetes.io/cluster/${var.cluster_name}"   = "shared"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-igw"
    }
  )
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  count  = length(var.public_subnet_cidrs)
  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-nat-eip-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  count         = length(var.public_subnet_cidrs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-nat-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-public-rt"
    }
  )
}

# Private Route Tables
resource "aws_route_table" "private" {
  count  = length(var.private_subnet_cidrs)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-private-rt-${count.index + 1}"
    }
  )
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = length(var.private_subnet_cidrs)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Groups
resource "aws_security_group" "eks_cluster" {
  name_prefix = "${var.project_name}-eks-cluster-"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-eks-cluster-sg"
    }
  )
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-rds-sg"
    }
  )
}
```

```hcl
# infrastructure/terraform/modules/vpc/variables.tf
variable "project_name" {
  description = "Project name"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
```

```hcl
# infrastructure/terraform/modules/vpc/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "eks_cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = aws_security_group.eks_cluster.id
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}
```

### Step 3: EKS Module

```hcl
# infrastructure/terraform/modules/eks/main.tf
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.public_access_cidrs
    security_group_ids      = [var.cluster_security_group_id]
  }

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]

  tags = var.tags

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
    aws_iam_role_policy_attachment.vpc_resource_controller,
  ]
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.node_group.arn
  subnet_ids      = var.private_subnet_ids

  instance_types = var.node_instance_types
  capacity_type  = var.capacity_type

  scaling_config {
    desired_size = var.desired_size
    max_size     = var.max_size
    min_size     = var.min_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    Environment = var.environment
  }

  tags = var.tags

  depends_on = [
    aws_iam_role_policy_attachment.node_group_policy,
    aws_iam_role_policy_attachment.cni_policy,
    aws_iam_role_policy_attachment.container_registry_policy,
  ]

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

# IAM Role for EKS Cluster
resource "aws_iam_role" "cluster" {
  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster.name
}

resource "aws_iam_role_policy_attachment" "vpc_resource_controller" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.cluster.name
}

# IAM Role for EKS Node Group
resource "aws_iam_role" "node_group" {
  name = "${var.cluster_name}-node-group-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "node_group_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.node_group.name
}

resource "aws_iam_role_policy_attachment" "cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.node_group.name
}

resource "aws_iam_role_policy_attachment" "container_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.node_group.name
}

# OIDC Provider for IRSA (IAM Roles for Service Accounts)
data "tls_certificate" "cluster" {
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "cluster" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.cluster.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = var.tags
}
```

### Step 4: RDS Module

```hcl
# infrastructure/terraform/modules/rds/main.tf
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-db-subnet-group"
    }
  )
}

resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-postgres"
  engine         = "postgres"
  engine_version = var.postgres_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.master_username
  password = var.master_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.rds_security_group_id]

  multi_az               = var.multi_az
  publicly_accessible    = false
  backup_retention_period = var.backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = true

  deletion_protection      = var.deletion_protection
  skip_final_snapshot     = !var.deletion_protection
  final_snapshot_identifier = var.deletion_protection ? "${var.project_name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-postgres"
    }
  )
}
```

### Step 5: Main Terraform Configuration

```hcl
# infrastructure/terraform/environments/production/main.tf
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

locals {
  cluster_name = "${var.project_name}-${var.environment}-eks"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  cluster_name         = local.cluster_name
  tags                 = local.common_tags
}

# EKS Module
module "eks" {
  source = "../../modules/eks"

  cluster_name              = local.cluster_name
  kubernetes_version        = var.kubernetes_version
  subnet_ids                = concat(module.vpc.public_subnet_ids, module.vpc.private_subnet_ids)
  private_subnet_ids        = module.vpc.private_subnet_ids
  cluster_security_group_id = module.vpc.eks_cluster_security_group_id

  node_instance_types = var.node_instance_types
  desired_size        = var.desired_node_count
  min_size            = var.min_node_count
  max_size            = var.max_node_count
  capacity_type       = "ON_DEMAND"

  environment = var.environment
  tags        = local.common_tags
}

# RDS Module
module "rds" {
  source = "../../modules/rds"

  project_name           = var.project_name
  postgres_version       = var.postgres_version
  instance_class         = var.rds_instance_class
  allocated_storage      = var.rds_allocated_storage
  max_allocated_storage  = var.rds_max_allocated_storage
  database_name          = var.database_name
  master_username        = var.database_username
  master_password        = var.database_password
  private_subnet_ids     = module.vpc.private_subnet_ids
  rds_security_group_id  = module.vpc.rds_security_group_id
  multi_az               = true
  backup_retention_period = 7
  deletion_protection    = true
  tags                   = local.common_tags
}

# ECR Repositories
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}/backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = local.common_tags
}

resource "aws_ecr_repository" "web" {
  name                 = "${var.project_name}/web"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = local.common_tags
}

# S3 Bucket for Static Assets
resource "aws_s3_bucket" "static_assets" {
  bucket = "${var.project_name}-static-assets-${var.environment}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "static_assets" {
  bucket = aws_s3_bucket.static_assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static_assets" {
  bucket = aws_s3_bucket.static_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket for Backups
resource "aws_s3_bucket" "backups" {
  bucket = "${var.project_name}-backups-${var.environment}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "expire-old-backups"
    status = "Enabled"

    expiration {
      days = 90
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }
  }
}
```

```hcl
# infrastructure/terraform/environments/production/terraform.tfvars
project_name = "lyrica"
environment  = "production"
aws_region   = "us-east-1"

# VPC Configuration
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]
availability_zones   = ["us-east-1a", "us-east-1b"]

# EKS Configuration
kubernetes_version  = "1.28"
node_instance_types = ["t3.large"]
desired_node_count  = 3
min_node_count      = 2
max_node_count      = 10

# RDS Configuration
postgres_version        = "15.4"
rds_instance_class      = "db.t3.medium"
rds_allocated_storage   = 100
rds_max_allocated_storage = 500
database_name           = "lyrica_production"
database_username       = "lyrica_admin"
# DO NOT commit passwords! Use AWS Secrets Manager or environment variables
# database_password = "USE_SECRETS_MANAGER"
```

### Step 6: Apply Terraform

```bash
# Navigate to environment directory
cd infrastructure/terraform/environments/production

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan infrastructure changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Show outputs
terraform output

# Export kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name lyrica-production-eks

# Verify kubectl access
kubectl get nodes
kubectl get namespaces
```

---

## Kubernetes Deployment

### Step 1: Create Namespaces

```yaml
# k8s/namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    name: production
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    name: staging
    environment: staging
---
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    name: monitoring
```

```bash
# Apply namespaces
kubectl apply -f k8s/namespaces.yaml
```

### Step 2: Create Secrets

```bash
# Create database secret
kubectl create secret generic postgres-credentials \
  --from-literal=username=lyrica_admin \
  --from-literal=password=YOUR_SECURE_PASSWORD \
  --from-literal=host=lyrica-production-postgres.xyz.us-east-1.rds.amazonaws.com \
  --from-literal=port=5432 \
  --from-literal=database=lyrica_production \
  -n production

# Create Redis secret
kubectl create secret generic redis-credentials \
  --from-literal=url=redis://redis-service:6379/0 \
  -n production

# Create JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=secret-key=$(openssl rand -hex 32) \
  -n production

# Create Ollama config
kubectl create configmap ollama-config \
  --from-literal=base-url=http://ollama-service:11434 \
  --from-literal=model=llama3 \
  -n production
```

### Step 3: Deploy Backend

```yaml
# k8s/backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: production
  labels:
    app: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/lyrica/backend:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: connection-string
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret-key
        - name: OLLAMA_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: ollama-config
              key: base-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: production
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

```bash
# Apply backend deployment
kubectl apply -f k8s/backend/deployment.yaml

# Check status
kubectl get deployments -n production
kubectl get pods -n production
kubectl logs -f deployment/backend -n production
```

---

*Due to length constraints, I'll continue with the Helm Charts and remaining sections...*

## Helm Charts

### Step 1: Create Helm Chart Structure

```bash
# Create Helm chart
mkdir -p helm/lyrica
cd helm/lyrica

helm create lyrica
```

### Step 2: Chart.yaml

```yaml
# helm/lyrica/Chart.yaml
apiVersion: v2
name: lyrica
description: Agentic Song Lyrics Generator
type: application
version: 1.0.0
appVersion: "1.0.0"

dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "18.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

### Step 3: Values.yaml

```yaml
# helm/lyrica/values.yaml
replicaCount: 3

image:
  backend:
    repository: YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/lyrica/backend
    tag: "latest"
    pullPolicy: IfNotPresent
  web:
    repository: YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/lyrica/web
    tag: "latest"
    pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.lyrica.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: lyrica-tls
      hosts:
        - api.lyrica.com

resources:
  backend:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: false  # Using RDS
  
redis:
  enabled: true
  auth:
    enabled: true
    password: "YOUR_REDIS_PASSWORD"
```

### Step 4: Install Helm Chart

```bash
# Add required Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Install Lyrica
helm install lyrica ./helm/lyrica \
  --namespace production \
  --create-namespace \
  --values ./helm/lyrica/values.yaml

# Check deployment
helm list -n production
kubectl get all -n production
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  EKS_CLUSTER: lyrica-production-eks
  ECR_BACKEND_REPO: lyrica/backend
  ECR_WEB_REPO: lyrica/web

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        working-directory: ./backend
        run: |
          pytest --cov=app tests/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push backend image
        working-directory: ./backend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_BACKEND_REPO:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_BACKEND_REPO:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_BACKEND_REPO:$IMAGE_TAG $ECR_REGISTRY/$ECR_BACKEND_REPO:latest
          docker push $ECR_REGISTRY/$ECR_BACKEND_REPO:latest
      
      - name: Build and push web image
        working-directory: ./web
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_WEB_REPO:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_WEB_REPO:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_WEB_REPO:$IMAGE_TAG $ECR_REGISTRY/$ECR_WEB_REPO:latest
          docker push $ECR_REGISTRY/$ECR_WEB_REPO:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name ${{ env.EKS_CLUSTER }} --region ${{ env.AWS_REGION }}
      
      - name: Deploy to EKS
        run: |
          kubectl set image deployment/backend backend=${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_BACKEND_REPO }}:${{ github.sha }} -n production
          kubectl set image deployment/web web=${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_WEB_REPO }}:${{ github.sha }} -n production
          kubectl rollout status deployment/backend -n production
          kubectl rollout status deployment/web -n production
```

---

## Monitoring & Logging

### Install Prometheus & Grafana

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus & Grafana
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set grafana.adminPassword=YOUR_ADMIN_PASSWORD

# Port forward Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Access Grafana: http://localhost:3000
# Username: admin
# Password: YOUR_ADMIN_PASSWORD
```

---

## Troubleshooting

### Common Issues

```bash
# 1. Pods not starting
kubectl describe pod POD_NAME -n production
kubectl logs POD_NAME -n production

# 2. Service not accessible
kubectl get svc -n production
kubectl describe svc SERVICE_NAME -n production

# 3. Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# 4. Check ingress
kubectl get ingress -n production
kubectl describe ingress INGRESS_NAME -n production

# 5. Database connection issues
kubectl exec -it POD_NAME -n production -- env | grep DATABASE

# 6. Scale deployment
kubectl scale deployment backend --replicas=5 -n production

# 7. Restart deployment
kubectl rollout restart deployment backend -n production

# 8. View logs
kubectl logs -f deployment/backend -n production --tail=100
```

---

This comprehensive deployment guide provides step-by-step instructions for deploying the Lyrica lyrics generator from local development to production on AWS with Kubernetes!

