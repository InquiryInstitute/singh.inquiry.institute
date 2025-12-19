# AWS Route 53 Setup for singh.inquiry.institute

This guide provides step-by-step instructions for configuring AWS Route 53 to point your custom domain to GitHub Pages.

## Prerequisites

- AWS account with Route 53 access
- Domain `inquiry.institute` registered (or access to manage DNS for it)
- GitHub Pages site deployed and accessible
- Repository: `InquiryInstitute/singh.inquiry.institute`

## Step 1: Determine Your Setup

Since `singh.inquiry.institute` is a **subdomain**, we have two options:

### Option A: Use Existing `inquiry.institute` Hosted Zone (Recommended)
If you already have a Route 53 hosted zone for `inquiry.institute`, simply add a CNAME record for the `singh` subdomain.

### Option B: Create New Hosted Zone for Subdomain
If you need a separate hosted zone (not recommended for subdomains), create one for `singh.inquiry.institute`.

**We'll use Option A** - adding a record to the existing `inquiry.institute` hosted zone.

## Step 2: Get GitHub Pages URL

For project pages under the `InquiryInstitute` organization, the GitHub Pages URL is:
- **Project Pages**: `inquiryinstitute.github.io/singh.inquiry.institute` (if using project pages)
- **Custom Domain**: `singh.inquiry.institute` (once configured)

For CNAME record, we'll use: **`inquiryinstitute.github.io`** (organization GitHub Pages URL)

**Note**: If the repository uses project pages, the actual URL might be different. Check your GitHub Pages settings.

## Step 3: Access Route 53 Hosted Zone

1. Log in to AWS Console: https://console.aws.amazon.com/route53/
2. Click "Hosted zones" in the left sidebar
3. Find and click on the hosted zone for **`inquiry.institute`**
   - If it doesn't exist, see "Alternative: Create New Hosted Zone" below

## Step 4: Create CNAME Record for singh Subdomain

1. In the `inquiry.institute` hosted zone, click **"Create record"**
2. Configure the record:
   - **Record name**: `singh` (this creates `singh.inquiry.institute`)
   - **Record type**: `CNAME - Routes traffic to another domain name and some AWS resources`
   - **Value**: `inquiryinstitute.github.io`
   - **TTL**: `300` (5 minutes) or use default
   - **Routing policy**: Simple routing
3. Click **"Create records"**

**Important**: The record name should be just `singh` (not `singh.inquiry.institute`), as Route 53 automatically appends the domain name from the hosted zone.

### Alternative: If Using Project Pages

If your GitHub Pages uses project pages format, the CNAME value should be:
- `inquiryinstitute.github.io` (for organization pages)
- Or check your actual GitHub Pages URL in repository Settings → Pages

## Alternative: Create New Hosted Zone (Not Recommended)

If you don't have a hosted zone for `inquiry.institute` and need to create one:

1. In Route 53, click "Create hosted zone"
2. Enter domain name: `inquiry.institute`
3. Choose "Public hosted zone"
4. Click "Create hosted zone"
5. **Important**: Update name servers at your domain registrar to point to Route 53 name servers
6. Then follow Step 4 above to create the CNAME record

## Step 5: Configure GitHub Pages Custom Domain

1. Go to your GitHub repository: `https://github.com/InquiryInstitute/singh.inquiry.institute`
2. Navigate to **Settings** → **Pages**
3. Under "Custom domain", enter: `singh.inquiry.institute`
4. Check **"Enforce HTTPS"** (recommended)
5. Click **"Save"**
6. GitHub will verify the domain and create/update the CNAME file in your repository

**Note**: The CNAME file has already been created in this repository at the root level. GitHub will use it automatically.

## Step 6: Update Name Servers (if needed)

If your domain `inquiry.institute` is registered with a different registrar and you're using Route 53:

1. In Route 53, go to your `inquiry.institute` hosted zone
2. Note the 4 name server addresses displayed (e.g., `ns-123.awsdns-12.com`, `ns-456.awsdns-45.net`, etc.)
3. Go to your domain registrar's control panel (where you registered `inquiry.institute`)
4. Find the DNS/Name Server settings
5. Update the name servers to the Route 53 name servers provided
6. Save changes

**Note**: If name servers are already pointing to Route 53, skip this step.

## Step 7: Verify DNS Propagation

Wait for DNS propagation (can take 5 minutes to 48 hours, usually 15-30 minutes):

### Using Command Line

```bash
# Check CNAME record
dig singh.inquiry.institute CNAME +short

# Expected output: inquiryinstitute.github.io

# Check full DNS resolution
dig singh.inquiry.institute +short

# Check name servers
dig inquiry.institute NS +short
```

### Using Online Tools

- **DNS Checker**: https://dnschecker.org/#CNAME/singh.inquiry.institute
- **What's My DNS**: https://www.whatsmydns.net/#CNAME/singh.inquiry.institute
- **DNS Propagation**: https://dnspropagation.net/

### Verify in Route 53

1. Go to your `inquiry.institute` hosted zone
2. Look for the `singh` CNAME record
3. Verify it shows `inquiryinstitute.github.io` as the value

## Step 8: SSL Certificate (HTTPS)

GitHub Pages automatically provisions SSL certificates via Let's Encrypt for custom domains. 

**Timeline**:
1. DNS propagates (5 minutes - 48 hours)
2. GitHub detects the custom domain (usually within 1 hour after DNS propagation)
3. Let's Encrypt certificate is provisioned (can take up to 24 hours)
4. HTTPS becomes available automatically

**To check status**:
- Go to repository **Settings** → **Pages**
- Look for the custom domain status indicator
- Green checkmark = DNS configured correctly
- "Certificate is being provisioned" = wait for certificate
- "Enforce HTTPS" checkbox will become available once certificate is ready

## Quick Setup Checklist

- [ ] Access Route 53 console
- [ ] Open `inquiry.institute` hosted zone (or create if needed)
- [ ] Create CNAME record: `singh` → `inquiryinstitute.github.io`
- [ ] Verify name servers at domain registrar point to Route 53
- [ ] Configure custom domain in GitHub Pages: `singh.inquiry.institute`
- [ ] Enable "Enforce HTTPS" in GitHub Pages settings
- [ ] Wait for DNS propagation (check with `dig` or online tools)
- [ ] Wait for SSL certificate provisioning (up to 24 hours)
- [ ] Test site: https://singh.inquiry.institute

## Troubleshooting

### Domain not resolving

**Check DNS records:**
```bash
dig singh.inquiry.institute CNAME
# Should return: inquiryinstitute.github.io
```

**Common issues:**
- CNAME record name should be `singh` (not `singh.inquiry.institute`)
- Verify the record exists in the correct hosted zone
- Check name servers are pointing to Route 53
- Wait for DNS propagation (can take up to 48 hours)

### HTTPS not working

**Check certificate status:**
1. Go to GitHub repository → Settings → Pages
2. Look for custom domain status
3. Check if "Enforce HTTPS" is available and enabled

**Common issues:**
- DNS must be fully propagated before certificate can be issued
- Certificate provisioning can take up to 24 hours
- Ensure "Enforce HTTPS" is checked in GitHub Pages settings
- Verify CNAME record is correct

### CNAME conflicts

- Ensure no duplicate CNAME records exist
- Check for conflicting A records (remove if present)
- Verify the record is in the correct hosted zone

### GitHub Pages not detecting domain

- Ensure CNAME file exists in repository root with content: `singh.inquiry.institute`
- Verify DNS is resolving correctly
- Check GitHub Pages settings show the custom domain
- Wait a few minutes after DNS changes for GitHub to detect

### Still having issues?

1. **Verify Route 53 record:**
   - Record name: `singh`
   - Record type: `CNAME`
   - Value: `inquiryinstitute.github.io`

2. **Check GitHub Pages:**
   - Custom domain: `singh.inquiry.institute`
   - CNAME file exists in repo
   - Pages source is set to GitHub Actions

3. **Test DNS:**
   ```bash
   dig singh.inquiry.institute CNAME +short
   # Should return: inquiryinstitute.github.io
   ```

## Additional Resources

- [GitHub Pages Custom Domain Documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [AWS Route 53 Documentation](https://docs.aws.amazon.com/route53/)
- [DNS Propagation Checker](https://dnschecker.org)
