# viewer_network.js

## Overview
Minified Sketchfab webpack chunk containing a Markdown editor with CodeMirror integration, providing rich text editing capabilities for descriptions and comments.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 8813
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "i2hM" - Markdown Editor
Full-featured Markdown editing interface:

### Markdown Formatting Tokens
| Format | Token |
|--------|-------|
| Bold | `**` |
| Code | ` ``` ` |
| Italic | `*` |
| Quote | `> ` |
| Unordered List | `* ` |
| Ordered List | `1. ` |

### Link Templates
- **Links**: `[`, `](#url#)`
- **Images**: `![`, `](#url#)`

### Toolbar Actions
| Action | Shortcut | Icon |
|--------|----------|------|
| `toggleBold` | Cmd-B | fa-bold |
| `toggleItalic` | Cmd-I | fa-italic |
| `drawLink` | Cmd-K | fa-link |
| `toggleHeading` | Cmd-H | fa-heading |
| `drawImage` | Cmd-Alt-I | fa-image |
| `toggleBlockquote` | Cmd-' | fa-quote-left |
| `toggleOrderedList` | Cmd-Alt-L | fa-list-ol |
| `toggleUnorderedList` | Cmd-L | fa-list-ul |

### Editor API

**Instance Methods**:
- `getEditor()` - Get CodeMirror instance
- `setEditor(editor)` - Set CodeMirror instance
- `getShortcuts()` - Get keyboard shortcut map
- `getMarkdownEditorValue()` - Get current content

**Formatting Methods**:
- `toggleBold()` - Toggle bold formatting
- `toggleItalic()` - Toggle italic formatting
- `toggleHeading()` - Cycle heading levels (1-6)
- `toggleBlockquote()` - Toggle quote formatting
- `toggleOrderedList()` - Toggle numbered list
- `toggleUnorderedList()` - Toggle bullet list
- `drawLink()` - Insert link template
- `drawImage()` - Insert image template

### Internal Methods

**`_toggleBlock(type, startToken, endToken)`**:
- Handles inline formatting (bold, italic, strikethrough)
- Smart selection handling
- Preserves cursor position

**`_toggleHeading()`**:
- Cycles through heading levels (# to ######)
- Multi-line support
- Removes heading on level 6+

**`_toggleLine(type)`**:
- Line-based formatting (quotes, lists)
- Toggle behavior (add/remove)
- Multi-line selection support

**`_replaceSelection(isActive, template, defaultUrl)`**:
- Link and image insertion
- URL placeholder replacement
- Selection preservation

### Tab Handling
- `_tabAndIndentMarkdownList()` - Indent list items
- `_shiftTabAndUnindentMarkdownList()` - Unindent list items
- Space-based indentation fallback

### Keyboard Shortcuts
Default shortcuts (Mac/Windows aware):
- **Enter**: `newlineAndIndentContinueMarkdownList`
- **Tab**: Indent list or insert spaces
- **Shift-Tab**: Unindent list

## Dependencies
- CodeMirror (editor engine)
- jQuery (DOM manipulation)
- Font Awesome (toolbar icons)

## Technical Details
- Platform-aware shortcuts (Cmd vs Ctrl)
- Preview mode detection
- Undo/redo support via CodeMirror
- State detection for toggle actions

## Use Cases
1. Model descriptions
2. Comments and discussions
3. Documentation editing
4. Rich text annotations

## Notes
- Integrates with CodeMirror's Markdown mode
- Supports GitHub-flavored Markdown
- Accessible toolbar with titles
- Maintains focus during formatting
