# visibility_popup.js

## Overview

This file contains **model visibility settings, theme configuration, and Pro badge components**. It handles public/private model access, subscription tier features, and dark/light theme switching.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~58KB (minified)
- **Type**: React settings components
- **Framework**: React

## Core Components

### 1. Visibility Settings (`ZfMt`)

Model access control:

```javascript
<VisibilitySettings
  model={model}
  onChange={handleVisibilityChange}
/>

// Visibility options:
// - 'public': Visible to everyone
// - 'unlisted': Accessible via direct link only
// - 'private': Only owner can see
// - 'password': Protected with password
```

### Visibility Option Details

```javascript
const visibilityOptions = [
  {
    value: 'public',
    label: 'Public',
    description: 'Anyone can find and view this model',
    icon: 'globe',
    requiresPro: false
  },
  {
    value: 'unlisted',
    label: 'Unlisted',
    description: 'Only people with the link can view',
    icon: 'link',
    requiresPro: false
  },
  {
    value: 'private',
    label: 'Private',
    description: 'Only you can view this model',
    icon: 'lock',
    requiresPro: true
  },
  {
    value: 'password',
    label: 'Password Protected',
    description: 'Viewers must enter a password',
    icon: 'key',
    requiresPro: true
  }
];
```

### 2. Theme Configuration (`L4wY`)

Dark/light mode switching:

```javascript
<ThemeProvider theme={currentTheme}>
  <App />
</ThemeProvider>

// Theme values
const themes = {
  light: {
    name: 'light',
    className: 'theme-light',
    colors: {
      background: '#ffffff',
      surface: '#f5f5f5',
      text: '#1a1a1a',
      textSecondary: '#666666',
      primary: '#1caad9',
      border: '#e0e0e0'
    }
  },
  dark: {
    name: 'dark',
    className: 'theme-dark',
    colors: {
      background: '#1a1a1a',
      surface: '#2d2d2d',
      text: '#ffffff',
      textSecondary: '#999999',
      primary: '#1caad9',
      border: '#404040'
    }
  }
};
```

### Theme Hook

```javascript
function useTheme() {
  const [theme, setTheme] = useState(() => {
    // Check user preference
    const saved = localStorage.getItem('theme');
    if (saved) return saved;
    
    // Check system preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });
  
  useEffect(() => {
    document.documentElement.className = themes[theme].className;
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  const toggle = () => setTheme(t => t === 'light' ? 'dark' : 'light');
  
  return { theme, setTheme, toggle, colors: themes[theme].colors };
}
```

### 3. Theme Toggle Switch

```javascript
<ThemeToggle
  value={theme}
  onChange={setTheme}
  showLabels={true}
/>

// Renders toggle switch with sun/moon icons
```

### 4. Pro Badge (`OsBk`)

Subscription tier indicator:

```javascript
<ProBadge 
  tier="plus"          // 'basic' | 'plus' | 'pro' | 'business' | 'enterprise'
  size="small"         // 'small' | 'medium'
  showTooltip={true}
/>

// Tier badges:
// Plus: Blue badge
// Pro: Gold badge  
// Business: Purple badge
// Enterprise: Custom
```

### Subscription Tiers

```javascript
const subscriptionTiers = {
  free: {
    name: 'Free',
    badge: null,
    features: {
      privateModels: false,
      passwordProtected: false,
      downloadableModels: false,
      customBranding: false,
      maxFileSize: 100 * 1024 * 1024,  // 100MB
      monthlyUploads: 10
    }
  },
  plus: {
    name: 'Plus',
    badge: 'plus',
    badgeColor: '#1caad9',
    features: {
      privateModels: true,
      passwordProtected: true,
      downloadableModels: 5,
      customBranding: false,
      maxFileSize: 500 * 1024 * 1024,  // 500MB
      monthlyUploads: 50
    }
  },
  pro: {
    name: 'Pro',
    badge: 'pro',
    badgeColor: '#ffc107',
    features: {
      privateModels: true,
      passwordProtected: true,
      downloadableModels: 20,
      customBranding: true,
      maxFileSize: 1024 * 1024 * 1024,  // 1GB
      monthlyUploads: 200
    }
  },
  business: {
    name: 'Business',
    badge: 'business',
    badgeColor: '#9c27b0',
    features: {
      privateModels: true,
      passwordProtected: true,
      downloadableModels: 'unlimited',
      customBranding: true,
      maxFileSize: 2 * 1024 * 1024 * 1024,  // 2GB
      monthlyUploads: 'unlimited',
      teamMembers: 5
    }
  }
};
```

### 5. Feature Gate

```javascript
<FeatureGate 
  feature="privateModels"
  requiredTier="plus"
  currentTier={user.tier}
>
  {/* Content shown if user has feature */}
  <PrivateModelSettings />
</FeatureGate>

// Shows upgrade prompt if feature not available
```

### 6. Upgrade Prompt

```javascript
<UpgradePrompt
  feature="private models"
  requiredTier="plus"
  onUpgrade={() => navigate('/plans')}
/>

// "Upgrade to Plus to unlock private models"
```

## Visibility UI

### Radio Button Group

```javascript
<VisibilityOptions
  value={visibility}
  onChange={setVisibility}
  userTier={user.tier}
>
  {visibilityOptions.map(option => (
    <VisibilityOption
      key={option.value}
      value={option.value}
      label={option.label}
      description={option.description}
      icon={option.icon}
      disabled={option.requiresPro && !userHasPro}
      requiresUpgrade={option.requiresPro && !userHasPro}
    />
  ))}
</VisibilityOptions>
```

### Password Protection

```javascript
<PasswordProtection
  enabled={visibility === 'password'}
  currentPassword={model.password}
  onPasswordChange={setPassword}
>
  <PasswordInput
    label="Model password"
    value={password}
    onChange={setPassword}
    showStrength={true}
  />
  <PasswordRequirements met={passwordMeetsRequirements} />
</PasswordProtection>
```

## Usage Examples

### Model Settings Page

```jsx
function ModelSettings({ model }) {
  const [visibility, setVisibility] = useState(model.visibility);
  const [password, setPassword] = useState('');
  const user = useCurrentUser();
  
  return (
    <div className="model-settings">
      <section>
        <h3>Visibility</h3>
        <VisibilitySettings
          value={visibility}
          onChange={setVisibility}
          userTier={user.tier}
        />
        
        {visibility === 'password' && (
          <PasswordProtection
            password={password}
            onChange={setPassword}
          />
        )}
      </section>
      
      <button onClick={() => saveSettings({ visibility, password })}>
        Save Changes
      </button>
    </div>
  );
}
```

### Theme Settings

```jsx
function ThemeSettings() {
  const { theme, setTheme } = useTheme();
  
  return (
    <div className="theme-settings">
      <h3>Appearance</h3>
      
      <div className="theme-options">
        <ThemeOption
          value="light"
          label="Light"
          selected={theme === 'light'}
          onSelect={setTheme}
          preview={<LightThemePreview />}
        />
        <ThemeOption
          value="dark"
          label="Dark"
          selected={theme === 'dark'}
          onSelect={setTheme}
          preview={<DarkThemePreview />}
        />
        <ThemeOption
          value="system"
          label="System"
          selected={theme === 'system'}
          onSelect={setTheme}
          preview={<SystemThemePreview />}
        />
      </div>
    </div>
  );
}
```

## CSS Classes

```css
/* Visibility */
.visibility-settings { }
.visibility-option { }
.visibility-option--selected { }
.visibility-option--disabled { }
.visibility-option__icon { }
.visibility-option__label { }
.visibility-option__description { }
.visibility-option__upgrade-badge { }

/* Theme */
.theme-toggle { }
.theme-toggle__track { }
.theme-toggle__thumb { }
.theme-option { }
.theme-option--selected { }
.theme-preview { }

/* Pro badge */
.pro-badge { }
.pro-badge--plus { }
.pro-badge--pro { }
.pro-badge--business { }
```

## Notes

- Model visibility/access control settings
- Theme switching (dark/light mode)
- Subscription tier badges and feature gating
- Upgrade prompts for premium features
- Password protection for models
