# popup_template.js

## Overview

This file contains **Nunjucks popup templates** - server-side rendered HTML templates for modal dialogs and popup UI components. Uses the Nunjucks templating engine.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~62KB (minified)
- **Type**: Nunjucks template strings
- **Framework**: Nunjucks

## Core Templates

### 1. Basic Popup Structure

```html
{% macro popup(options) %}
<div class="popup {{ options.className }}" 
     role="dialog" 
     aria-modal="true"
     aria-labelledby="popup-title-{{ options.id }}">
  
  {% if options.showHeader %}
  <header class="popup__header">
    <h2 id="popup-title-{{ options.id }}" class="popup__title">
      {{ options.title }}
    </h2>
    {% if options.showClose %}
    <button class="popup__close" aria-label="Close">
      <svg><!-- close icon --></svg>
    </button>
    {% endif %}
  </header>
  {% endif %}
  
  <div class="popup__body">
    {{ caller() }}
  </div>
  
  {% if options.showFooter %}
  <footer class="popup__footer">
    {{ options.footerContent | safe }}
  </footer>
  {% endif %}
</div>
{% endmacro %}
```

### 2. Confirm Dialog

```html
{% macro confirmDialog(options) %}
{% call popup({ 
  title: options.title or 'Confirm', 
  className: 'popup--confirm',
  showClose: true 
}) %}
  <p class="popup__message">{{ options.message }}</p>
  
  <div class="popup__actions">
    <button class="c-button c-button--secondary" 
            data-action="cancel">
      {{ options.cancelText or 'Cancel' }}
    </button>
    <button class="c-button c-button--primary {{ options.destructive ? 'c-button--danger' : '' }}" 
            data-action="confirm">
      {{ options.confirmText or 'Confirm' }}
    </button>
  </div>
{% endcall %}
{% endmacro %}
```

### 3. Login/Signup Popup

```html
{% macro authPopup(mode) %}
<div class="popup popup--auth">
  <div class="popup__tabs">
    <button class="popup__tab {{ 'active' if mode == 'login' }}" 
            data-mode="login">
      Log In
    </button>
    <button class="popup__tab {{ 'active' if mode == 'signup' }}" 
            data-mode="signup">
      Sign Up
    </button>
  </div>
  
  <div class="popup__body">
    {% if mode == 'login' %}
      {{ loginForm() }}
    {% else %}
      {{ signupForm() }}
    {% endif %}
  </div>
  
  <div class="popup__social">
    <span class="popup__divider">or continue with</span>
    <div class="popup__social-buttons">
      <button class="c-button c-button--google">Google</button>
      <button class="c-button c-button--facebook">Facebook</button>
      <button class="c-button c-button--apple">Apple</button>
    </div>
  </div>
</div>
{% endmacro %}
```

### 4. Share Popup

```html
{% macro sharePopup(model) %}
<div class="popup popup--share">
  <h2 class="popup__title">Share this model</h2>
  
  <div class="popup__share-buttons">
    <button class="share-button share-button--twitter" 
            data-share="twitter">
      Twitter
    </button>
    <button class="share-button share-button--facebook" 
            data-share="facebook">
      Facebook
    </button>
    <button class="share-button share-button--pinterest" 
            data-share="pinterest">
      Pinterest
    </button>
    <button class="share-button share-button--email" 
            data-share="email">
      Email
    </button>
  </div>
  
  <div class="popup__share-link">
    <input type="text" 
           value="{{ model.viewerUrl }}" 
           readonly 
           class="popup__share-input" />
    <button class="c-button" data-action="copy">
      Copy Link
    </button>
  </div>
</div>
{% endmacro %}
```

### 5. Download Popup

```html
{% macro downloadPopup(model, formats) %}
<div class="popup popup--download">
  <h2 class="popup__title">Download {{ model.name }}</h2>
  
  <ul class="popup__format-list">
    {% for format in formats %}
    <li class="format-option">
      <input type="radio" 
             name="format" 
             value="{{ format.extension }}" 
             id="format-{{ format.extension }}"
             {{ 'checked' if loop.first }} />
      <label for="format-{{ format.extension }}">
        <span class="format-option__name">{{ format.name }}</span>
        <span class="format-option__ext">.{{ format.extension }}</span>
        <span class="format-option__size">{{ format.size | filesizeformat }}</span>
      </label>
    </li>
    {% endfor %}
  </ul>
  
  <div class="popup__actions">
    <button class="c-button c-button--primary" data-action="download">
      Download
    </button>
  </div>
</div>
{% endmacro %}
```

### 6. Embed Popup

```html
{% macro embedPopup(model, options) %}
<div class="popup popup--embed">
  <h2 class="popup__title">Embed this model</h2>
  
  <div class="popup__preview">
    <iframe src="{{ model.embedUrl }}" 
            width="320" 
            height="240"></iframe>
  </div>
  
  <div class="popup__embed-options">
    <label>
      <input type="checkbox" name="autostart" checked />
      Autostart
    </label>
    <label>
      <input type="checkbox" name="ui_controls" checked />
      Show controls
    </label>
    <label>
      <input type="checkbox" name="ui_infos" />
      Show info
    </label>
  </div>
  
  <div class="popup__embed-code">
    <label for="embed-code">Embed code</label>
    <textarea id="embed-code" readonly>{{ embedCode }}</textarea>
    <button class="c-button" data-action="copy">Copy Code</button>
  </div>
</div>
{% endmacro %}
```

### 7. Report Popup

```html
{% macro reportPopup(type, target) %}
<div class="popup popup--report">
  <h2 class="popup__title">Report {{ type }}</h2>
  
  <form class="report-form">
    <fieldset>
      <legend>Reason for report</legend>
      
      <label class="radio-option">
        <input type="radio" name="reason" value="copyright" />
        Copyright infringement
      </label>
      <label class="radio-option">
        <input type="radio" name="reason" value="inappropriate" />
        Inappropriate content
      </label>
      <label class="radio-option">
        <input type="radio" name="reason" value="spam" />
        Spam or misleading
      </label>
      <label class="radio-option">
        <input type="radio" name="reason" value="other" />
        Other
      </label>
    </fieldset>
    
    <div class="form-field">
      <label for="report-details">Additional details</label>
      <textarea id="report-details" 
                name="details" 
                rows="4"></textarea>
    </div>
    
    <button type="submit" class="c-button c-button--primary">
      Submit Report
    </button>
  </form>
</div>
{% endmacro %}
```

## Nunjucks Filters

```javascript
// Custom filters used in templates
const filters = {
  filesizeformat: (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
  },
  
  truncate: (str, length) => {
    if (str.length <= length) return str;
    return str.slice(0, length) + '...';
  },
  
  dateformat: (date, format) => {
    return dayjs(date).format(format);
  }
};
```

## Template Rendering

```javascript
import nunjucks from 'nunjucks';

// Configure environment
const env = nunjucks.configure({
  autoescape: true,
  throwOnUndefined: false
});

// Add filters
env.addFilter('filesizeformat', filters.filesizeformat);
env.addFilter('truncate', filters.truncate);

// Render template
const html = env.renderString(popupTemplate, {
  model: modelData,
  formats: downloadFormats
});

// Insert into DOM
document.body.insertAdjacentHTML('beforeend', html);
```

## Usage Examples

### Show Confirm Dialog

```javascript
function showConfirmDialog(options) {
  const html = nunjucks.render('confirm.njk', {
    title: options.title,
    message: options.message,
    confirmText: options.confirmText,
    cancelText: options.cancelText,
    destructive: options.destructive
  });
  
  const popup = createPopupFromHTML(html);
  
  return new Promise((resolve) => {
    popup.querySelector('[data-action="confirm"]')
      .addEventListener('click', () => resolve(true));
    popup.querySelector('[data-action="cancel"]')
      .addEventListener('click', () => resolve(false));
  });
}

// Usage
const confirmed = await showConfirmDialog({
  title: 'Delete Model',
  message: 'Are you sure you want to delete this model?',
  confirmText: 'Delete',
  destructive: true
});
```

## CSS Classes

```css
.popup { }
.popup--confirm { }
.popup--auth { }
.popup--share { }
.popup--download { }
.popup--embed { }
.popup--report { }

.popup__header { }
.popup__title { }
.popup__close { }
.popup__body { }
.popup__footer { }
.popup__actions { }
.popup__tabs { }
.popup__tab { }
.popup__tab.active { }

.popup__message { }
.popup__share-buttons { }
.popup__share-link { }
.popup__format-list { }
.popup__embed-options { }
.popup__embed-code { }
```

## Notes

- Server-side rendered popup HTML templates
- Uses Nunjucks templating syntax
- Includes common popup patterns (confirm, share, download, etc.)
- Custom filters for formatting
- Accessible with ARIA attributes
