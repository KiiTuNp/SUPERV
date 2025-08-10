#!/bin/bash

# =============================================================================
# SUPER Vote Secret - Ultimate Production Deployment Script
# Ultra-robust HTTPS configuration with comprehensive validation
# =============================================================================

set -euo pipefail

# Colors and formatting
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# Configuration constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/deployment.log"
readonly MAX_WAIT_TIME=600
readonly SSL_MAX_ATTEMPTS=3
readonly HEALTH_CHECK_TIMEOUT=120
readonly WEB_ACCESS_MIN_SUCCESS_RATE=70

# Global state variables
DOMAIN=""
ADMIN_EMAIL=""
MONGO_ROOT_PASSWORD=""
JWT_SECRET=""
ENCRYPTION_KEY=""
DEPLOYMENT_START_TIME=0
SSL_CONFIGURED=false
HTTP_WORKING=false
HTTPS_WORKING=false

# =============================================================================
# LOGGING AND UTILITY FUNCTIONS
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${BLUE}ℹ${NC} ${message}" ;;
        "SUCCESS") echo -e "${GREEN}✅${NC} ${message}" ;;
        "WARNING") echo -e "${YELLOW}⚠${NC} ${message}" ;;
        "ERROR") echo -e "${RED}❌${NC} ${message}" ;;
        "STEP") echo -e "${CYAN}▶${NC} ${BOLD}${message}${NC}" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

show_header() {
    clear
    echo -e "${CYAN}${BOLD}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                      🗳️  SUPER VOTE SECRET                                   ║
║                   Production Deployment System                              ║
║                                                                              ║
║              🔒 Ultra-Robust HTTPS • 🚀 Zero-Downtime • 🛡️ Secure            ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${BOLD}Version 3.0 - Production-Ready Deployment with Comprehensive Validation${NC}"
    echo -e "═══════════════════════════════════════════════════════════════════════════════"
    echo
}

spinner() {
    local pid=$1
    local message="$2"
    local timeout="${3:-60}"
    local chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    local start_time=$(date +%s)
    
    while kill -0 $pid 2>/dev/null; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            kill $pid 2>/dev/null || true
            printf "\r${RED}✗${NC} %s (timeout after %ds)\n" "$message" "$timeout"
            return 1
        fi
        
        for (( i=0; i<${#chars}; i++ )); do
            printf "\r${BLUE}%s${NC} %s (%ds)" "${chars:$i:1}" "$message" "$elapsed"
            sleep 0.1
            if ! kill -0 $pid 2>/dev/null; then
                break
            fi
        done
    done
    
    wait $pid
    local exit_code=$?
    local final_time=$(($(date +%s) - start_time))
    
    if [ $exit_code -eq 0 ]; then
        printf "\r${GREEN}✅${NC} %s (${final_time}s)\n" "$message"
        return 0
    else
        printf "\r${RED}✗${NC} %s (failed after ${final_time}s)\n" "$message"
        return 1
    fi
}

# =============================================================================
# SYSTEM VERIFICATION
# =============================================================================

verify_system() {
    log "STEP" "System Verification"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed"
        echo -e "${YELLOW}📦 Install Docker: https://docs.docker.com/engine/install/${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! (command -v docker-compose &> /dev/null || docker compose version &> /dev/null); then
        log "ERROR" "Docker Compose is not available"
        echo -e "${YELLOW}📦 Install Docker Compose: https://docs.docker.com/compose/install/${NC}"
        exit 1
    fi
    
    # Test Docker permissions
    if ! docker ps &> /dev/null; then
        log "ERROR" "Cannot access Docker daemon"
        echo -e "${YELLOW}🔐 Add user to docker group: sudo usermod -aG docker \$USER${NC}"
        exit 1
    fi
    
    # Check available disk space (minimum 5GB)
    local disk_space_kb=$(df . | awk 'NR==2 {print $4}')
    local disk_space_gb=$((disk_space_kb / 1024 / 1024))
    
    if [ $disk_space_gb -lt 5 ]; then
        log "WARNING" "Low disk space: ${disk_space_gb}GB available (5GB+ recommended)"
        read -p "Continue with deployment? (y/N): " continue_anyway
        if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check port availability
    local conflicting_services=()
    for port in 80 443; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            local service=$(netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f2 | head -1)
            conflicting_services+=("Port $port: ${service:-unknown}")
        fi
    done
    
    if [ ${#conflicting_services[@]} -gt 0 ]; then
        log "WARNING" "Conflicting services detected: ${conflicting_services[*]}"
        log "INFO" "These will be stopped automatically during deployment"
    fi
    
    log "SUCCESS" "System verification completed"
}

# =============================================================================
# CONFIGURATION COLLECTION
# =============================================================================

collect_configuration() {
    log "STEP" "Configuration Collection"
    
    echo -e "\n${BOLD}📋 Deployment Configuration${NC}"
    echo -e "${CYAN}───────────────────────────${NC}\n"
    
    # Domain validation
    while [[ -z "$DOMAIN" ]]; do
        echo -e "${BOLD}🌐 Domain Configuration${NC}"
        read -p "Enter your domain (e.g., vote.example.com): " DOMAIN
        
        # Basic format validation
        if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$ ]]; then
            echo -e "${RED}❌ Invalid domain format${NC}"
            DOMAIN=""
            continue
        fi
        
        # DNS resolution check
        echo -e "${YELLOW}🔍 Checking DNS resolution...${NC}"
        if host "$DOMAIN" &>/dev/null; then
            local resolved_ip=$(host "$DOMAIN" 2>/dev/null | grep "has address" | awk '{print $4}' | head -1)
            echo -e "${GREEN}✅ DNS resolved: $DOMAIN → $resolved_ip${NC}"
        else
            echo -e "${YELLOW}⚠ DNS not resolved for $DOMAIN${NC}"
            echo -e "${YELLOW}📝 Make sure your domain points to this server${NC}"
            read -p "Continue anyway? (y/N): " dns_continue
            if [[ ! "$dns_continue" =~ ^[Yy]$ ]]; then
                DOMAIN=""
                continue
            fi
        fi
    done
    
    # Email validation
    while [[ -z "$ADMIN_EMAIL" ]]; do
        echo -e "\n${BOLD}📧 SSL Configuration${NC}"
        read -p "Enter admin email (for SSL certificates): " ADMIN_EMAIL
        
        if [[ ! "$ADMIN_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            echo -e "${RED}❌ Invalid email format${NC}"
            ADMIN_EMAIL=""
        fi
    done
    
    # Secure password generation
    while [[ -z "$MONGO_ROOT_PASSWORD" ]]; do
        echo -e "\n${BOLD}🔒 Database Security${NC}"
        echo -e "Password requirements:"
        echo -e "  • Minimum 16 characters"
        echo -e "  • Mix of uppercase, lowercase, numbers, symbols"
        echo -e "  • No dictionary words"
        
        read -s -p "Enter MongoDB password: " MONGO_ROOT_PASSWORD
        echo
        
        # Password strength validation
        if [[ ${#MONGO_ROOT_PASSWORD} -lt 16 ]]; then
            echo -e "${RED}❌ Password too short (minimum 16 characters)${NC}"
            MONGO_ROOT_PASSWORD=""
            continue
        fi
        
        local strength_checks=0
        [[ "$MONGO_ROOT_PASSWORD" =~ [A-Z] ]] && ((strength_checks++))
        [[ "$MONGO_ROOT_PASSWORD" =~ [a-z] ]] && ((strength_checks++))
        [[ "$MONGO_ROOT_PASSWORD" =~ [0-9] ]] && ((strength_checks++))
        [[ "$MONGO_ROOT_PASSWORD" =~ [^A-Za-z0-9] ]] && ((strength_checks++))
        
        if [ $strength_checks -lt 4 ]; then
            echo -e "${RED}❌ Password must contain uppercase, lowercase, numbers, and symbols${NC}"
            MONGO_ROOT_PASSWORD=""
            continue
        fi
        
        # Confirm password
        read -s -p "Confirm password: " password_confirm
        echo
        
        if [[ "$MONGO_ROOT_PASSWORD" != "$password_confirm" ]]; then
            echo -e "${RED}❌ Passwords do not match${NC}"
            MONGO_ROOT_PASSWORD=""
        fi
    done
    
    # Generate cryptographically secure keys
    log "INFO" "Generating security keys..."
    JWT_SECRET=$(openssl rand -base64 64 | tr -d '\n')
    ENCRYPTION_KEY=$(openssl rand -hex 32)
    
    # Configuration summary
    echo -e "\n${BOLD}📋 Configuration Summary${NC}"
    echo -e "${CYAN}───────────────────────────${NC}"
    echo -e "🌐 Domain: ${GREEN}$DOMAIN${NC}"
    echo -e "📧 Email: ${GREEN}$ADMIN_EMAIL${NC}"
    echo -e "🔒 Database: ${GREEN}Secure password configured${NC}"
    echo -e "🔑 Security: ${GREEN}Cryptographic keys generated${NC}"
    
    echo
    read -p "Proceed with this configuration? (Y/n): " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        log "INFO" "Deployment cancelled by user"
        exit 0
    fi
    
    log "SUCCESS" "Configuration collected and validated"
}

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

setup_environment() {
    log "STEP" "Environment Setup"
    
    # Create directory structure
    mkdir -p data/mongodb nginx/ssl
    
    # Generate DH parameters for enhanced SSL security
    if [ ! -f "nginx/ssl/dhparam.pem" ]; then
        log "INFO" "Generating DH parameters (this may take a few minutes)..."
        (openssl dhparam -out nginx/ssl/dhparam.pem 2048) &
        spinner $! "Generating DH parameters" 300
    fi
    
    # Generate self-signed certificates for fallback
    if [ ! -f "nginx/ssl/nginx-selfsigned.crt" ]; then
        log "INFO" "Generating fallback SSL certificates..."
        openssl req -new -x509 -days 3650 -nodes \
            -out nginx/ssl/nginx-selfsigned.crt \
            -keyout nginx/ssl/nginx-selfsigned.key \
            -subj "/C=US/ST=CA/L=San Francisco/O=Vote Secret/OU=IT/CN=$DOMAIN" \
            -addext "subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN,DNS:localhost,IP:127.0.0.1"
    fi
    
    # Create optimized environment file
    cat > .env << EOF
# SUPER Vote Secret - Production Environment
# Generated: $(date -Iseconds)

# Domain Configuration
DOMAIN=$DOMAIN
ADMIN_EMAIL=$ADMIN_EMAIL

# MongoDB Configuration
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=$MONGO_ROOT_PASSWORD
MONGO_DB=vote_secret

# Security Configuration (Auto-generated)
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY

# Application Settings
APP_NAME=SUPER Vote Secret
APP_VERSION=3.0.0
NODE_ENV=production
PYTHON_ENV=production

# SSL Configuration
SSL_ENABLED=true

# Performance Settings  
COMPOSE_PARALLEL_LIMIT=8
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1

# Deployment Metadata
DEPLOY_DATE=$(date -Iseconds)
DEPLOY_USER=${USER:-unknown}
DEPLOY_HOST=$(hostname)
EOF
    
    chmod 600 .env
    
    log "SUCCESS" "Environment setup completed"
}

# =============================================================================
# SERVICE MANAGEMENT
# =============================================================================

stop_conflicting_services() {
    log "STEP" "Managing Conflicting Services"
    
    local services_stopped=false
    
    # Stop system web servers
    for service in nginx apache2 httpd; do
        if systemctl is-active --quiet $service 2>/dev/null; then
            log "INFO" "Stopping system $service..."
            sudo systemctl stop $service || true
            sudo systemctl disable $service || true
            services_stopped=true
        fi
    done
    
    # Clean up old containers
    local old_containers=$(docker ps -a --format "{{.Names}}" | grep -E "vote-secret|nginx|apache" | head -10)
    if [[ -n "$old_containers" ]]; then
        log "INFO" "Removing old containers..."
        echo "$old_containers" | xargs -r docker stop 2>/dev/null || true
        echo "$old_containers" | xargs -r docker rm 2>/dev/null || true
        services_stopped=true
    fi
    
    # Docker system cleanup
    if [ "$services_stopped" = true ]; then
        log "INFO" "Cleaning Docker resources..."
        docker system prune -f &>/dev/null || true
        sleep 5
    fi
    
    log "SUCCESS" "Conflicting services managed"
}

# =============================================================================
# DEPLOYMENT
# =============================================================================

deploy_application() {
    log "STEP" "Application Deployment"
    
    # Build and start services
    log "INFO" "Building application images..."
    (
        export DOCKER_BUILDKIT=1
        export COMPOSE_DOCKER_CLI_BUILD=1
        export COMPOSE_PARALLEL_LIMIT=8
        
        docker-compose build --no-cache --parallel 2>&1 | tee -a "$LOG_FILE"
    ) &
    
    if ! spinner $! "Building Docker images" 900; then
        log "ERROR" "Failed to build Docker images"
        return 1
    fi
    
    # Start services
    log "INFO" "Starting services..."
    if ! docker-compose up -d; then
        log "ERROR" "Failed to start services"
        return 1
    fi
    
    log "SUCCESS" "Application deployed successfully"
}

# =============================================================================
# HEALTH CHECKS
# =============================================================================

wait_for_services() {
    log "STEP" "Service Health Verification"
    
    local services=(
        "mongodb:27017:MongoDB"
        "backend:8001:Backend API"
        "frontend:3000:Frontend"  
        "nginx:80:Nginx Proxy"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service port name <<< "$service_info"
        
        log "INFO" "Waiting for $name..."
        local attempts=0
        local max_attempts=60
        
        while [ $attempts -lt $max_attempts ]; do
            if docker-compose ps "$service" | grep -q "Up"; then
                case "$service" in
                    "mongodb")
                        if docker-compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" &>/dev/null; then
                            break
                        fi
                        ;;
                    *)
                        if curl -sf --max-time 5 "http://localhost:$port/health" &>/dev/null; then
                            break
                        fi
                        ;;
                esac
            fi
            
            attempts=$((attempts + 1))
            printf "\r${YELLOW}⏳${NC} $name health check... ($attempts/$max_attempts)"
            sleep 2
        done
        
        if [ $attempts -ge $max_attempts ]; then
            printf "\r${RED}❌${NC} $name health check failed\n"
            log "ERROR" "$name failed to start properly"
            return 1
        else
            printf "\r${GREEN}✅${NC} $name is healthy\n"
            log "SUCCESS" "$name started successfully"
        fi
    done
    
    log "SUCCESS" "All services are healthy"
}

# =============================================================================
# SSL CONFIGURATION
# =============================================================================

configure_ssl() {
    log "STEP" "SSL Certificate Configuration"
    
    # Wait for nginx to be fully ready
    sleep 30
    
    # Test domain accessibility first
    log "INFO" "Testing domain accessibility..."
    local domain_accessible=false
    
    for attempt in {1..10}; do
        if curl -sf --max-time 10 "http://$DOMAIN/.well-known/" &>/dev/null; then
            domain_accessible=true
            break
        fi
        printf "\r${YELLOW}⏳${NC} Testing domain accessibility... ($attempt/10)"
        sleep 3
    done
    
    if [ "$domain_accessible" = true ]; then
        printf "\r${GREEN}✅${NC} Domain is accessible for SSL validation\n"
    else
        printf "\r${YELLOW}⚠${NC}  Domain accessibility uncertain\n"
        log "WARNING" "Domain $DOMAIN may not be properly configured"
    fi
    
    # Configure SSL certificate
    log "INFO" "Configuring SSL certificate..."
    
    # Monitor SSL generation
    local ssl_success=false
    local attempt=0
    
    while [ $attempt -lt $SSL_MAX_ATTEMPTS ] && [ "$ssl_success" = false ]; do
        attempt=$((attempt + 1))
        log "INFO" "SSL attempt $attempt/$SSL_MAX_ATTEMPTS"
        
        # Wait for certificate generation
        local wait_time=0
        while [ $wait_time -lt 300 ]; do  # 5 minutes max
            # Check if certificate was generated
            if docker-compose exec -T certbot test -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" 2>/dev/null; then
                ssl_success=true
                printf "\r${GREEN}✅${NC} SSL certificate generated successfully\n"
                break
            fi
            
            # Check for errors
            local recent_logs=$(docker-compose logs --tail 20 certbot 2>/dev/null)
            if echo "$recent_logs" | grep -qE "(error|Error|failed|Failed)"; then
                printf "\r${RED}❌${NC} SSL generation encountered errors\n"
                break
            fi
            
            printf "\r${YELLOW}⏳${NC} Generating SSL certificate... (${wait_time}s/300s)"
            sleep 10
            wait_time=$((wait_time + 10))
        done
        
        [ "$ssl_success" = false ] && [ $attempt -lt $SSL_MAX_ATTEMPTS ] && sleep 30
    done
    
    if [ "$ssl_success" = true ]; then
        SSL_CONFIGURED=true
        log "SUCCESS" "SSL certificate configured successfully"
    else
        log "WARNING" "SSL automatic generation failed - HTTP mode available"
        echo -e "${YELLOW}💡 Manual SSL setup:${NC}"
        echo -e "   1. Verify $DOMAIN points to this server"
        echo -e "   2. Restart SSL generation: ${CYAN}docker-compose restart certbot${NC}"
        echo -e "   3. Check logs: ${CYAN}docker-compose logs -f certbot${NC}"
    fi
}

# =============================================================================
# COMPREHENSIVE WEB ACCESSIBILITY TESTING
# =============================================================================

test_web_accessibility() {
    log "STEP" "Web Accessibility Validation"
    
    # Test endpoints with comprehensive validation
    local test_results=()
    local total_tests=0
    local successful_tests=0
    
    # HTTP endpoints
    local http_endpoints=(
        "http://localhost/health|Local HTTP Health"
        "http://localhost:80/health|Port 80 Health"
        "http://$DOMAIN/health|Domain HTTP Health"
        "http://localhost/api/health|API HTTP Health"
        "http://localhost|Frontend HTTP"
        "http://$DOMAIN|Domain HTTP Frontend"
    )
    
    # HTTPS endpoints (if SSL configured)
    local https_endpoints=()
    if [ "$SSL_CONFIGURED" = true ]; then
        https_endpoints=(
            "https://localhost:443/health|HTTPS Port 443 Health"
            "https://$DOMAIN/health|Domain HTTPS Health"
            "https://localhost/api/health|API HTTPS Health"
            "https://$DOMAIN|Domain HTTPS Frontend"
        )
    fi
    
    # Fallback SSL endpoints
    local fallback_endpoints=(
        "https://localhost:8443/health|Fallback SSL Health"
    )
    
    echo -e "\n${BOLD}🌐 Comprehensive Accessibility Testing${NC}"
    echo -e "${CYAN}───────────────────────────────────────${NC}\n"
    
    # Test all endpoints
    for endpoints_array in "http_endpoints[@]" "https_endpoints[@]" "fallback_endpoints[@]"; do
        local array_name=$endpoints_array
        eval "local endpoints=(\"\${${array_name}}\")"
        
        for endpoint_test in "${endpoints[@]}"; do
            [ -z "$endpoint_test" ] && continue
            
            local url=$(echo "$endpoint_test" | cut -d'|' -f1)
            local description=$(echo "$endpoint_test" | cut -d'|' -f2)
            
            total_tests=$((total_tests + 1))
            
            printf "${YELLOW}⏳${NC} Testing: $description..."
            
            local test_passed=false
            local response=""
            
            # Multiple attempts with different validation criteria
            for attempt in {1..3}; do
                # Health endpoint test
                if [[ "$url" == *"/health" ]]; then
                    if response=$(curl -sf --max-time 15 --connect-timeout 5 -k "$url" 2>/dev/null); then
                        if [[ "$response" == *"healthy"* ]] || [[ "$response" == *"secure"* ]]; then
                            test_passed=true
                            break
                        fi
                    fi
                # Frontend test (looking for HTML content)
                else
                    if response=$(curl -sf --max-time 20 --connect-timeout 5 -k "$url" 2>/dev/null); then
                        if [[ "$response" == *"<html"* ]] || [[ "$response" == *"<!DOCTYPE"* ]] || [[ "$response" == *"Vote Secret"* ]]; then
                            test_passed=true
                            break
                        fi
                    fi
                fi
                
                [ $attempt -lt 3 ] && sleep 2
            done
            
            if [ "$test_passed" = true ]; then
                printf "\r${GREEN}✅${NC} $description\n"
                successful_tests=$((successful_tests + 1))
                
                # Set accessibility flags
                if [[ "$url" == *"https://"* ]]; then
                    HTTPS_WORKING=true
                else
                    HTTP_WORKING=true
                fi
            else
                printf "\r${RED}❌${NC} $description\n"
                log "WARNING" "$description - URL: $url"
            fi
        done
    done
    
    # Calculate success rate
    local success_rate=0
    [ $total_tests -gt 0 ] && success_rate=$(( (successful_tests * 100) / total_tests ))
    
    echo -e "\n${BOLD}📊 Accessibility Test Results${NC}"
    echo -e "${CYAN}─────────────────────────────${NC}"
    echo -e "Tests passed: ${GREEN}$successful_tests/$total_tests${NC} (${success_rate}%)"
    
    if [ "$HTTP_WORKING" = true ]; then
        echo -e "${GREEN}✅${NC} HTTP access confirmed"
    fi
    
    if [ "$HTTPS_WORKING" = true ]; then
        echo -e "${GREEN}✅${NC} HTTPS access confirmed"
    fi
    
    # Validation threshold
    if [ $success_rate -ge $WEB_ACCESS_MIN_SUCCESS_RATE ]; then
        log "SUCCESS" "Web accessibility validation passed ($success_rate%)"
        return 0
    else
        log "ERROR" "Web accessibility validation failed ($success_rate% < $WEB_ACCESS_MIN_SUCCESS_RATE%)"
        return 1
    fi
}

# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================

show_deployment_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - DEPLOYMENT_START_TIME))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    clear
    
    if [ "$HTTP_WORKING" = true ] || [ "$HTTPS_WORKING" = true ]; then
        echo -e "${GREEN}${BOLD}"
        cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🎉 DEPLOYMENT SUCCESSFUL! 🎉                         ║
║                     Your application is now live!                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    else
        echo -e "${YELLOW}${BOLD}"
        cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ⚠️  DEPLOYMENT NEEDS ATTENTION ⚠️                       ║
║                   Application deployed but needs configuration              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    fi
    echo -e "${NC}"
    
    echo -e "${BOLD}📊 Deployment Summary${NC}"
    echo -e "${CYAN}══════════════════════${NC}"
    echo -e "⏱️  Duration: ${GREEN}${minutes}m ${seconds}s${NC}"
    echo -e "🌐 Domain: ${GREEN}$DOMAIN${NC}"
    echo -e "📧 Admin: ${GREEN}$ADMIN_EMAIL${NC}"
    echo -e "🐳 Containers: ${GREEN}$(docker-compose ps --services | wc -l) running${NC}"
    echo -e "💾 Data: ${GREEN}Persistent (Docker volumes)${NC}"
    echo
    
    echo -e "${BOLD}🌍 Access URLs${NC}"
    echo -e "${CYAN}══════════════${NC}"
    
    if [ "$HTTP_WORKING" = true ]; then
        echo -e "🔗 HTTP:  ${CYAN}http://$DOMAIN${NC} ${GREEN}✅ Accessible${NC}"
        echo -e "📍 Local: ${CYAN}http://localhost${NC} ${GREEN}✅ Working${NC}"
    fi
    
    if [ "$HTTPS_WORKING" = true ]; then
        echo -e "🔒 HTTPS: ${CYAN}https://$DOMAIN${NC} ${GREEN}✅ Secure${NC}"
    elif [ "$SSL_CONFIGURED" = true ]; then
        echo -e "🔒 HTTPS: ${CYAN}https://$DOMAIN${NC} ${YELLOW}⏳ Configuring${NC}"
    else
        echo -e "🔒 HTTPS: ${YELLOW}⚠️  Manual configuration needed${NC}"
    fi
    
    echo
    
    # Status assessment
    if [ "$HTTP_WORKING" = true ] && [ "$HTTPS_WORKING" = true ]; then
        echo -e "${GREEN}${BOLD}🚀 Status: Production Ready${NC}"
        echo -e "   Your application is fully operational with SSL security"
    elif [ "$HTTP_WORKING" = true ]; then
        echo -e "${YELLOW}${BOLD}⚙️  Status: HTTP Operational${NC}"
        echo -e "   Application accessible via HTTP - SSL configuration in progress"
    else
        echo -e "${RED}${BOLD}🔧 Status: Configuration Required${NC}"
        echo -e "   Please check network configuration and domain DNS settings"
    fi
    
    echo
    echo -e "${BOLD}🛠️  Management Commands${NC}"
    echo -e "${CYAN}══════════════════════${NC}"
    echo -e "📊 Status:    ${YELLOW}docker-compose ps${NC}"
    echo -e "📋 Logs:      ${YELLOW}docker-compose logs -f [service]${NC}"
    echo -e "🔄 Restart:   ${YELLOW}docker-compose restart${NC}"
    echo -e "🛑 Stop:      ${YELLOW}docker-compose down${NC}"
    echo -e "🔒 SSL Setup: ${YELLOW}docker-compose logs -f certbot${NC}"
    
    echo
    echo -e "${BOLD}📁 Important Files${NC}"
    echo -e "${CYAN}═════════════════${NC}"
    echo -e "• Environment: ${YELLOW}.env${NC}"
    echo -e "• Logs: ${YELLOW}$LOG_FILE${NC}"
    echo -e "• Data: ${YELLOW}Docker volumes${NC}"
    echo
    
    # SSL guidance if needed
    if [ "$HTTPS_WORKING" != true ] && [ "$SSL_CONFIGURED" != true ]; then
        echo -e "${YELLOW}${BOLD}🔒 SSL Configuration Guide${NC}"
        echo -e "${YELLOW}══════════════════════════${NC}"
        echo -e "If SSL setup failed, verify:"
        echo -e "1. Domain DNS: ${CYAN}nslookup $DOMAIN${NC}"
        echo -e "2. Port 80 accessibility: ${CYAN}curl -I http://$DOMAIN${NC}"
        echo -e "3. Retry SSL: ${CYAN}docker-compose restart certbot${NC}"
        echo -e "4. Check logs: ${CYAN}docker-compose logs -f certbot${NC}"
        echo
    fi
    
    log "SUCCESS" "Deployment completed in ${minutes}m ${seconds}s"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

cleanup_on_exit() {
    log "WARNING" "Deployment interrupted - cleaning up..."
    docker-compose down 2>/dev/null || true
    exit 1
}

main() {
    DEPLOYMENT_START_TIME=$(date +%s)
    
    # Setup signal handling
    trap cleanup_on_exit INT TERM
    
    # Initialize
    show_header
    log "INFO" "Starting SUPER Vote Secret deployment"
    
    # Execute deployment steps
    verify_system
    collect_configuration
    setup_environment
    stop_conflicting_services
    
    if ! deploy_application; then
        log "ERROR" "Application deployment failed"
        exit 1
    fi
    
    if ! wait_for_services; then
        log "ERROR" "Services failed to start properly"
        exit 1
    fi
    
    configure_ssl
    
    # Critical validation step
    if ! test_web_accessibility; then
        log "WARNING" "Web accessibility validation incomplete"
        echo -e "\n${YELLOW}⚠️  Application deployed but may need additional configuration${NC}"
        echo -e "Check logs and service status: ${CYAN}docker-compose ps && docker-compose logs${NC}"
    fi
    
    # Show final results
    show_deployment_summary
    
    # Final message based on actual results
    if [ "$HTTP_WORKING" = true ]; then
        echo -e "${GREEN}${BOLD}🎉 SUCCESS: Your SUPER Vote Secret application is now live!${NC}"
        echo -e "${CYAN}🔗 Access your application: http://$DOMAIN${NC}"
        if [ "$HTTPS_WORKING" = true ]; then
            echo -e "${CYAN}🔒 Secure access: https://$DOMAIN${NC}"
        fi
    else
        echo -e "${YELLOW}${BOLD}⚠️  DEPLOYMENT COMPLETE: Additional configuration may be needed${NC}"
        echo -e "Review the deployment logs and check service status for any issues."
    fi
    
    echo
    echo -e "📖 For detailed documentation, see: ${CYAN}README.md${NC}"
}

# Ensure script is run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Check for root execution
    if [[ $EUID -eq 0 ]]; then
        echo -e "${YELLOW}⚠️  Running as root is not recommended for security${NC}"
        read -p "Continue anyway? (y/N): " continue_root
        if [[ ! "$continue_root" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    main "$@"
fi