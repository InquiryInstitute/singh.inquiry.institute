# singh.inquiry.institute

Repository for Singh Inquiry Institute project - Khan Academy content collection and aFaculty integration with dialogic delivery.

## Overview

This repository contains tools and infrastructure for:
- **Collecting all Khan Academy videos and transcripts** - Comprehensive cataloging and download pipeline
- **Mapping content to aFaculty personas** - Connecting Khan Academy courses to teaching assistants
- **Dialogic delivery via Matrix chat** - Delivering Khan Academy content in an interruptible, dialogic format using the [dialogic](https://github.com/InquiryInstitute/dialogic) library

## Project Structure

```
singh.inquiry.institute/
├── src/
│   ├── pages/              # Astro pages
│   │   ├── index.astro     # Main page
│   │   └── matrix-chat.astro  # Dialogic delivery interface
│   └── layouts/            # Astro layouts
├── data/                    # Collected data (gitignored)
│   ├── videos/             # Downloaded video files
│   ├── transcripts/        # Processed transcripts
│   ├── metadata/           # Catalogs and metadata
│   └── exercises/          # Exercise data
├── public/                  # Static assets (deployed)
│   └── data/               # Public transcript data
├── scripts/                 # Main execution scripts
├── docs/                    # Documentation
└── .github/                 # GitHub workflows (Pages deployment)
```

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Using Dialogic Library

The Matrix chat page uses the [dialogic](https://github.com/InquiryInstitute/dialogic) JavaScript library:

```javascript
import { Dialogic, DialogicAPI } from 'https://cdn.jsdelivr.net/gh/InquiryInstitute/dialogic@main/src/index.js';

const dialogic = new Dialogic({
  matrixServer: 'https://matrix.inquiry.institute',
  apiUrl: 'https://xougqdomkoisrxdnagcj.supabase.co/functions/v1',
  apiKey: 'your-api-key'
});

await dialogic.initialize(roomId, segments, facultyId);
await dialogic.start();
```

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch.

- **Custom domain**: `singh.inquiry.institute`
- **Build**: Astro static site generation
- **Workflow**: `.github/workflows/pages.yml`

## Technology Stack

- **Framework**: Astro (static site generation)
- **Styling**: Tailwind CSS
- **Dialogic Library**: [@inquiry-institute/dialogic](https://github.com/InquiryInstitute/dialogic)
- **Deployment**: GitHub Pages

## Related Projects

- [dialogic](https://github.com/InquiryInstitute/dialogic) - JavaScript library for dialogic delivery
- [Inquiry.Institute](https://github.com/InquiryInstitute/Inquiry.Institute) - Main platform

## Documentation

- [Khan Academy API Documentation](./docs/KHAN_ACADEMY_API.md) - API endpoints and data structures
- [Google Cloud Storage Setup](./docs/GCS_SETUP.md) - GCS bucket configuration and usage
- [Transcript Status](./TRANSCRIPT_STATUS.md) - Current transcript collection status

---

Project scaffold initialized on 2025-11-09.
