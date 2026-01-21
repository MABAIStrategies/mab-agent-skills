#!/bin/bash

# MAB AI Strategies - Agent Skills Platform
# GitHub Push Script
# 
# This script will initialize git and push your repository to GitHub
# Run with: bash PUSH_TO_GITHUB.sh

set -e  # Exit on error

echo "🚀 MAB AI Agent Skills - GitHub Push Script"
echo "==========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install git first.${NC}"
    echo "   Visit: https://git-scm.com/downloads"
    exit 1
fi

echo -e "${GREEN}✅ Git is installed${NC}"

# Get GitHub username
echo ""
echo -e "${BLUE}📝 GitHub Configuration${NC}"
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}❌ GitHub username cannot be empty${NC}"
    exit 1
fi

# Repository name
REPO_NAME="mab-agent-skills"

echo ""
echo -e "${BLUE}Repository Details:${NC}"
echo "   Username: $GITHUB_USERNAME"
echo "   Repository: $REPO_NAME"
echo "   URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

# Confirm
read -p "Does this look correct? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo -e "${YELLOW}⚠️  Cancelled by user${NC}"
    exit 0
fi

# Check if already initialized
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git repository already initialized${NC}"
    read -p "Do you want to reinitialize? This will delete .git directory (y/n): " REINIT
    if [ "$REINIT" == "y" ]; then
        rm -rf .git
        echo -e "${GREEN}✅ Removed existing .git directory${NC}"
    else
        echo -e "${YELLOW}⚠️  Using existing repository${NC}"
    fi
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo ""
    echo -e "${BLUE}🔧 Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
fi

# Add all files
echo ""
echo -e "${BLUE}📦 Adding files to git...${NC}"
git add .
echo -e "${GREEN}✅ Files added${NC}"

# Create commit
echo ""
echo -e "${BLUE}💾 Creating initial commit...${NC}"
git commit -m "🚀 Initial commit: MAB AI Agent Skills Platform

- 10 production-ready AI agent skills
- Enterprise infrastructure (Docker, Terraform, databases)
- Shared utilities (auth, logging, LLM integration)
- 100+ pages of documentation
- CI/CD workflows with GitHub Actions
- Monitoring & observability setup

Built for MAB AI Strategies LLC
Author: Mark Bockrath"

echo -e "${GREEN}✅ Commit created${NC}"

# Set main branch
echo ""
echo -e "${BLUE}🌿 Setting main branch...${NC}"
git branch -M main
echo -e "${GREEN}✅ Main branch set${NC}"

# Add remote
echo ""
echo -e "${BLUE}🔗 Adding GitHub remote...${NC}"
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git" 2>/dev/null || \
git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo -e "${GREEN}✅ Remote added${NC}"

# Push to GitHub
echo ""
echo -e "${BLUE}🚀 Pushing to GitHub...${NC}"
echo ""
echo -e "${YELLOW}⚠️  You will be prompted for your GitHub credentials${NC}"
echo ""

if git push -u origin main; then
    echo ""
    echo -e "${GREEN}===============================================${NC}"
    echo -e "${GREEN}🎉 SUCCESS! Repository pushed to GitHub!${NC}"
    echo -e "${GREEN}===============================================${NC}"
    echo ""
    echo -e "${BLUE}📍 Your repository:${NC}"
    echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "   1. Go to your repository on GitHub"
    echo "   2. Set up GitHub Secrets for CI/CD (see GITHUB_SETUP.md)"
    echo "   3. Enable GitHub Actions"
    echo "   4. Add repository topics/tags"
    echo "   5. Pin to your GitHub profile"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "   - GITHUB_SETUP.md - Complete GitHub configuration guide"
    echo "   - DEPLOYMENT_GUIDE.md - Deploy to production"
    echo "   - MASTER_IMPLEMENTATION_GUIDE.md - Implement remaining skills"
    echo ""
    echo -e "${GREEN}🏀 Great job! Your enterprise AI platform is now on GitHub!${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}===============================================${NC}"
    echo -e "${RED}❌ Push failed${NC}"
    echo -e "${RED}===============================================${NC}"
    echo ""
    echo -e "${YELLOW}Common issues:${NC}"
    echo "   1. Repository doesn't exist on GitHub yet"
    echo "      → Create it first: https://github.com/new"
    echo "      → Name: $REPO_NAME"
    echo "      → Do NOT initialize with README"
    echo ""
    echo "   2. Authentication failed"
    echo "      → Use Personal Access Token instead of password"
    echo "      → Create token: https://github.com/settings/tokens"
    echo ""
    echo "   3. Permission denied"
    echo "      → Verify repository ownership"
    echo "      → Check repository URL"
    echo ""
    echo "See GITHUB_SETUP.md for detailed troubleshooting"
    exit 1
fi
