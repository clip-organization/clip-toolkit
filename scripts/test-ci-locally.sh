#!/bin/bash
# Script to test GitHub Actions workflow locally

echo "🧪 Testing GitHub Actions workflow locally..."
echo "This simulates what happens in the CI pipeline"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run a step
run_step() {
    local step_name=$1
    local command=$2
    echo -e "${YELLOW}▶ Running: $step_name${NC}"
    echo "  Command: $command"
    
    if eval "$command"; then
        echo -e "${GREEN}✓ $step_name passed${NC}\n"
        return 0
    else
        echo -e "${RED}✗ $step_name failed${NC}\n"
        return 1
    fi
}

# Clean environment
echo "🧹 Cleaning environment..."
rm -rf node_modules packages/*/node_modules packages/*/dist

# Setup
run_step "Install dependencies" "npm ci"

# Lint
echo "🔍 Testing lint job..."
for package in encoder-cli decoder-lib validator-core; do
    run_step "Lint $package" "cd packages/$package && npm run lint && cd ../.."
done

# Type checking
echo "📝 Testing type checking..."
run_step "TypeScript build (all packages)" "npm run build"

# Test
echo "🧪 Testing test job..."
for package in encoder-cli decoder-lib validator-core; do
    run_step "Test $package" "cd packages/$package && npm test && cd ../.."
done

# Build individual packages (like GitHub Actions does)
echo "🏗️ Testing individual package builds..."
for package in encoder-cli decoder-lib validator-core; do
    # Clean first
    rm -rf packages/$package/dist
    
    # Build all (to ensure dependencies are built)
    run_step "Build for $package" "npm run build"
    
    # Check if dist exists
    if [ -d "packages/$package/dist" ]; then
        echo -e "${GREEN}✓ $package has dist directory${NC}"
    else
        echo -e "${RED}✗ $package missing dist directory${NC}"
    fi
done

echo ""
echo "🎉 Local CI test complete!"
echo "If all steps passed, your GitHub Actions workflow should succeed." 