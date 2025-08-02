#!/bin/bash

# Environment Setup Script
# This script helps set up local environment files from templates

echo "🔧 Setting up environment files..."

# Function to copy template if env file doesn't exist
setup_env_file() {
    local template_file=$1
    local env_file=$2
    
    if [ ! -f "$env_file" ]; then
        if [ -f "$template_file" ]; then
            cp "$template_file" "$env_file"
            echo "✅ Created $env_file from template"
            echo "⚠️  Please edit $env_file with your actual values"
        else
            echo "❌ Template $template_file not found"
        fi
    else
        echo "ℹ️  $env_file already exists, skipping..."
    fi
}

# Setup backend environment
setup_env_file "backend/.env.template" "backend/.env"

# Setup frontend environment  
setup_env_file "frontend/.env.template" "frontend/.env"

echo ""
echo "🔐 Security Reminder:"
echo "- Never commit .env files to git"
echo "- Generate strong secrets for production"
echo "- Use different credentials for each environment"
echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env with your database credentials"
echo "2. Edit frontend/.env with your GitHub OAuth client ID"
echo "3. Generate secure random keys for production"