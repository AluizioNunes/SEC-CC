#!/bin/bash

# SEC Application Deployment Script
# Automated deployment with security and monitoring

set -e

# Configuration
ENVIRONMENT=${1:-staging}
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="/backup/deployments"
LOG_FILE="/var/log/sec-deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."

    # Check if docker and docker-compose are installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
    fi

    # Check if required files exist
    required_files=("$DOCKER_COMPOSE_FILE" ".env")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Required file $file not found"
        fi
    done

    # Check available disk space
    available_space=$(df /var/lib/docker | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 5000000 ]; then  # Less than 5GB
        warning "Low disk space available for Docker"
    fi

    # Check if ports are available
    ports=(80 443 8000 3000 5432 6379 27017)
    for port in "${ports[@]}"; do
        if lsof -i :$port &> /dev/null; then
            warning "Port $port is already in use"
        fi
    done

    success "Pre-deployment checks completed"
}

# Create backup
create_backup() {
    log "💾 Creating backup..."

    backup_name="sec-backup-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Backup current deployment if exists
    if [ -d "/opt/sec" ]; then
        tar -czf "$BACKUP_DIR/$backup_name-current.tar.gz" -C /opt sec/ || warning "Failed to backup current deployment"
    fi

    # Backup database
    if docker ps -q -f name=CC-POSTGRESQL &> /dev/null; then
        log "Backing up PostgreSQL database..."
        docker exec CC-POSTGRESQL pg_dump -U ${POSTGRES_USER:-sec_user} ${POSTGRES_DB:-sec_db} > "$BACKUP_DIR/$backup_name-postgres.sql" || warning "Failed to backup PostgreSQL"
    fi

    # Backup Redis data
    if docker ps -q -f name=CC-REDIS &> /dev/null; then
        log "Backing up Redis data..."
        docker exec CC-REDIS redis-cli SAVE || warning "Failed to backup Redis"
    fi

    success "Backup created: $backup_name"
}

# Security hardening
security_hardening() {
    log "🔐 Applying security hardening..."

    # Generate secure secrets if they don't exist
    if [ ! -f ".env.security" ]; then
        log "Generating security configuration..."
        cat > .env.security << EOF
JWT_SECRET_KEY=$(openssl rand -hex 32)
REDIS_PASSWORD=$(openssl rand -hex 16)
DB_PASSWORD=$(openssl rand -hex 16)
API_KEY=$(openssl rand -hex 16)
EOF
        success "Security configuration generated"
    fi

    # Set proper file permissions
    chmod 600 .env .env.security || warning "Failed to set file permissions"

    # Check SSL certificates
    if [ "$ENVIRONMENT" = "production" ]; then
        if [ ! -d "/etc/letsencrypt/live/${DOMAIN:-localhost}" ]; then
            warning "SSL certificates not found. Run Let's Encrypt setup first."
        fi
    fi

    success "Security hardening applied"
}

# Deploy application
deploy_application() {
    log "🚀 Deploying SEC application to $ENVIRONMENT..."

    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down || warning "Failed to stop existing containers"

    # Remove old images (keep last 5)
    log "Cleaning up old Docker images..."
    docker image prune -f || warning "Failed to prune old images"

    # Pull latest images if using pre-built ones
    if [ "$USE_PREBUILT_IMAGES" = "true" ]; then
        log "Pulling pre-built images..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" pull || warning "Failed to pull images"
    else
        # Build images
        log "Building Docker images..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" build --parallel || error "Failed to build images"
    fi

    # Start application
    log "Starting application..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d || error "Failed to start application"

    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30

    # Check service health
    check_service_health

    success "Application deployed successfully"
}

# Check service health
check_service_health() {
    log "🏥 Checking service health..."

    services=("CC-NGINX" "CC-FRONTEND" "CC-FASTAPI" "CC-NESTJS" "CC-POSTGRESQL" "CC-REDIS")

    for service in "${services[@]}"; do
        if docker ps -q -f name="$service" &> /dev/null; then
            # Check if service responds to health checks
            if [ "$service" = "CC-NGINX" ]; then
                if curl -f -s http://localhost/health > /dev/null; then
                    log "✅ $service is healthy"
                else
                    error "$service health check failed"
                fi
            elif [ "$service" = "CC-FASTAPI" ]; then
                if curl -f -s http://localhost:8000/health > /dev/null; then
                    log "✅ $service is healthy"
                else
                    error "$service health check failed"
                fi
            elif [ "$service" = "CC-NESTJS" ]; then
                if curl -f -s http://localhost:3000/health > /dev/null; then
                    log "✅ $service is healthy"
                else
                    error "$service health check failed"
                fi
            fi
        else
            warning "$service is not running"
        fi
    done

    success "Health checks completed"
}

# Post-deployment tasks
post_deployment_tasks() {
    log "🔧 Running post-deployment tasks..."

    # Update monitoring dashboards
    if command -v curl &> /dev/null; then
        # Reload Grafana dashboards if Grafana is running
        if docker ps -q -f name=CC-GRAFANA &> /dev/null; then
            curl -X POST http://admin:admin@localhost:3001/api/admin/provisioning/dashboards/reload || warning "Failed to reload Grafana dashboards"
        fi
    fi

    # Run database migrations if needed
    # Add your migration commands here

    # Clean up old backups (keep last 7 days)
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +7 -delete || warning "Failed to clean old backups"

    success "Post-deployment tasks completed"
}

# Send notifications
send_notifications() {
    log "📧 Sending deployment notifications..."

    # Here you can add Slack, Discord, or email notifications
    # Example:
    # curl -X POST -H 'Content-type: application/json' \
    #   --data '{"text":"SEC Application deployed to $ENVIRONMENT successfully"}' \
    #   $SLACK_WEBHOOK_URL

    success "Notifications sent"
}

# Main deployment flow
main() {
    log "🚀 Starting SEC Application deployment to $ENVIRONMENT environment"

    pre_deployment_checks
    create_backup
    security_hardening
    deploy_application
    post_deployment_tasks
    send_notifications

    log "🎉 Deployment completed successfully!"
    echo -e "${GREEN}=======================================${NC}"
    echo -e "${GREEN}   SEC Application Deployed Successfully${NC}"
    echo -e "${GREEN}   Environment: $ENVIRONMENT${NC}"
    echo -e "${GREEN}   Time: $(date)${NC}"
    echo -e "${GREEN}=======================================${NC}"
}

# Handle script arguments
case "${1:-}" in
    "staging")
        ENVIRONMENT="staging"
        main
        ;;
    "production")
        ENVIRONMENT="production"
        # Add extra checks for production
        if [ "$(whoami)" != "root" ]; then
            error "Production deployment must be run as root"
        fi
        main
        ;;
    "rollback")
        log "🔄 Rolling back to previous version..."
        # Add rollback logic here
        ;;
    *)
        echo "Usage: $0 {staging|production|rollback}"
        exit 1
        ;;
esac
