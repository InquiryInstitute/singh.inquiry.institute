# Route 53 Quick Setup for singh.inquiry.institute

## TL;DR - Quick Steps

1. **AWS Route 53 Console**: https://console.aws.amazon.com/route53/
2. **Open Hosted Zone**: Click on `inquiry.institute` hosted zone
3. **Create CNAME Record**:
   - Record name: `singh`
   - Record type: `CNAME`
   - Value: `inquiryinstitute.github.io`
   - TTL: `300`
4. **GitHub Pages**: Settings → Pages → Custom domain: `singh.inquiry.institute` → Enforce HTTPS
5. **Wait**: DNS propagation (5-30 min) + SSL certificate (up to 24 hours)

## Detailed Steps

### Step 1: Create CNAME Record in Route 53

1. Go to: https://console.aws.amazon.com/route53/
2. Click **"Hosted zones"** in left sidebar
3. Click on **`inquiry.institute`** hosted zone
4. Click **"Create record"**
5. Fill in:
   ```
   Record name: singh
   Record type: CNAME
   Value: inquiryinstitute.github.io
   TTL: 300
   ```
6. Click **"Create records"**

### Step 2: Configure GitHub Pages

1. Go to: https://github.com/InquiryInstitute/singh.inquiry.institute/settings/pages
2. Under **"Custom domain"**, enter: `singh.inquiry.institute`
3. Check **"Enforce HTTPS"**
4. Click **"Save"**

### Step 3: Verify DNS

```bash
# Check CNAME record
dig singh.inquiry.institute CNAME +short
# Expected: inquiryinstitute.github.io

# Or use online tool
# https://dnschecker.org/#CNAME/singh.inquiry.institute
```

### Step 4: Wait for SSL Certificate

- DNS propagation: Usually 5-30 minutes
- SSL certificate: Up to 24 hours after DNS is correct
- Check status in GitHub Pages settings

## Verification Checklist

- [ ] CNAME record created in Route 53
- [ ] Record shows: `singh` → `inquiryinstitute.github.io`
- [ ] Custom domain configured in GitHub Pages
- [ ] CNAME file exists in repository (already done)
- [ ] DNS propagates correctly (check with `dig`)
- [ ] SSL certificate provisioned (check GitHub Pages settings)
- [ ] Site accessible at https://singh.inquiry.institute

## Troubleshooting

**DNS not resolving?**
- Verify record name is `singh` (not `singh.inquiry.institute`)
- Check name servers point to Route 53
- Wait for propagation (up to 48 hours)

**HTTPS not working?**
- Wait for SSL certificate (up to 24 hours)
- Ensure "Enforce HTTPS" is enabled
- Verify DNS is correct first

**Need help?** See [AWS_ROUTE53_SETUP.md](./AWS_ROUTE53_SETUP.md) for detailed instructions.
