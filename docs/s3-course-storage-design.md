# S3 Course Storage Design

## Overview
Store Khan Academy, MIT OCW, and other course content in S3 with manifest files for extensibility.

## S3 Structure

```
s3://singh-courses/
├── manifest.json                    # Master manifest of all courses
├── sources/
│   ├── khan-academy/
│   │   ├── manifest.json            # Khan Academy courses manifest
│   │   ├── courses/
│   │   │   ├── algebra-basics/
│   │   │   │   ├── metadata.json    # Course metadata
│   │   │   │   ├── videos/
│   │   │   │   │   ├── video-1/
│   │   │   │   │   │   ├── transcript.json
│   │   │   │   │   │   ├── transcript_dialogic.json
│   │   │   │   │   │   └── metadata.json
│   │   │   │   │   └── video-2/...
│   │   │   │   └── assets/          # Images, PDFs, etc.
│   │   │   └── geometry-intro/...
│   │   └── subjects/
│   │       ├── math.json
│   │       ├── science.json
│   │       └── ...
│   ├── mit-ocw/
│   │   ├── manifest.json
│   │   ├── courses/
│   │   │   ├── 18-01-single-variable-calculus/
│   │   │   │   ├── metadata.json
│   │   │   │   ├── lectures/
│   │   │   │   │   ├── lecture-1/
│   │   │   │   │   │   ├── transcript.json
│   │   │   │   │   │   ├── transcript_dialogic.json
│   │   │   │   │   │   ├── video.mp4 (or reference)
│   │   │   │   │   │   └── slides.pdf
│   │   │   │   │   └── ...
│   │   │   │   └── syllabus.json
│   │   │   │   └── assignments/
│   │   │   │       └── ...
│   │   │   └── ...
│   │   └── subjects/
│   └── custom/
│       └── ...
└── cache/
    └── ...                          # Cached processed transcripts
```

## Manifest Structure

### Master Manifest (`manifest.json`)
```json
{
  "version": "1.0",
  "last_updated": "2025-01-20T12:00:00Z",
  "sources": [
    {
      "id": "khan-academy",
      "name": "Khan Academy",
      "manifest_path": "sources/khan-academy/manifest.json",
      "course_count": 150,
      "last_synced": "2025-01-20T10:00:00Z"
    },
    {
      "id": "mit-ocw",
      "name": "MIT OpenCourseWare",
      "manifest_path": "sources/mit-ocw/manifest.json",
      "course_count": 2500,
      "last_synced": "2025-01-20T11:00:00Z"
    }
  ],
  "total_courses": 2650
}
```

### Source Manifest (`sources/khan-academy/manifest.json`)
```json
{
  "source_id": "khan-academy",
  "version": "1.0",
  "last_updated": "2025-01-20T10:00:00Z",
  "courses": [
    {
      "course_id": "algebra-basics",
      "title": "Introduction to Algebra",
      "subject": "Math",
      "topic": "Algebra",
      "level": "beginner",
      "path": "sources/khan-academy/courses/algebra-basics",
      "metadata_path": "sources/khan-academy/courses/algebra-basics/metadata.json",
      "video_count": 12,
      "duration_minutes": 180,
      "faculty_suggestions": ["a.gauss", "a.euler", "a.hypatia"],
      "tags": ["algebra", "variables", "equations"],
      "standards": {
        "common_core": ["A-CED.1", "A-REI.1"],
        "ngss": null
      }
    }
  ],
  "subjects": {
    "math": {
      "course_ids": ["algebra-basics", "geometry-intro", ...],
      "count": 45
    },
    "science": {
      "course_ids": ["biology-basics", ...],
      "count": 38
    }
  }
}
```

## Course Metadata Schema

### Khan Academy Course (`metadata.json`)
```json
{
  "course_id": "algebra-basics",
  "source": "khan-academy",
  "title": "Introduction to Algebra",
  "description": "An introduction to algebraic thinking and basic operations",
  "subject": "Math",
  "topic": "Algebra",
  "level": "beginner",
  "duration_minutes": 180,
  "video_count": 12,
  "created": "2025-01-15T00:00:00Z",
  "updated": "2025-01-20T00:00:00Z",
  "faculty_suggestions": ["a.gauss", "a.euler", "a.hypatia"],
  "tags": ["algebra", "variables", "equations"],
  "standards": {
    "common_core": ["A-CED.1", "A-REI.1"],
    "ngss": null
  },
  "videos": [
    {
      "video_id": "NybHckSEQBI",
      "youtube_id": "NybHckSEQBI",
      "title": "Introduction to variables",
      "order": 1,
      "duration_seconds": 600,
      "transcript_path": "videos/video-1/transcript_dialogic.json",
      "metadata_path": "videos/video-1/metadata.json"
    }
  ],
  "prerequisites": [],
  "learning_objectives": [
    "Understand what variables are",
    "Solve basic equations"
  ]
}
```

### MIT OCW Course (`metadata.json`)
```json
{
  "course_id": "18-01-single-variable-calculus",
  "source": "mit-ocw",
  "title": "Single Variable Calculus",
  "description": "Introduction to differential and integral calculus",
  "subject": "Mathematics",
  "department": "Mathematics",
  "course_number": "18.01",
  "level": "undergraduate",
  "semester": "Fall",
  "year": 2020,
  "instructor": "Prof. David Jerison",
  "duration_hours": 39,
  "lecture_count": 39,
  "created": "2025-01-10T00:00:00Z",
  "updated": "2025-01-20T00:00:00Z",
  "faculty_suggestions": ["a.newton", "a.euler", "a.leibniz"],
  "tags": ["calculus", "derivatives", "integrals"],
  "lectures": [
    {
      "lecture_id": "lecture-1",
      "title": "Derivatives, slope, velocity, rate of change",
      "order": 1,
      "duration_minutes": 50,
      "transcript_path": "lectures/lecture-1/transcript_dialogic.json",
      "video_path": "lectures/lecture-1/video.mp4",
      "slides_path": "lectures/lecture-1/slides.pdf"
    }
  ],
  "syllabus_path": "syllabus.json",
  "assignments_path": "assignments/",
  "prerequisites": ["18.00"],
  "learning_objectives": [
    "Understand limits and continuity",
    "Compute derivatives"
  ]
}
```

## Transcript Format

### Dialogic Transcript (`transcript_dialogic.json`)
```json
{
  "course_id": "algebra-basics",
  "video_id": "NybHckSEQBI",
  "source": "khan-academy",
  "title": "Introduction to variables",
  "segments": [
    {
      "segment_id": 1,
      "text": "Welcome to algebra. Today we'll explore the fundamental concepts of variables.",
      "start_time": 0,
      "end_time": 8,
      "duration": 8,
      "allows_questions": true,
      "pause_duration": 2000,
      "topic_marker": "introduction"
    }
  ],
  "total_segments": 8,
  "total_duration": 60,
  "metadata": {
    "format_version": "1.0",
    "processed": "2025-01-20T00:00:00Z"
  }
}
```

## API Design

### Course Listing
```
GET /api/courses?source=khan-academy&subject=math&level=beginner
```

### Course Details
```
GET /api/courses/{course_id}
```

### Transcript
```
GET /api/courses/{course_id}/transcript
GET /api/courses/{course_id}/videos/{video_id}/transcript
```

## Implementation Plan

1. **S3 Bucket Setup**
   - Create `singh-courses` bucket
   - Set up IAM policies
   - Configure CORS for web access

2. **Manifest Generation**
   - Script to generate master manifest
   - Script to generate source manifests
   - Update on course additions

3. **Course Loader**
   - S3 client for fetching manifests
   - Course metadata loader
   - Transcript loader with caching

4. **Migration**
   - Move existing sample courses to S3
   - Update frontend to use S3 loader
   - Add fallback to local files

5. **Extensibility**
   - Generic course interface
   - Source-specific adapters
   - MIT OCW integration
