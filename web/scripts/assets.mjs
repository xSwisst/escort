import sharp from 'sharp';
import { access } from 'node:fs/promises';

const source = 'public/campaign-source.png';

try {
  await access(source);
} catch {
  throw new Error(
    'Place the supplied campaign image at public/campaign-source.png.'
  );
}

for (const width of [768, 1536]) {
  await sharp(source)
    .resize({ width, withoutEnlargement: true })
    .webp({ quality: 86 })
    .toFile('public/campaign-' + width + '.webp');

  await sharp(source)
    .resize({ width, withoutEnlargement: true })
    .avif({ quality: 65, effort: 5 })
    .toFile('public/campaign-' + width + '.avif');
}
