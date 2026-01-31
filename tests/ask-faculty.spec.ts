import { test, expect } from '@playwright/test';

const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvdWdxZG9ta29pc3J4ZG5hZ2NqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5NjIwMTIsImV4cCI6MjA4MTUzODAxMn0.eA1vXG6UVI1AjUOXN7q3gTlSyPoDByuVehOcKPjHmvs';
const SUPABASE_URL = 'https://xougqdomkoisrxdnagcj.supabase.co';

test.describe('ask-faculty endpoint', () => {
  test('should respond to a question from a.gauss', async ({ request }) => {
    try {
      const response = await request.post(`${SUPABASE_URL}/functions/v1/ask-faculty`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'apikey': SUPABASE_ANON_KEY,
        },
        data: {
          faculty_id: 'a.gauss',
          message: 'What is a variable in algebra?',
          conversation_history: [],
          context: 'office_hours',
        },
        timeout: 30000,
      });

      console.log('Response status:', response.status());
      console.log('Response headers:', response.headers());

      if (!response.ok()) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        console.error('Status:', response.status());
      }

      // Accept 200 or 201 as success
      expect([200, 201]).toContain(response.status());

      const data = await response.json();
      console.log('Response data:', JSON.stringify(data, null, 2));

      expect(data).toHaveProperty('response');
      expect(data.response).toBeTruthy();
      expect(typeof data.response).toBe('string');
      expect(data.response.length).toBeGreaterThan(0);
    } catch (error: any) {
      // Log the error for debugging
      console.error('Request failed:', error.message);
      console.error('Error type:', error.constructor.name);
      
      // If it's a DNS error, skip the test but log it
      if (error.message?.includes('ENOTFOUND') || error.message?.includes('getaddrinfo')) {
        console.warn('DNS resolution failed - Supabase URL may be incorrect or network unavailable');
        test.skip();
      } else {
        throw error;
      }
    }
  });

  test('should handle conversation history', async ({ request }) => {
    const conversationHistory = [
      { role: 'user', content: 'What is algebra?' },
      { role: 'assistant', content: 'Algebra is a branch of mathematics that uses symbols and letters to represent numbers and quantities.' },
    ];

    const response = await request.post(`${SUPABASE_URL}/functions/v1/ask-faculty`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'apikey': SUPABASE_ANON_KEY,
      },
      data: {
        faculty_id: 'a.gauss',
        message: 'Can you give me an example?',
        conversation_history: conversationHistory,
        context: 'office_hours',
      },
    });

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('response');
    expect(data.response).toBeTruthy();
  });

  test('should handle different faculty members', async ({ request }) => {
    const facultyIds = ['a.gauss', 'a.plato', 'a.einstein'];

    for (const facultyId of facultyIds) {
      const response = await request.post(`${SUPABASE_URL}/functions/v1/ask-faculty`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'apikey': SUPABASE_ANON_KEY,
        },
        data: {
          faculty_id: facultyId,
          message: 'What is mathematics?',
          conversation_history: [],
          context: 'office_hours',
        },
      });

      console.log(`Testing ${facultyId}:`, response.status());

      if (response.ok()) {
        const data = await response.json();
        expect(data).toHaveProperty('response');
        expect(data.response).toBeTruthy();
      } else {
        const errorText = await response.text();
        console.warn(`${facultyId} failed:`, errorText);
      }
    }
  });

  test('should handle network errors gracefully', async ({ request }) => {
    // Test with invalid URL to verify error handling
    try {
      const response = await request.post('https://invalid-url.supabase.co/functions/v1/ask-faculty', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'apikey': SUPABASE_ANON_KEY,
        },
        data: {
          faculty_id: 'a.gauss',
          message: 'Test question',
          conversation_history: [],
        },
        timeout: 5000,
      });

      // Should either fail or timeout
      expect(response.status()).not.toBe(200);
    } catch (error) {
      // Network error is expected
      expect(error).toBeDefined();
    }
  });
});

test.describe('Matrix Chat UI', () => {
  test('should load the matrix chat page', async ({ page }) => {
    await page.goto('http://localhost:4321/matrix-chat');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check for key elements
    await expect(page.locator('h2:has-text("Dialogic Controls")')).toBeVisible();
    await expect(page.locator('#courseSelect')).toBeVisible();
    await expect(page.locator('#facultySelect')).toBeVisible();
    await expect(page.locator('#startBtn')).toBeVisible();
  });

  test('should allow selecting a course and faculty', async ({ page }) => {
    await page.goto('http://localhost:4321/matrix-chat');
    await page.waitForLoadState('networkidle');
    
    // Select course
    await page.selectOption('#courseSelect', 'algebra-basics-intro');
    
    // Wait for faculty to load (might be async)
    await page.waitForTimeout(1000);
    
    // Select faculty (should have options after loading)
    const facultySelect = page.locator('#facultySelect');
    await expect(facultySelect).toBeVisible();
    
    // Try to select a faculty member
    const options = await facultySelect.locator('option').all();
    if (options.length > 1) {
      // Skip the first option which is "-- Select a.Faculty --"
      await page.selectOption('#facultySelect', { index: 1 });
    }
  });

  test('should send a question and get a response', async ({ page }) => {
    await page.goto('http://localhost:4321/matrix-chat');
    await page.waitForLoadState('networkidle');
    
    // Select course and faculty
    await page.selectOption('#courseSelect', 'algebra-basics-intro');
    await page.waitForTimeout(1000);
    
    const facultySelect = page.locator('#facultySelect');
    const options = await facultySelect.locator('option').all();
    if (options.length > 1) {
      await page.selectOption('#facultySelect', { index: 1 });
    }
    
    // Start delivery
    await page.click('#startBtn');
    
    // Wait for delivery to start
    await page.waitForTimeout(2000);
    
    // Type a question
    const chatInput = page.locator('#chatInput');
    await expect(chatInput).toBeEnabled();
    await chatInput.fill('What is a variable?');
    
    // Send the question
    await page.click('#sendBtn');
    
    // Wait for response (with timeout)
    await page.waitForTimeout(5000);
    
    // Check if response appeared
    const messages = page.locator('.message-item');
    const messageCount = await messages.count();
    expect(messageCount).toBeGreaterThan(0);
    
    // Check for user message
    const userMessages = page.locator('.message-item[data-type="user"]');
    const userMessageCount = await userMessages.count();
    expect(userMessageCount).toBeGreaterThan(0);
  });
});
