-- Add ElevenLabs voice prompt/ID field to faculty table
-- This allows each faculty member to have a unique voice for lecture delivery

-- Add elevenlabs_voice_prompt column to faculty table
-- (This will be applied to the main Inquiry.Institute Supabase instance)
ALTER TABLE IF EXISTS public.faculty 
ADD COLUMN IF NOT EXISTS elevenlabs_voice_id text;

ALTER TABLE IF EXISTS public.faculty 
ADD COLUMN IF NOT EXISTS elevenlabs_voice_prompt text;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_faculty_elevenlabs_voice_id 
ON public.faculty(elevenlabs_voice_id) 
WHERE elevenlabs_voice_id IS NOT NULL;

-- Add comments
COMMENT ON COLUMN public.faculty.elevenlabs_voice_id IS 'ElevenLabs voice ID for text-to-speech generation';
COMMENT ON COLUMN public.faculty.elevenlabs_voice_prompt IS 'Voice prompt/description for ElevenLabs voice cloning or selection';
