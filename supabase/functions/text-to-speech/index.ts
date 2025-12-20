// Supabase Edge Function for ElevenLabs Text-to-Speech
// Takes faculty name and text, retrieves voice prompt from database, and generates audio

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Get ElevenLabs API key from environment
    const ELEVENLABS_API_KEY = Deno.env.get('ELEVENLABS_API_KEY')
    if (!ELEVENLABS_API_KEY) {
      throw new Error('ELEVENLABS_API_KEY not set in Supabase function secrets')
    }

    // Parse request body
    const { faculty_name, text } = await req.json()

    if (!faculty_name || !text) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: faculty_name and text' }),
        { 
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Find faculty by name (search in given_name, surname, or id)
    const { data: faculty, error: facultyError } = await supabase
      .from('faculty')
      .select('id, given_name, surname, elevenlabs_voice_id, elevenlabs_voice_prompt')
      .or(`given_name.ilike.%${faculty_name}%,surname.ilike.%${faculty_name}%,id.ilike.%${faculty_name}%`)
      .eq('active', true)
      .limit(1)
      .single()

    if (facultyError || !faculty) {
      return new Response(
        JSON.stringify({ error: `Faculty not found: ${faculty_name}` }),
        { 
          status: 404,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Determine voice to use
    let voiceId = faculty.elevenlabs_voice_id
    let voicePrompt = faculty.elevenlabs_voice_prompt

    // If no voice_id, use default voice (Rachel - multilingual)
    if (!voiceId) {
      voiceId = '21m00Tcm4TlvDq8ikWAM' // Default ElevenLabs voice
    }

    // Voice settings
    const voiceSettings = {
      stability: 0.5,
      similarity_boost: 0.75,
      style: 0.0,
      use_speaker_boost: true
    }

    // Prepare text for TTS (use voice prompt if available to guide generation)
    let textToSpeak = text
    if (voicePrompt && !faculty.elevenlabs_voice_id) {
      // If using default voice but have a prompt, prepend context
      // Note: This is a simple approach; for better results, use voice cloning
      textToSpeak = text
    }

    // Call ElevenLabs API
    const elevenlabsUrl = `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`
    
    const response = await fetch(elevenlabsUrl, {
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': ELEVENLABS_API_KEY
      },
      body: JSON.stringify({
        text: textToSpeak,
        model_id: 'eleven_multilingual_v2',
        voice_settings: voiceSettings
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('ElevenLabs API error:', errorText)
      return new Response(
        JSON.stringify({ error: `ElevenLabs API error: ${errorText}` }),
        { 
          status: response.status,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Get audio blob
    const audioBlob = await response.blob()

    // Return audio as base64 for easier transport
    const arrayBuffer = await audioBlob.arrayBuffer()
    const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))

    return new Response(
      JSON.stringify({
        success: true,
        faculty_id: faculty.id,
        faculty_name: `${faculty.given_name || ''} ${faculty.surname || ''}`.trim(),
        voice_id: voiceId,
        audio_base64: base64Audio,
        audio_format: 'audio/mpeg'
      }),
      {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Error in text-to-speech function:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})
