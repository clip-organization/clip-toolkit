#!/bin/bash

echo "🔍 Debugging TypeScript Build Issues"
echo "===================================="

echo ""
echo "📦 Checking package structure..."
find packages -name "tsconfig*.json" -type f | sort

echo ""
echo "🏗️ Checking build outputs..."
find packages -name "dist" -type d | while read dir; do
    echo "  $dir:"
    ls -la "$dir" 2>/dev/null | head -5 || echo "    (empty or missing)"
done

echo ""
echo "🔗 Checking project references..."
grep -r "references" packages/*/tsconfig*.json 2>/dev/null || echo "  No references found"

echo ""
echo "⚙️ Running clean build..."
npm run clean
npm run build:verbose

echo ""
echo "✅ Build completed. Check output above for errors." 