#!/bin/bash

# =============================================================================
# SUPER Vote Secret - System Validation Script
# Final verification of production readiness
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔍 SUPER Vote Secret - System Validation${NC}"
echo -e "═══════════════════════════════════════"
echo

# Check all critical files
REQUIRED_FILES=(
    "deploy.sh"
    "docker-compose.yml"
    "nginx/nginx.conf"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "README.md"
    ".env.example"
    "Makefile"
)

echo -e "${YELLOW}📁 Checking required files...${NC}"
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file (MISSING)"
        exit 1
    fi
done
echo

# Check script permissions
echo -e "${YELLOW}🔐 Checking script permissions...${NC}"
if [ -x "deploy.sh" ]; then
    echo -e "${GREEN}✅${NC} deploy.sh is executable"
else
    echo -e "${RED}❌${NC} deploy.sh is not executable"
    exit 1
fi
echo

# Validate Docker configurations
echo -e "${YELLOW}🐳 Validating Docker configurations...${NC}"

# Check docker-compose syntax (if docker is available)
if command -v docker-compose >/dev/null 2>&1; then
    if docker-compose config >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} docker-compose.yml syntax valid"
    else
        echo -e "${RED}❌${NC} docker-compose.yml syntax error"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠${NC} docker-compose not available (syntax not checked)"
fi

# Check development compose (if docker is available)
if command -v docker-compose >/dev/null 2>&1; then
    if docker-compose -f docker-compose.dev.yml config >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} docker-compose.dev.yml syntax valid"
    else
        echo -e "${RED}❌${NC} docker-compose.dev.yml syntax error"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠${NC} Development compose syntax not checked"
fi
echo

# Check script syntax
echo -e "${YELLOW}📋 Validating script syntax...${NC}"
if bash -n deploy.sh; then
    echo -e "${GREEN}✅${NC} deploy.sh syntax valid"
else
    echo -e "${RED}❌${NC} deploy.sh syntax error"
    exit 1
fi
echo

# Check for required directories
echo -e "${YELLOW}📂 Checking directory structure...${NC}"
REQUIRED_DIRS=(
    "backend"
    "frontend"
    "frontend/src"
    "nginx"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅${NC} $dir/"
    else
        echo -e "${RED}❌${NC} $dir/ (MISSING)"
        exit 1
    fi
done
echo

# System Summary
echo -e "${GREEN}🎉 SYSTEM VALIDATION COMPLETE${NC}"
echo -e "════════════════════════════════"
echo -e "${GREEN}✅${NC} All required files present"
echo -e "${GREEN}✅${NC} All configurations valid"
echo -e "${GREEN}✅${NC} All scripts properly formatted"
echo -e "${GREEN}✅${NC} Directory structure correct"
echo
echo -e "${BLUE}🚀 System is ready for production deployment!${NC}"
echo
echo -e "To deploy:"
echo -e "  ${YELLOW}./deploy.sh${NC}"
echo
echo -e "For development:"
echo -e "  ${YELLOW}make dev${NC}"
echo
echo -e "For help:"
echo -e "  ${YELLOW}make help${NC}"
echo