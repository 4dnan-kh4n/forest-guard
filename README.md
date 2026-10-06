# Forest Guard

First step: Gemma 4 text generation through Google's hosted Gemini API.
Node.js 22 or newer is required. No dependencies need to be installed.

## Setup

1. Create an API key in [Google AI Studio](https://aistudio.google.com/apikey).
2. Copy the environment template in PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Edit `.env` and replace the placeholder with your API key. Keep this file private.
4. Run a prompt:

   ```powershell
   npm run gemma -- "How can AI help detect forest degradation?"
   ```

Running `npm run gemma` without a prompt uses a short forest monitoring question.
The default model is `gemma-4-26b-a4b-it`; set `GEMMA_MODEL=gemma-4-31b-it`
in `.env` to use the other supported hosted model.

## Reuse in the application

Import the client in server-side Node.js code, with the environment variables loaded:

```js
import { generateText } from './src/gemma.js';

const answer = await generateText('Summarize signs of forest degradation.');
```

The client returns generated text and throws on invalid input, missing credentials,
API errors, empty responses, or a 60-second timeout. Keep the API key on the server;
do not bundle this client into frontend code.

## Verification

```powershell
npm test
```

Tests mock the API and need no key. A successful live `npm run gemma` call is the
remaining check for your credentials and model access.

[Official Gemma API documentation](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api)
