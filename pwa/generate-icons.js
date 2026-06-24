/**
 * Icon Generator for MessageCipher PWA
 * 
 * Generates cipher-themed PNG icons at 192x192 and 512x512 pixels.
 * Uses pure Node.js (no external dependencies) to create minimal valid PNG files.
 * 
 * Design: 
 * - Solid background fill (#0077b6 brand color)
 * - Central lock/cipher motif occupying ~65% of canvas
 * - No transparency (solid background for maskable icon compatibility)
 */

import { writeFileSync } from 'fs';
import { deflateSync } from 'zlib';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Brand color #0077b6
const BRAND_R = 0x00;
const BRAND_G = 0x77;
const BRAND_B = 0xb6;

// Lighter accent for the motif
const ACCENT_R = 0xFF;
const ACCENT_G = 0xFF;
const ACCENT_B = 0xFF;

// Dark accent for depth
const DARK_R = 0x00;
const DARK_G = 0x4E;
const DARK_B = 0x7A;

/**
 * Creates a minimal valid PNG file from raw RGBA pixel data.
 */
function createPNG(width, height, pixels) {
  // PNG signature
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  // IHDR chunk
  const ihdrData = Buffer.alloc(13);
  ihdrData.writeUInt32BE(width, 0);
  ihdrData.writeUInt32BE(height, 4);
  ihdrData[8] = 8;  // bit depth
  ihdrData[9] = 2;  // color type: RGB (no alpha, solid background)
  ihdrData[10] = 0; // compression
  ihdrData[11] = 0; // filter
  ihdrData[12] = 0; // interlace
  const ihdr = createChunk('IHDR', ihdrData);

  // IDAT chunk - filter rows then deflate
  // Convert RGBA to RGB (we don't need alpha since background is solid)
  const rawData = Buffer.alloc(height * (1 + width * 3));
  for (let y = 0; y < height; y++) {
    const rowOffset = y * (1 + width * 3);
    rawData[rowOffset] = 0; // filter: None
    for (let x = 0; x < width; x++) {
      const srcIdx = (y * width + x) * 3;
      const dstIdx = rowOffset + 1 + x * 3;
      rawData[dstIdx] = pixels[srcIdx];     // R
      rawData[dstIdx + 1] = pixels[srcIdx + 1]; // G
      rawData[dstIdx + 2] = pixels[srcIdx + 2]; // B
    }
  }
  const compressed = deflateSync(rawData);
  const idat = createChunk('IDAT', compressed);

  // IEND chunk
  const iend = createChunk('IEND', Buffer.alloc(0));

  return Buffer.concat([signature, ihdr, idat, iend]);
}

function createChunk(type, data) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const typeBuffer = Buffer.from(type, 'ascii');
  const crcData = Buffer.concat([typeBuffer, data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(crcData), 0);
  return Buffer.concat([length, typeBuffer, data, crc]);
}

function crc32(buf) {
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) {
    crc ^= buf[i];
    for (let j = 0; j < 8; j++) {
      if (crc & 1) {
        crc = (crc >>> 1) ^ 0xEDB88320;
      } else {
        crc = crc >>> 1;
      }
    }
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

/**
 * Draws a cipher-themed lock icon on the pixel buffer.
 * The lock motif occupies approximately 65% of the canvas.
 */
function drawCipherIcon(pixels, size) {
  // Fill entire canvas with brand color (solid, non-transparent background)
  for (let i = 0; i < size * size; i++) {
    pixels[i * 3] = BRAND_R;
    pixels[i * 3 + 1] = BRAND_G;
    pixels[i * 3 + 2] = BRAND_B;
  }

  // Central motif dimensions (~65% of canvas)
  const motifSize = Math.floor(size * 0.65);
  const offsetX = Math.floor((size - motifSize) / 2);
  const offsetY = Math.floor((size - motifSize) / 2);

  // Draw a lock body (rounded rectangle in the lower portion)
  const lockBodyTop = offsetY + Math.floor(motifSize * 0.38);
  const lockBodyBottom = offsetY + motifSize;
  const lockBodyLeft = offsetX + Math.floor(motifSize * 0.1);
  const lockBodyRight = offsetX + Math.floor(motifSize * 0.9);
  const cornerRadius = Math.floor(motifSize * 0.08);

  drawRoundedRect(pixels, size, lockBodyLeft, lockBodyTop, lockBodyRight, lockBodyBottom, cornerRadius, ACCENT_R, ACCENT_G, ACCENT_B);

  // Draw the lock shackle (arc at the top)
  const shackleCenter = Math.floor(size / 2);
  const shackleOuterRadius = Math.floor(motifSize * 0.3);
  const shackleInnerRadius = Math.floor(motifSize * 0.2);
  const shackleTop = offsetY;
  const shackleBottom = lockBodyTop + Math.floor(motifSize * 0.05);

  drawShackle(pixels, size, shackleCenter, shackleBottom, shackleOuterRadius, shackleInnerRadius, shackleTop, ACCENT_R, ACCENT_G, ACCENT_B);

  // Draw keyhole in the lock body (dark circle + triangle)
  const keyholeX = Math.floor(size / 2);
  const keyholeY = lockBodyTop + Math.floor((lockBodyBottom - lockBodyTop) * 0.4);
  const keyholeRadius = Math.floor(motifSize * 0.09);

  drawFilledCircle(pixels, size, keyholeX, keyholeY, keyholeRadius, DARK_R, DARK_G, DARK_B);

  // Draw keyhole slot (small rectangle below circle)
  const slotWidth = Math.floor(keyholeRadius * 1.0);
  const slotHeight = Math.floor(motifSize * 0.15);
  const slotLeft = keyholeX - Math.floor(slotWidth / 2);
  const slotTop = keyholeY + Math.floor(keyholeRadius * 0.5);

  for (let y = slotTop; y < slotTop + slotHeight && y < size; y++) {
    for (let x = slotLeft; x < slotLeft + slotWidth && x < size; x++) {
      if (x >= 0 && y >= 0) {
        const idx = (y * size + x) * 3;
        pixels[idx] = DARK_R;
        pixels[idx + 1] = DARK_G;
        pixels[idx + 2] = DARK_B;
      }
    }
  }

  // Draw small cipher text characters around the lock for the "cipher" theme
  drawCipherText(pixels, size, offsetX, offsetY, motifSize);
}

function drawRoundedRect(pixels, size, left, top, right, bottom, radius, r, g, b) {
  for (let y = top; y < bottom && y < size; y++) {
    for (let x = left; x < right && x < size; x++) {
      if (x < 0 || y < 0) continue;
      // Check corners
      let inside = true;
      if (x < left + radius && y < top + radius) {
        // Top-left corner
        const dx = x - (left + radius);
        const dy = y - (top + radius);
        if (dx * dx + dy * dy > radius * radius) inside = false;
      } else if (x > right - radius && y < top + radius) {
        // Top-right corner
        const dx = x - (right - radius);
        const dy = y - (top + radius);
        if (dx * dx + dy * dy > radius * radius) inside = false;
      } else if (x < left + radius && y > bottom - radius) {
        // Bottom-left corner
        const dx = x - (left + radius);
        const dy = y - (bottom - radius);
        if (dx * dx + dy * dy > radius * radius) inside = false;
      } else if (x > right - radius && y > bottom - radius) {
        // Bottom-right corner
        const dx = x - (right - radius);
        const dy = y - (bottom - radius);
        if (dx * dx + dy * dy > radius * radius) inside = false;
      }
      if (inside) {
        const idx = (y * size + x) * 3;
        pixels[idx] = r;
        pixels[idx + 1] = g;
        pixels[idx + 2] = b;
      }
    }
  }
}

function drawShackle(pixels, size, centerX, bottomY, outerR, innerR, topY, r, g, b) {
  // Draw the top arc of the shackle
  const arcCenterY = bottomY - Math.floor((bottomY - topY) * 0.2);

  for (let y = topY; y <= bottomY && y < size; y++) {
    for (let x = centerX - outerR; x <= centerX + outerR && x < size; x++) {
      if (x < 0 || y < 0) continue;
      const dx = x - centerX;
      const dy = y - arcCenterY;
      const dist = Math.sqrt(dx * dx + dy * dy);

      // Only draw the upper portion (above arcCenterY) as arc, and sides below
      if (y <= arcCenterY) {
        if (dist >= innerR && dist <= outerR) {
          const idx = (y * size + x) * 3;
          pixels[idx] = r;
          pixels[idx + 1] = g;
          pixels[idx + 2] = b;
        }
      } else {
        // Draw vertical bars on sides
        if ((x >= centerX - outerR && x <= centerX - innerR) ||
            (x >= centerX + innerR && x <= centerX + outerR)) {
          const idx = (y * size + x) * 3;
          pixels[idx] = r;
          pixels[idx + 1] = g;
          pixels[idx + 2] = b;
        }
      }
    }
  }
}

function drawFilledCircle(pixels, size, cx, cy, radius, r, g, b) {
  for (let y = cy - radius; y <= cy + radius; y++) {
    for (let x = cx - radius; x <= cx + radius; x++) {
      if (x < 0 || y < 0 || x >= size || y >= size) continue;
      const dx = x - cx;
      const dy = y - cy;
      if (dx * dx + dy * dy <= radius * radius) {
        const idx = (y * size + x) * 3;
        pixels[idx] = r;
        pixels[idx + 1] = g;
        pixels[idx + 2] = b;
      }
    }
  }
}

/**
 * Draws small "01" binary/cipher text elements around the border of the motif area
 * to reinforce the encryption/cipher theme.
 */
function drawCipherText(pixels, size, offsetX, offsetY, motifSize) {
  const charSize = Math.max(4, Math.floor(size * 0.025));
  const spacing = charSize * 2;

  // Use a semi-transparent lighter shade
  const textR = 0x4D;
  const textG = 0xA8;
  const textB = 0xD4;

  // Draw dots pattern around the edges representing encoded data
  // Top edge
  for (let x = offsetX; x < offsetX + motifSize; x += spacing) {
    if (x + charSize < size && offsetY - charSize * 2 >= 0) {
      drawSmallDot(pixels, size, x, offsetY - charSize * 2, Math.floor(charSize / 2), textR, textG, textB);
    }
  }

  // Bottom edge  
  for (let x = offsetX; x < offsetX + motifSize; x += spacing) {
    if (x + charSize < size && offsetY + motifSize + charSize < size) {
      drawSmallDot(pixels, size, x, offsetY + motifSize + charSize, Math.floor(charSize / 2), textR, textG, textB);
    }
  }

  // Left edge
  for (let y = offsetY; y < offsetY + motifSize; y += spacing) {
    if (offsetX - charSize * 2 >= 0 && y + charSize < size) {
      drawSmallDot(pixels, size, offsetX - charSize * 2, y, Math.floor(charSize / 2), textR, textG, textB);
    }
  }

  // Right edge
  for (let y = offsetY; y < offsetY + motifSize; y += spacing) {
    if (offsetX + motifSize + charSize < size && y + charSize < size) {
      drawSmallDot(pixels, size, offsetX + motifSize + charSize, y, Math.floor(charSize / 2), textR, textG, textB);
    }
  }
}

function drawSmallDot(pixels, size, x, y, radius, r, g, b) {
  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      const px = x + dx;
      const py = y + dy;
      if (px >= 0 && py >= 0 && px < size && py < size) {
        if (dx * dx + dy * dy <= radius * radius) {
          const idx = (py * size + px) * 3;
          pixels[idx] = r;
          pixels[idx + 1] = g;
          pixels[idx + 2] = b;
        }
      }
    }
  }
}

// Generate icons
function generateIcon(size, outputPath) {
  const pixels = Buffer.alloc(size * size * 3);
  drawCipherIcon(pixels, size);
  const png = createPNG(size, size, pixels);
  writeFileSync(outputPath, png);
  console.log(`Generated ${size}x${size} icon: ${outputPath}`);
}

const iconsDir = join(__dirname, 'icons');
generateIcon(192, join(iconsDir, 'icon-192.png'));
generateIcon(512, join(iconsDir, 'icon-512.png'));
console.log('Done! Icons generated successfully.');
