import { generateText } from './gemma.js';

const prompt = process.argv.slice(2).join(' ') ||
  'In one sentence, explain how AI can help monitor forest health.';
try {
  console.log(await generateText(prompt));
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
