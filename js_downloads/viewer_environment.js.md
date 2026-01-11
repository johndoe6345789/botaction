# viewer_environment.js

## Overview

This file contains the **jQuery library** - NOT 3D environment/skybox handling. It's a complete minified jQuery for DOM manipulation, AJAX, events, and animations.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~89KB (minified)
- **Type**: JavaScript library
- **Library**: jQuery (https://jquery.com)

## Purpose

jQuery is bundled for legacy compatibility with older Sketchfab components that haven't been migrated to React.

## Core Features

### 1. DOM Selection & Manipulation

```javascript
// Selection
$('#element')              // By ID
$('.class')                // By class
$('div.container')         // Combined
$('[data-id="123"]')       // By attribute

// DOM manipulation
$('.item').addClass('active');
$('.item').removeClass('active');
$('.item').toggleClass('active');
$('.item').attr('data-id', '123');
$('.item').html('<span>content</span>');
$('.item').text('content');
$('.item').append('<div>new</div>');
$('.item').prepend('<div>first</div>');
$('.item').remove();
```

### 2. Event Handling

```javascript
// Click events
$('.button').on('click', function(e) {
  e.preventDefault();
  // Handle click
});

// Delegated events
$('.container').on('click', '.item', function() {
  // Handle delegated click
});

// Event shortcuts
$('.button').click(handler);
$('.input').focus(handler);
$('.input').blur(handler);
$('.form').submit(handler);

// Remove events
$('.button').off('click');
```

### 3. AJAX Requests

```javascript
// GET request
$.ajax({
  url: '/api/models',
  method: 'GET',
  success: function(data) {
    console.log(data);
  },
  error: function(xhr, status, error) {
    console.error(error);
  }
});

// Shorthand
$.get('/api/models', function(data) {
  console.log(data);
});

// POST request
$.post('/api/models', { name: 'Model' }, function(response) {
  console.log(response);
});

// JSON
$.getJSON('/api/models', function(data) {
  console.log(data);
});
```

### 4. CSS Manipulation

```javascript
// Get/set CSS
$('.element').css('color');
$('.element').css('color', 'red');
$('.element').css({
  color: 'red',
  fontSize: '14px'
});

// Dimensions
$('.element').width();
$('.element').height();
$('.element').outerWidth();
$('.element').outerHeight();

// Position
$('.element').offset();     // Relative to document
$('.element').position();   // Relative to parent
```

### 5. Animations

```javascript
// Basic animations
$('.element').show();
$('.element').hide();
$('.element').toggle();

// Fade
$('.element').fadeIn();
$('.element').fadeOut();
$('.element').fadeToggle();
$('.element').fadeTo(0.5);

// Slide
$('.element').slideDown();
$('.element').slideUp();
$('.element').slideToggle();

// Custom animation
$('.element').animate({
  opacity: 0.5,
  left: '+=50'
}, 500, 'swing', function() {
  // Complete callback
});
```

### 6. Traversal

```javascript
// Ancestors
$('.item').parent();
$('.item').parents();
$('.item').closest('.container');

// Descendants
$('.container').find('.item');
$('.container').children();

// Siblings
$('.item').siblings();
$('.item').next();
$('.item').prev();

// Filtering
$('.items').filter('.active');
$('.items').not('.disabled');
$('.items').first();
$('.items').last();
$('.items').eq(2);
```

### 7. Utilities

```javascript
// Array/object iteration
$.each(array, function(index, value) {
  // ...
});

$.each(object, function(key, value) {
  // ...
});

// Extend objects
$.extend(target, source);
$.extend(true, target, source);  // Deep merge

// Type checking
$.isArray(value);
$.isFunction(value);
$.isPlainObject(value);

// Data
$('.element').data('key', 'value');
$('.element').data('key');
```

### 8. Deferred/Promises

```javascript
// Create deferred
var deferred = $.Deferred();

// Resolve/reject
deferred.resolve(value);
deferred.reject(error);

// Promise
deferred.promise();

// Chaining
$.ajax('/api/models')
  .done(function(data) { })
  .fail(function(error) { })
  .always(function() { });

// Multiple promises
$.when(promise1, promise2).done(function(result1, result2) {
  // Both completed
});
```

## Sketchfab Usage

### Legacy Components

```javascript
// Still used in some older Backbone views
var PopupView = Backbone.View.extend({
  events: {
    'click .close': 'onClose'
  },
  
  render: function() {
    this.$el.html(this.template());
    this.$('.content').addClass('active');
    return this;
  }
});
```

### DOM Ready

```javascript
$(document).ready(function() {
  // Initialize legacy components
});

// Or shorthand
$(function() {
  // Initialize
});
```

### Plugin Integration

```javascript
// Some legacy plugins still use jQuery
$('.slider').owlCarousel({
  items: 4,
  navigation: true
});
```

## Migration Note

Sketchfab is transitioning away from jQuery:

```javascript
// Old jQuery code
$('.button').on('click', function() {
  $(this).addClass('active');
});

// Modern React equivalent
function Button() {
  const [active, setActive] = useState(false);
  return (
    <button 
      className={active ? 'active' : ''} 
      onClick={() => setActive(true)}
    >
      Click me
    </button>
  );
}
```

## Version

The bundled version appears to be jQuery 3.x based on the module pattern and API signatures.

## Notes

- Filename is misleading - contains jQuery, not 3D environments
- Bundled for legacy compatibility
- New code should use React/vanilla JS
- Full jQuery API available globally as `$` and `jQuery`
- Includes AJAX, animation, event handling, DOM manipulation
