// Call this module from server-side code so the API key stays private.
export async function generateText(prompt) {
  if (typeof prompt !== 'string' || !prompt.trim()) {
    throw new Error('Provide a non-empty text prompt.');
  }
  const apiKey = process.env.GEMINI_API_KEY?.trim();
  if (!apiKey || apiKey === 'your_google_ai_studio_api_key') {
    throw new Error('Set GEMINI_API_KEY in .env using a Google AI Studio API key.');
  }
  const model = process.env.GEMMA_MODEL?.trim() || 'gemma-4-26b-a4b-it';
  if (!['gemma-4-26b-a4b-it', 'gemma-4-31b-it'].includes(model)) {
    throw new Error('GEMMA_MODEL must be gemma-4-26b-a4b-it or gemma-4-31b-it.');
  }

  let response;
  try {
    response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-goog-api-key': apiKey },
        body: JSON.stringify({ contents: [{ role: 'user', parts: [{ text: prompt }] }] }),
        signal: AbortSignal.timeout(60_000),
      },
    );
  } catch (error) {
    throw new Error(error.name === 'TimeoutError'
      ? 'Gemma request timed out after 60 seconds.'
      : 'Could not reach the Gemma API. Check your network connection.');
  }
  if (!response.ok) {
    // Avoid including upstream response bodies, which could contain sensitive data.
    const hint = {
      400: 'Check the prompt and model configuration.',
      401: 'Check your API key.',
      403: 'Check your API key and model access.',
      404: 'The configured model is unavailable.',
      429: 'API quota exceeded. Try again later.',
    }[response.status] || 'Try again later.';
    throw new Error(`Gemma API returned HTTP ${response.status}. ${hint}`);
  }
  const data = await response.json();
  const text = data.candidates?.[0]?.content?.parts
    ?.filter(part => !part.thought && typeof part.text === 'string')
    .map(part => part.text).join('');
  if (!text?.trim()) {
    throw new Error('Gemma returned no text. The prompt may have been blocked or generation stopped.');
  }
  return text;
}
