#!/bin/bash
# Check GitHub Pages workflow status

echo "=== GitHub Pages Workflow Check ==="
echo ""

# Check if workflow file exists
if [ -f ".github/workflows/pages.yml" ]; then
    echo "✅ Workflow file exists: .github/workflows/pages.yml"
else
    echo "❌ Workflow file missing!"
    exit 1
fi

# Check workflow syntax
echo ""
echo "=== Workflow File Contents ==="
cat .github/workflows/pages.yml

echo ""
echo "=== Required Files Check ==="

# Check for index.html
if [ -f "index.html" ]; then
    echo "✅ index.html exists"
else
    echo "❌ index.html missing!"
fi

# Check for .nojekyll
if [ -f ".nojekyll" ]; then
    echo "✅ .nojekyll exists"
else
    echo "❌ .nojekyll missing!"
fi

# Check for CNAME
if [ -f "CNAME" ]; then
    echo "✅ CNAME exists"
    echo "   Content: $(cat CNAME)"
else
    echo "❌ CNAME missing!"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Check GitHub Actions: https://github.com/InquiryInstitute/singh.inquiry.institute/actions"
echo "2. Verify Pages settings: https://github.com/InquiryInstitute/singh.inquiry.institute/settings/pages"
echo "3. Source should be: GitHub Actions"
echo "4. Custom domain: singh.inquiry.institute"
