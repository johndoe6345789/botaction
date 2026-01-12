# missing_webgl_popup.js

## Overview

This file contains **WebGL error handling and model properties components**. It displays WebGL compatibility errors and provides model property editing forms.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~48KB (minified)
- **Type**: React error/form components
- **Framework**: React

## Core Components

### 1. WebGL Error Popup (`a3pH`)

Displayed when WebGL is unavailable:

```javascript
<WebGLErrorPopup
  error={webglError}
  onDismiss={handleDismiss}
/>

// Error types:
// - 'not_supported': Browser doesn't support WebGL
// - 'disabled': WebGL disabled in browser settings
// - 'context_lost': GPU context lost
// - 'extension_missing': Required extension not available
```

### Error Messages

```javascript
const errorMessages = {
  not_supported: {
    title: 'WebGL Not Supported',
    message: 'Your browser does not support WebGL. Please try a different browser.',
    suggestions: [
      'Try Chrome, Firefox, or Edge',
      'Update your browser to the latest version',
      'Make sure hardware acceleration is enabled'
    ]
  },
  disabled: {
    title: 'WebGL Disabled',
    message: 'WebGL is disabled in your browser settings.',
    suggestions: [
      'Enable WebGL in your browser settings',
      'Check if an extension is blocking WebGL',
      'Try disabling ad blockers temporarily'
    ]
  },
  context_lost: {
    title: 'Graphics Context Lost',
    message: 'The graphics context was lost. This can happen when your GPU is under heavy load.',
    suggestions: [
      'Refresh the page to try again',
      'Close other GPU-intensive applications',
      'Update your graphics drivers'
    ]
  },
  extension_missing: {
    title: 'Missing WebGL Extension',
    message: 'A required WebGL extension is not available on your device.',
    suggestions: [
      'Try a different browser',
      'Update your graphics drivers',
      'The model may use features not supported by your GPU'
    ]
  }
};
```

### WebGL Detection

```javascript
function detectWebGLSupport() {
  const canvas = document.createElement('canvas');
  
  // Try WebGL2 first
  let gl = canvas.getContext('webgl2');
  if (gl) {
    return { supported: true, version: 2, context: gl };
  }
  
  // Fall back to WebGL1
  gl = canvas.getContext('webgl') || 
       canvas.getContext('experimental-webgl');
  if (gl) {
    return { supported: true, version: 1, context: gl };
  }
  
  return { supported: false, version: 0, context: null };
}

function getWebGLInfo(gl) {
  const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
  
  return {
    vendor: debugInfo 
      ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) 
      : gl.getParameter(gl.VENDOR),
    renderer: debugInfo
      ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
      : gl.getParameter(gl.RENDERER),
    version: gl.getParameter(gl.VERSION),
    shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
    maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
    maxViewportDims: gl.getParameter(gl.MAX_VIEWPORT_DIMS)
  };
}
```

### 2. Model Properties Form (`KmQw`)

Model metadata editing:

```javascript
<ModelPropertiesForm
  model={model}
  onSave={handleSave}
  onCancel={handleCancel}
/>
```

### Property Fields

```javascript
const modelProperties = {
  // Basic info
  name: {
    type: 'text',
    label: 'Name',
    maxLength: 100,
    required: true,
    placeholder: 'Enter model name'
  },
  description: {
    type: 'textarea',
    label: 'Description',
    maxLength: 5000,
    required: false,
    placeholder: 'Describe your model...',
    supportMarkdown: true
  },
  tags: {
    type: 'tags',
    label: 'Tags',
    maxTags: 20,
    minTags: 1,
    placeholder: 'Add tags...'
  },
  
  // Categories
  categories: {
    type: 'multiselect',
    label: 'Categories',
    maxSelections: 3,
    options: [
      { value: 'characters', label: 'Characters & Creatures' },
      { value: 'architecture', label: 'Architecture' },
      { value: 'vehicles', label: 'Vehicles' },
      { value: 'electronics', label: 'Electronics' },
      { value: 'nature', label: 'Nature & Plants' },
      { value: 'furniture', label: 'Furniture' },
      { value: 'food', label: 'Food & Drink' },
      { value: 'weapons', label: 'Weapons & Armor' },
      // ...more
    ]
  },
  
  // License
  license: {
    type: 'select',
    label: 'License',
    options: [
      { value: 'cc0', label: 'CC0 - Public Domain' },
      { value: 'cc-by', label: 'CC Attribution' },
      { value: 'cc-by-sa', label: 'CC Attribution-ShareAlike' },
      { value: 'cc-by-nd', label: 'CC Attribution-NoDerivs' },
      { value: 'cc-by-nc', label: 'CC Attribution-NonCommercial' },
      { value: 'cc-by-nc-sa', label: 'CC Attribution-NonCommercial-ShareAlike' },
      { value: 'cc-by-nc-nd', label: 'CC Attribution-NonCommercial-NoDerivs' },
      { value: 'all-rights-reserved', label: 'All Rights Reserved' }
    ]
  },
  
  // Settings
  isDownloadable: {
    type: 'toggle',
    label: 'Allow downloads',
    description: 'Let users download this model'
  },
  isPublished: {
    type: 'toggle',
    label: 'Published',
    description: 'Make this model visible to others'
  },
  isAgeRestricted: {
    type: 'toggle',
    label: 'Age restricted',
    description: 'This model contains mature content'
  }
};
```

### 3. Tags Input

```javascript
<TagsInput
  value={tags}
  onChange={setTags}
  maxTags={20}
  suggestions={tagSuggestions}
  placeholder="Add tags..."
/>

// Features:
// - Autocomplete suggestions
// - Tag validation
// - Duplicate prevention
// - Remove on backspace
```

### 4. Category Selector

```javascript
<CategorySelector
  value={selectedCategories}
  onChange={setCategories}
  maxSelections={3}
  categories={categoryTree}
/>

// Hierarchical category selection
// Shows breadcrumb of selected categories
```

## Form Validation

```javascript
const validationRules = {
  name: [
    { type: 'required', message: 'Name is required' },
    { type: 'maxLength', value: 100, message: 'Name too long' },
    { type: 'minLength', value: 3, message: 'Name too short' }
  ],
  tags: [
    { type: 'minLength', value: 1, message: 'Add at least one tag' },
    { type: 'maxLength', value: 20, message: 'Maximum 20 tags' }
  ],
  description: [
    { type: 'maxLength', value: 5000, message: 'Description too long' }
  ]
};

function validateModel(model) {
  const errors = {};
  
  for (const [field, rules] of Object.entries(validationRules)) {
    for (const rule of rules) {
      const value = model[field];
      
      if (rule.type === 'required' && !value) {
        errors[field] = rule.message;
        break;
      }
      if (rule.type === 'maxLength' && value?.length > rule.value) {
        errors[field] = rule.message;
        break;
      }
      // ...more validations
    }
  }
  
  return errors;
}
```

## Usage Examples

### WebGL Check on Load

```jsx
function ViewerPage({ modelId }) {
  const [webglError, setWebglError] = useState(null);
  
  useEffect(() => {
    const { supported, version } = detectWebGLSupport();
    
    if (!supported) {
      setWebglError('not_supported');
    } else if (version < 2 && modelRequiresWebGL2(modelId)) {
      setWebglError('extension_missing');
    }
  }, [modelId]);
  
  if (webglError) {
    return (
      <WebGLErrorPopup
        error={webglError}
        onDismiss={() => navigate('/')}
      />
    );
  }
  
  return <ModelViewer modelId={modelId} />;
}
```

### Model Edit Form

```jsx
function EditModelPage({ model }) {
  const [formData, setFormData] = useState({
    name: model.name,
    description: model.description,
    tags: model.tags,
    categories: model.categories,
    license: model.license
  });
  const [errors, setErrors] = useState({});
  
  const handleSubmit = async () => {
    const validationErrors = validateModel(formData);
    
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    
    await updateModel(model.id, formData);
  };
  
  return (
    <ModelPropertiesForm
      values={formData}
      errors={errors}
      onChange={setFormData}
      onSubmit={handleSubmit}
    />
  );
}
```

## CSS Classes

```css
/* WebGL Error */
.webgl-error { }
.webgl-error__icon { }
.webgl-error__title { }
.webgl-error__message { }
.webgl-error__suggestions { }
.webgl-error__button { }

/* Model Properties Form */
.model-form { }
.model-form__section { }
.model-form__field { }
.model-form__label { }
.model-form__input { }
.model-form__error { }
.model-form__help { }

/* Tags Input */
.tags-input { }
.tags-input__tag { }
.tags-input__tag-remove { }
.tags-input__input { }
.tags-input__suggestions { }
```

## Notes

- WebGL compatibility detection and error handling
- Model property editing forms
- Form validation with error messages
- Tags and category selection
- License selection for models
