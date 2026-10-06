import { test } from 'node:test';
import assert from 'node:assert/strict';
import { generateText } from '../src/gemma.js';

test('Gemma request, response, and failure handling', async () => {
  const originalFetch = globalThis.fetch;
  const originalEnv = { ...process.env };
  try {
    delete process.env.GEMINI_API_KEY;
    await assert.rejects(generateText('hello'), /Set GEMINI_API_KEY/);
    process.env.GEMINI_API_KEY = 'test-key';
    delete process.env.GEMMA_MODEL;
    await assert.rejects(generateText('  '), /non-empty/);
    globalThis.fetch = async (url, options) => {
      assert.ok(url.endsWith('/gemma-4-26b-a4b-it:generateContent'));
      assert.equal(options.headers['x-goog-api-key'], 'test-key');
      assert.equal(options.method, 'POST');
      assert.deepEqual(JSON.parse(options.body).contents,
        [{ role: 'user', parts: [{ text: 'hello' }] }]);
      return Response.json({ candidates: [{ content: { parts: [
        { text: 'private reasoning', thought: true }, { text: 'Forest ' }, { text: 'Guard' },
      ] } }] });
    };
    assert.equal(await generateText('hello'), 'Forest Guard');
    process.env.GEMMA_MODEL = 'gemma-4-31b-it';
    globalThis.fetch = async url => {
      assert.ok(url.endsWith('/gemma-4-31b-it:generateContent'));
      return Response.json({ error: { message: 'sensitive upstream data' } }, { status: 429 });
    };
    await assert.rejects(generateText('hello'), /HTTP 429.*quota/);
    globalThis.fetch = async () => Response.json({ candidates: [] });
    await assert.rejects(generateText('hello'), /no text/);
    globalThis.fetch = async () => { throw new DOMException('timeout', 'TimeoutError'); };
    await assert.rejects(generateText('hello'), /timed out/);
    globalThis.fetch = async () => { throw new TypeError('fetch failed'); };
    await assert.rejects(generateText('hello'), /network connection/);
    process.env.GEMMA_MODEL = 'invalid';
    await assert.rejects(generateText('hello'), /GEMMA_MODEL must be/);
  } finally {
    globalThis.fetch = originalFetch;
    for (const key of ['GEMINI_API_KEY', 'GEMMA_MODEL']) {
      if (originalEnv[key] === undefined) delete process.env[key];
      else process.env[key] = originalEnv[key];
    }
  }
});
