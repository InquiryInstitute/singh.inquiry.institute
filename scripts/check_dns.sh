#!/bin/bash
# Check DNS configuration for singh.inquiry.institute

echo "=== DNS Check for singh.inquiry.institute ==="
echo ""

# Check CNAME
echo "1. CNAME Record:"
CNAME=$(dig singh.inquiry.institute CNAME +short 2>&1)
if [ -z "$CNAME" ]; then
    echo "   ❌ NOT FOUND"
    echo "   → CNAME record doesn't exist in Route 53"
    echo ""
    echo "   Required record:"
    echo "     Name: singh"
    echo "     Type: CNAME"
    echo "     Value: inquiryinstitute.github.io"
else
    echo "   ✅ Found: $CNAME"
    if [ "$CNAME" = "inquiryinstitute.github.io." ]; then
        echo "   ✅ Correct value"
    else
        echo "   ⚠️  Value should be: inquiryinstitute.github.io"
    fi
fi

echo ""
echo "2. A Record:"
A=$(dig singh.inquiry.institute A +short 2>&1)
if [ -z "$A" ]; then
    echo "   ✅ No A record (correct for subdomain)"
else
    echo "   ⚠️  A record found: $A"
    echo "   → Should use CNAME instead for subdomain"
fi

echo ""
echo "3. Name Servers (inquiry.institute):"
NS=$(dig inquiry.institute NS +short 2>&1)
if echo "$NS" | grep -q "awsdns"; then
    echo "   ✅ Route 53 name servers configured"
    echo "$NS" | sed 's/^/     /'
else
    echo "   ⚠️  Name servers may not be Route 53"
fi

echo ""
echo "=== GitHub Pages Status ==="
gh api repos/InquiryInstitute/singh.inquiry.institute/pages --jq '"Custom Domain: \(.cname)\nBuild Type: \(.build_type)\nURL: \(.html_url)"' 2>&1 | sed 's/^/   /'

echo ""
if [ -z "$CNAME" ]; then
    echo "=== ACTION REQUIRED ==="
    echo "Create CNAME record in Route 53:"
    echo "  1. Go to: https://console.aws.amazon.com/route53/"
    echo "  2. Hosted zones → inquiry.institute"
    echo "  3. Create record:"
    echo "     - Name: singh"
    echo "     - Type: CNAME"
    echo "     - Value: inquiryinstitute.github.io"
    echo "     - TTL: 300"
    echo ""
    echo "After creating, wait 5-30 minutes for DNS propagation."
else
    echo "=== DNS Configured ==="
    echo "If site still shows 404, wait for DNS propagation (5-30 min)"
fi
