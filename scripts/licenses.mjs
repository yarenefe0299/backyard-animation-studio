// Keep installed package notices beside the MP4 when distributing artifacts.
import {readdir, readFile, mkdir, copyFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
const dest = 'out/licenses';
await mkdir(dest, {recursive: true});
const packages = [];
async function scan(root) {
  for (const entry of await readdir(root, {withFileTypes: true})) {
    if (!entry.isDirectory() || entry.name === '.bin') continue;
    const dir = path.join(root, entry.name);
    if (entry.name.startsWith('@')) {await scan(dir); continue;}
    let pkg;
    try {pkg = JSON.parse(await readFile(path.join(dir, 'package.json'), 'utf8'));} catch {continue;}
    packages.push({name: pkg.name, version: pkg.version, license: pkg.license ?? 'see package notice'});
    for (const name of await readdir(dir)) {
      if (/^(license|licence|notice|copying)(\.|$|-)/i.test(name)) {
        const target = path.join(dest, pkg.name.replaceAll('/', '__'));
        await mkdir(target, {recursive: true});
        try {await copyFile(path.join(dir, name), path.join(target, name));} catch (e) {
          if (e.code !== 'EISDIR') throw e;
        }
      }
    }
    try {await scan(path.join(dir, 'node_modules'));} catch(e) {if(e.code !== 'ENOENT') throw e;}
  }
}
await scan('node_modules');
await writeFile(path.join(dest, 'packages.json'), JSON.stringify(packages, null, 2));
for (const name of await readdir('licenses')) await copyFile(path.join('licenses', name), path.join(dest, name));
await copyFile('THIRD_PARTY_NOTICES.md', path.join(dest, 'THIRD_PARTY_NOTICES.md'));
console.log(`Preserved notices for ${packages.length} installed packages.`);
