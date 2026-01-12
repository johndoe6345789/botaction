# viewer_postprocessing.js

## Overview

This file contains **typography, theming, and modal/form components** - core UI infrastructure for text styling, color themes, and overlay dialogs. NOT WebGL post-processing as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~68KB (minified)
- **Type**: React UI infrastructure
- **Framework**: React

## Core Systems

### 1. Typography System

Text styling components:

```javascript
// Headings
<Heading level={1}>Page Title</Heading>
<Heading level={2}>Section Title</Heading>
<Heading level={3}>Subsection</Heading>

// Body text
<Text size="large">Large body text</Text>
<Text size="medium">Regular body text</Text>
<Text size="small">Small text</Text>

// Specialized
<Label>Form label</Label>
<Caption>Image caption</Caption>
<Code>inline code</Code>
```

### Typography Scale

```javascript
const typographyScale = {
  h1: {
    fontSize: '2.5rem',      // 40px
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: '-0.02em'
  },
  h2: {
    fontSize: '2rem',        // 32px
    fontWeight: 700,
    lineHeight: 1.25,
    letterSpacing: '-0.01em'
  },
  h3: {
    fontSize: '1.5rem',      // 24px
    fontWeight: 600,
    lineHeight: 1.3
  },
  h4: {
    fontSize: '1.25rem',     // 20px
    fontWeight: 600,
    lineHeight: 1.4
  },
  body: {
    fontSize: '1rem',        // 16px
    fontWeight: 400,
    lineHeight: 1.5
  },
  small: {
    fontSize: '0.875rem',    // 14px
    fontWeight: 400,
    lineHeight: 1.5
  },
  caption: {
    fontSize: '0.75rem',     // 12px
    fontWeight: 400,
    lineHeight: 1.4
  }
};
```

### 2. Theme System

Color and styling themes:

```javascript
const themes = {
  light: {
    name: 'light',
    colors: {
      // Background
      background: '#ffffff',
      backgroundSecondary: '#f5f5f5',
      surface: '#ffffff',
      surfaceHover: '#f8f8f8',
      
      // Text
      text: '#1a1a1a',
      textSecondary: '#666666',
      textMuted: '#999999',
      textInverse: '#ffffff',
      
      // Brand
      primary: '#1caad9',
      primaryHover: '#0e8ab8',
      primaryLight: '#e8f7fc',
      
      // Status
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
      
      // Border
      border: '#e0e0e0',
      borderHover: '#c0c0c0',
      
      // Shadows
      shadowColor: 'rgba(0, 0, 0, 0.1)'
    },
    shadows: {
      sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
      md: '0 4px 6px rgba(0, 0, 0, 0.1)',
      lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
      xl: '0 20px 25px rgba(0, 0, 0, 0.15)'
    }
  },
  
  dark: {
    name: 'dark',
    colors: {
      background: '#1a1a1a',
      backgroundSecondary: '#2d2d2d',
      surface: '#2d2d2d',
      surfaceHover: '#3d3d3d',
      
      text: '#ffffff',
      textSecondary: '#b0b0b0',
      textMuted: '#808080',
      textInverse: '#1a1a1a',
      
      primary: '#1caad9',
      primaryHover: '#3dbde8',
      primaryLight: '#1a3a4a',
      
      success: '#34d399',
      warning: '#fbbf24',
      error: '#f87171',
      info: '#60a5fa',
      
      border: '#404040',
      borderHover: '#505050',
      
      shadowColor: 'rgba(0, 0, 0, 0.3)'
    },
    shadows: {
      sm: '0 1px 2px rgba(0, 0, 0, 0.2)',
      md: '0 4px 6px rgba(0, 0, 0, 0.3)',
      lg: '0 10px 15px rgba(0, 0, 0, 0.3)',
      xl: '0 20px 25px rgba(0, 0, 0, 0.4)'
    }
  }
};
```

### Theme Provider

```jsx
const ThemeContext = createContext(themes.light);

function ThemeProvider({ children, theme = 'light' }) {
  const themeValue = themes[theme];
  
  useEffect(() => {
    // Apply CSS variables
    const root = document.documentElement;
    Object.entries(themeValue.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${kebabCase(key)}`, value);
    });
  }, [theme]);
  
  return (
    <ThemeContext.Provider value={themeValue}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  return useContext(ThemeContext);
}
```

### 3. Modal System

Dialog/overlay components:

```javascript
<Modal
  isOpen={isOpen}
  onClose={handleClose}
  size="medium"       // 'small' | 'medium' | 'large' | 'fullscreen'
  closeOnOverlay={true}
  closeOnEscape={true}
>
  <Modal.Header>
    <Modal.Title>Modal Title</Modal.Title>
    <Modal.CloseButton />
  </Modal.Header>
  
  <Modal.Body>
    Modal content here
  </Modal.Body>
  
  <Modal.Footer>
    <Button variant="secondary" onClick={handleClose}>Cancel</Button>
    <Button variant="primary" onClick={handleSave}>Save</Button>
  </Modal.Footer>
</Modal>
```

### Modal Sizes

```javascript
const modalSizes = {
  small: { width: '400px', maxHeight: '80vh' },
  medium: { width: '600px', maxHeight: '85vh' },
  large: { width: '800px', maxHeight: '90vh' },
  xlarge: { width: '1000px', maxHeight: '90vh' },
  fullscreen: { width: '100vw', height: '100vh' }
};
```

### 4. Form Components

Form field wrappers:

```javascript
<FormField
  label="Email"
  required
  error={errors.email}
  help="We'll never share your email"
>
  <Input
    type="email"
    value={email}
    onChange={setEmail}
    placeholder="you@example.com"
  />
</FormField>
```

### Form Elements

```jsx
// Input variations
<Input type="text" />
<Input type="email" />
<Input type="password" />
<Input type="number" min={0} max={100} />

// Textarea
<Textarea rows={4} maxLength={500} />

// Checkbox
<Checkbox
  checked={checked}
  onChange={setChecked}
  label="Accept terms"
/>

// Radio Group
<RadioGroup
  value={selected}
  onChange={setSelected}
  options={[
    { value: 'a', label: 'Option A' },
    { value: 'b', label: 'Option B' }
  ]}
/>

// Toggle/Switch
<Toggle
  checked={enabled}
  onChange={setEnabled}
  label="Enable feature"
/>
```

### 5. Alert Component

Inline notifications:

```javascript
<Alert variant="info" dismissible>
  Information message
</Alert>

<Alert variant="success" icon={<CheckIcon />}>
  Operation completed successfully
</Alert>

<Alert variant="warning" title="Warning">
  Please review before proceeding
</Alert>

<Alert variant="error" actions={
  <Button size="small" onClick={retry}>Retry</Button>
}>
  Something went wrong
</Alert>
```

### 6. Card Component

Content container:

```javascript
<Card>
  <Card.Header>
    <Card.Title>Card Title</Card.Title>
    <Card.Actions>
      <IconButton icon={<MoreIcon />} />
    </Card.Actions>
  </Card.Header>
  
  <Card.Body>
    Card content
  </Card.Body>
  
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```

## CSS Variables

```css
:root {
  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: 'Fira Code', 'Consolas', monospace;
  
  /* Colors (set by theme) */
  --color-background: #ffffff;
  --color-text: #1a1a1a;
  --color-primary: #1caad9;
  --color-border: #e0e0e0;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
  
  /* Z-index layers */
  --z-dropdown: 100;
  --z-modal: 200;
  --z-toast: 300;
}
```

## Usage Examples

### Themed Form

```jsx
function SettingsForm() {
  const theme = useTheme();
  
  return (
    <Card>
      <Card.Header>
        <Card.Title>Settings</Card.Title>
      </Card.Header>
      
      <Card.Body>
        <FormField label="Display Name" required>
          <Input value={name} onChange={setName} />
        </FormField>
        
        <FormField label="Bio">
          <Textarea value={bio} onChange={setBio} />
        </FormField>
        
        <FormField label="Notifications">
          <Toggle
            checked={notifications}
            onChange={setNotifications}
            label="Email notifications"
          />
        </FormField>
      </Card.Body>
      
      <Card.Footer>
        <Button variant="primary">Save Changes</Button>
      </Card.Footer>
    </Card>
  );
}
```

## CSS Classes

```css
/* Typography */
.heading { }
.heading--1 { }
.heading--2 { }
.text { }
.text--large { }
.text--small { }
.caption { }

/* Modal */
.modal-overlay { }
.modal { }
.modal--small { }
.modal--large { }
.modal__header { }
.modal__body { }
.modal__footer { }

/* Forms */
.form-field { }
.form-field__label { }
.form-field__error { }
.form-field__help { }

/* Card */
.card { }
.card__header { }
.card__body { }
.card__footer { }

/* Alert */
.alert { }
.alert--info { }
.alert--success { }
.alert--warning { }
.alert--error { }
```

## Notes

- Filename is misleading - contains UI infrastructure, not WebGL post-processing
- Complete typography scale
- Light/dark theme system
- Modal and dialog components
- Form field components
- Alert and notification components
