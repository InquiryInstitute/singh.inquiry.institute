/**
 * S3 Course Loader
 * 
 * Loads courses from S3 with manifest-based discovery.
 * Supports Khan Academy, MIT OCW, and extensible to other sources.
 */

export class S3CourseLoader {
  constructor(options = {}) {
    this.bucket = options.bucket || 'singh-courses';
    this.region = options.region || 'us-east-1';
    this.baseUrl = options.baseUrl || `https://${this.bucket}.s3.${this.region}.amazonaws.com`;
    this.cache = new Map();
    this.cacheTimeout = options.cacheTimeout || 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Get master manifest
   */
  async getMasterManifest() {
    const cacheKey = 'master-manifest';
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${this.baseUrl}/manifest.json`);
      if (!response.ok) throw new Error(`Failed to fetch manifest: ${response.status}`);
      
      const manifest = await response.json();
      this.cache.set(cacheKey, { data: manifest, timestamp: Date.now() });
      return manifest;
    } catch (error) {
      console.error('Failed to load master manifest:', error);
      // Return empty manifest as fallback
      return { version: '1.0', sources: [], total_courses: 0 };
    }
  }

  /**
   * Get source manifest
   */
  async getSourceManifest(sourceId) {
    const cacheKey = `source-manifest-${sourceId}`;
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const masterManifest = await this.getMasterManifest();
      const source = masterManifest.sources?.find(s => s.id === sourceId);
      if (!source) {
        throw new Error(`Source not found: ${sourceId}`);
      }

      const response = await fetch(`${this.baseUrl}/${source.manifest_path}`);
      if (!response.ok) throw new Error(`Failed to fetch source manifest: ${response.status}`);
      
      const manifest = await response.json();
      this.cache.set(cacheKey, { data: manifest, timestamp: Date.now() });
      return manifest;
    } catch (error) {
      console.error(`Failed to load source manifest for ${sourceId}:`, error);
      return { source_id: sourceId, courses: [] };
    }
  }

  /**
   * List courses by source and filters
   */
  async listCourses(options = {}) {
    const { source, subject, level, tags } = options;
    
    if (source) {
      const sourceManifest = await this.getSourceManifest(source);
      let courses = sourceManifest.courses || [];

      // Apply filters
      if (subject) {
        courses = courses.filter(c => c.subject === subject || c.subject?.toLowerCase() === subject.toLowerCase());
      }
      if (level) {
        courses = courses.filter(c => c.level === level);
      }
      if (tags && Array.isArray(tags)) {
        courses = courses.filter(c => 
          tags.some(tag => c.tags?.includes(tag))
        );
      }

      return courses;
    }

    // If no source specified, return all courses from all sources
    const masterManifest = await this.getMasterManifest();
    const allCourses = [];

    for (const sourceInfo of masterManifest.sources || []) {
      try {
        const sourceManifest = await this.getSourceManifest(sourceInfo.id);
        const courses = sourceManifest.courses || [];
        allCourses.push(...courses.map(c => ({ ...c, source: sourceInfo.id })));
      } catch (error) {
        console.warn(`Failed to load courses from ${sourceInfo.id}:`, error);
      }
    }

    return allCourses;
  }

  /**
   * Get course metadata
   */
  async getCourseMetadata(courseId, sourceId = null) {
    const cacheKey = `course-metadata-${courseId}-${sourceId || 'any'}`;
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      // If source not provided, find it
      if (!sourceId) {
        const masterManifest = await this.getMasterManifest();
        for (const sourceInfo of masterManifest.sources || []) {
          const sourceManifest = await this.getSourceManifest(sourceInfo.id);
          const course = sourceManifest.courses?.find(c => c.course_id === courseId);
          if (course) {
            sourceId = sourceInfo.id;
            break;
          }
        }
      }

      if (!sourceId) {
        throw new Error(`Course not found: ${courseId}`);
      }

      const sourceManifest = await this.getSourceManifest(sourceId);
      const courseInfo = sourceManifest.courses?.find(c => c.course_id === courseId);
      if (!courseInfo) {
        throw new Error(`Course not found: ${courseId}`);
      }

      const response = await fetch(`${this.baseUrl}/${courseInfo.metadata_path}`);
      if (!response.ok) throw new Error(`Failed to fetch course metadata: ${response.status}`);
      
      const metadata = await response.json();
      this.cache.set(cacheKey, { data: metadata, timestamp: Date.now() });
      return metadata;
    } catch (error) {
      console.error(`Failed to load course metadata for ${courseId}:`, error);
      throw error;
    }
  }

  /**
   * Get course transcript (all videos combined)
   */
  async getCourseTranscript(courseId, sourceId = null) {
    try {
      const metadata = await this.getCourseMetadata(courseId, sourceId);
      const allSegments = [];
      let segmentIdCounter = 1;

      // Load transcripts for all videos/lectures
      const contentItems = metadata.videos || metadata.lectures || [];
      
      for (const item of contentItems) {
        try {
          const transcriptPath = item.transcript_path || item.transcript_dialogic_path;
          if (!transcriptPath) continue;

          const response = await fetch(`${this.baseUrl}/${metadata.path || ''}/${transcriptPath}`);
          if (!response.ok) {
            console.warn(`Failed to load transcript for ${item.video_id || item.lecture_id}:`, response.status);
            continue;
          }

          const videoTranscript = await response.json();
          
          // Add transition marker if not first video
          if (allSegments.length > 0 && videoTranscript.segments?.length > 0) {
            allSegments.push({
              segment_id: segmentIdCounter++,
              text: `Now let's move on to: ${item.title}`,
              allows_questions: true,
              pause_duration: 2000,
              topic_marker: `video-${item.order || segmentIdCounter}`,
              is_transition: true
            });
          }

          // Add all segments from this video
          if (videoTranscript.segments) {
            videoTranscript.segments.forEach(segment => {
              allSegments.push({
                ...segment,
                segment_id: segmentIdCounter++,
                video_order: item.order,
                video_title: item.title,
                video_id: item.video_id || item.lecture_id
              });
            });
          }
        } catch (error) {
          console.error(`Error loading transcript for ${item.video_id || item.lecture_id}:`, error);
        }
      }

      return {
        course_id: courseId,
        source: sourceId || metadata.source,
        segments: allSegments,
        total_segments: allSegments.length,
        metadata: metadata
      };
    } catch (error) {
      console.error(`Failed to load course transcript for ${courseId}:`, error);
      throw error;
    }
  }

  /**
   * Get single video/lecture transcript
   */
  async getVideoTranscript(courseId, videoId, sourceId = null) {
    try {
      const metadata = await this.getCourseMetadata(courseId, sourceId);
      const video = (metadata.videos || metadata.lectures || []).find(
        v => (v.video_id === videoId) || (v.lecture_id === videoId) || (v.youtube_id === videoId)
      );

      if (!video) {
        throw new Error(`Video not found: ${videoId}`);
      }

      const transcriptPath = video.transcript_path || video.transcript_dialogic_path;
      if (!transcriptPath) {
        throw new Error(`No transcript path for video: ${videoId}`);
      }

      const response = await fetch(`${this.baseUrl}/${metadata.path || ''}/${transcriptPath}`);
      if (!response.ok) throw new Error(`Failed to fetch transcript: ${response.status}`);

      return await response.json();
    } catch (error) {
      console.error(`Failed to load video transcript for ${videoId}:`, error);
      throw error;
    }
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }
}

// Default instance
export const courseLoader = new S3CourseLoader();
