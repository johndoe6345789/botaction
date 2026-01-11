# viewer_lighting.js

## Overview
Minified Sketchfab webpack chunk containing the Twemoji library (v14.0.2) for cross-platform emoji rendering using Twitter's emoji assets.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 4798
- **Library**: Twemoji v14.0.2
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Twemoji Library
Twitter's emoji library for consistent emoji display:

**CDN Configuration**:
- Base URL: `https://twemoji.maxcdn.com/v/14.0.2/`
- Default extension: `.png`
- Default size: `72x72`

**Core Functions**:

| Function | Description |
|----------|-------------|
| `parse` | Parse string or DOM for emoji |
| `replace` | Replace emoji with img elements |
| `test` | Test if string contains emoji |

**Convert Utilities**:
- `fromCodePoint` - Convert code point to emoji string
- `toCodePoint` - Convert emoji to code point string

### Emoji Detection
**Regex Pattern**:
- Matches Unicode emoji sequences
- Handles compound emoji (skin tones, ZWJ sequences)
- Supports emoji modifiers

### DOM Manipulation
**Methods**:
- `createElement` - Create img element for emoji
- `replaceChild` - Replace text node with img
- `createTextNode` - Create text node

**Image Element Creation**:
- Automatic `onerror` fallback
- Alt text set to original emoji
- Draggable disabled by default

### HTML Entity Escaping
Escapes special characters:
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `'` → `&#39;`
- `"` → `&quot;`

## Dependencies
- MaxCDN (emoji image hosting)
- No external JavaScript dependencies

## Technical Details
- Works in both browser and Node.js
- Supports all emoji up to Unicode 14.0
- Lazy loads emoji images
- XSS-safe text handling

## Use Cases
1. Consistent emoji display across platforms
2. Comment and chat emoji rendering
3. Profile bio emoji support
4. Model descriptions with emoji
5. Cross-browser emoji compatibility

## Notes
- Uses Twitter's open-source emoji set
- Falls back to native emoji on error
- Minimal performance impact
- Accessible (includes alt text)
- Part of Sketchfab's text rendering pipeline
