import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

const output = fileURLToPath(new URL('../../src/kaiten_cli/assets/document_yjs.cjs', import.meta.url));
await fs.mkdir(new URL('../../src/kaiten_cli/assets/', import.meta.url), { recursive: true });
const result = await build({
  entryPoints: [fileURLToPath(new URL('./cli.mjs', import.meta.url))],
  bundle: true, minify: true, platform: 'node', target: 'node20', format: 'cjs',
  outfile: output, legalComments: 'external', metafile: true,
});
const packages = new Map();
for (const input of Object.keys(result.metafile.inputs)) {
  let dir = path.dirname(path.resolve(input));
  while (dir.includes('node_modules')) {
    try {
      const pkg = JSON.parse(await fs.readFile(path.join(dir, 'package.json'), 'utf8'));
      const filename = (await fs.readdir(dir)).find(name => /^licen[cs]e(?:\.(?:txt|md))?$/i.test(name));
      if (filename) packages.set(`${pkg.name}@${pkg.version}`, await fs.readFile(path.join(dir, filename), 'utf8'));
      break;
    } catch { dir = path.dirname(dir); }
  }
}
await fs.writeFile(output + '.LICENSES.txt', [...packages].sort().map(([name, text]) => `${name}\n${text}`).join('\n\n'));
