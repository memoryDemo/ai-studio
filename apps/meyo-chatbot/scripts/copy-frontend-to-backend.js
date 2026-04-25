import { cp, mkdir, rm } from 'fs/promises';
import { resolve } from 'path';

const root = process.cwd();
const source = resolve(root, 'build');
const target = resolve(root, 'backend/open_webui/frontend');

await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
await cp(source, target, { recursive: true });

console.log(`Copied frontend build from ${source} to ${target}`);
