# SSL and DNS Fix

## Issue
SSL certificate warning: The certificate is for `*.github.io` but the domain is `singh.inquiry.institute`, causing SSL verification errors.

## Current Status
- ✅ DNS CNAME: `singh.inquiry.institute` → `inquiryinstitute.github.io` (correct)
- ✅ Domain verified: `protected_domain_state: "verified"`
- ⚠️ HTTPS enforced: `false` (needs to be enabled)
- ⚠️ SSL certificate: Not yet provisioned for custom domain

## Fix Applied
1. Enabled HTTPS enforcement via GitHub API
2. GitHub Pages will now provision SSL certificate for the custom domain

## Next Steps
1. Wait 5-10 minutes for GitHub to provision the SSL certificate
2. The certificate will be automatically issued by Let's Encrypt
3. Once provisioned, HTTPS will work without warnings

## Verification
```bash
# Check HTTPS enforcement
gh api repos/InquiryInstitute/singh.inquiry.institute/pages | jq '.https_enforced'

# Test SSL
curl -I https://singh.inquiry.institute

# Check DNS
dig singh.inquiry.institute +short
```

## Note
GitHub Pages automatically provisions SSL certificates for verified custom domains, but it can take a few minutes after enabling HTTPS enforcement.
