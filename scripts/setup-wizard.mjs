#!/usr/bin/env node
/**
 * AUTHORA Setup Wizard
 * Guides first-time setup: DB check, env config, admin user creation.
 */
import { createInterface } from 'readline';
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { resolve } from 'path';

const rl = createInterface({ input: process.stdin, output: process.stdout });

function ask(question, defaultVal = '') {
  return new Promise((resolve) => {
    const suffix = defaultVal ? ` [${defaultVal}]` : '';
    rl.question(`${question}${suffix}: `, (ans) => {
      resolve(ans.trim() || defaultVal);
    });
  });
}

async function main() {
  console.log('\n=== AUTHORA Setup Wizard ===\n');

  const root = resolve(process.cwd());
  const envPath = resolve(root, '.env');
  const envExample = resolve(root, '.env.example');

  let env = {};
  if (existsSync(envPath)) {
    const content = readFileSync(envPath, 'utf8');
    content.split('\n').forEach((line) => {
      const m = line.match(/^([^#=]+)=(.*)$/);
      if (m) env[m[1].trim()] = m[2].trim();
    });
  }

  console.log('1. Database (PostgreSQL)');
  const dbUrl = await ask(
    'Database URL',
    env.DATABASE_URL || 'postgresql://authora:authora@localhost:5432/authora'
  );
  env.DATABASE_URL = dbUrl;

  console.log('\n2. Redis');
  const redisUrl = await ask('Redis URL', env.REDIS_URL || 'redis://localhost:6379/0');
  env.REDIS_URL = redisUrl;

  console.log('\n3. Security');
  const secret = await ask(
    'Secret key (for JWT)',
    env.SECRET_KEY || 'change-me-in-production-use-openssl-rand-hex-32'
  );
  env.SECRET_KEY = secret;

  console.log('\n4. AI (optional - leave blank to skip)');
  const openaiKey = await ask('OpenAI API key', env.OPENAI_API_KEY || '');
  if (openaiKey) env.OPENAI_API_KEY = openaiKey;

  const anthropicKey = await ask('Anthropic API key', env.ANTHROPIC_API_KEY || '');
  if (anthropicKey) env.ANTHROPIC_API_KEY = anthropicKey;

  const out = Object.entries(env)
    .map(([k, v]) => `${k}=${v}`)
    .join('\n');

  writeFileSync(envPath, out + '\n');
  console.log(`\nWrote ${envPath}`);
  console.log('\nNext steps:');
  console.log('  1. Ensure PostgreSQL and Redis are running');
  console.log('  2. Run: npm run db:migrate');
  console.log('  3. Run: npm run db:seed  (creates demo admin user)');
  console.log('  4. Run: npm run dev     (starts frontend)');
  console.log('  5. Run: npm run dev:api (starts backend)\n');
  rl.close();
}

main().catch(console.error);
