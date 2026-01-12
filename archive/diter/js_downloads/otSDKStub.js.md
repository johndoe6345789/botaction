# otSDKStub.js

## Overview

This file contains the **OneTrust SDK Stub** - a placeholder/stub for the OneTrust cookie consent management platform. It provides the OneTrust API interface for GDPR/CCPA cookie consent banners.

## File Information

- **Status**: Active SDK stub
- **Size**: ~15KB (minified)
- **Type**: Cookie consent SDK
- **Vendor**: OneTrust

## Purpose

OneTrust is a privacy management platform that:
- Displays cookie consent banners
- Manages user consent preferences
- Categorizes cookies (essential, analytics, marketing, etc.)
- Complies with GDPR, CCPA, and other privacy regulations

This stub provides the API interface before the full SDK loads.

## Core API

### OneTrust Global Object

```javascript
// OneTrust global namespace
window.OneTrust = {
  // Consent management
  AllowAll: function() { },
  RejectAll: function() { },
  ToggleInfoDisplay: function() { },
  
  // Get consent status
  IsAlertBoxClosed: function() { return false; },
  GetDomainData: function() { return {}; },
  
  // Category consent
  GetActiveGroups: function() { return ',C0001,C0002,'; },
  IsActiveGroup: function(group) { return true; }
};
```

### OptanonWrapper Function

```javascript
// Callback fired when consent changes
function OptanonWrapper() {
  // Called when:
  // - Banner is shown
  // - User makes consent choice
  // - Page loads with existing consent
  
  const activeGroups = OneTrust.GetActiveGroups();
  
  // Check specific category consent
  if (activeGroups.includes(',C0002,')) {
    // Performance cookies allowed
    enableAnalytics();
  }
  
  if (activeGroups.includes(',C0003,')) {
    // Functional cookies allowed
    enableFunctionalCookies();
  }
  
  if (activeGroups.includes(',C0004,')) {
    // Targeting cookies allowed
    enableMarketingPixels();
  }
}
```

### Consent Categories

```javascript
// Standard OneTrust consent category IDs
const consentCategories = {
  C0001: 'Strictly Necessary',     // Always active
  C0002: 'Performance',            // Analytics, metrics
  C0003: 'Functional',             // Preferences, features
  C0004: 'Targeting',              // Advertising, retargeting
  C0005: 'Social Media'            // Social sharing, embeds
};
```

### Optanon Global Variables

```javascript
// Data layer variables set by OneTrust
window.OptanonActiveGroups = ',C0001,C0002,';  // Active consent groups
window.OptanonConsent = 'isIABGlobal=false&...';  // Consent string

// Wait for consent before loading scripts
if (window.OptanonActiveGroups.includes(',C0002,')) {
  // Load analytics
}
```

## Integration Patterns

### Conditional Script Loading

```javascript
// Load scripts based on consent
function loadScriptWithConsent(category, src) {
  if (OneTrust.IsActiveGroup(category)) {
    const script = document.createElement('script');
    script.src = src;
    document.head.appendChild(script);
  }
}

// In OptanonWrapper
function OptanonWrapper() {
  // Analytics (C0002)
  loadScriptWithConsent('C0002', 'https://www.google-analytics.com/analytics.js');
  
  // Marketing (C0004)
  loadScriptWithConsent('C0004', 'https://connect.facebook.net/en_US/fbevents.js');
}
```

### Script Tag Blocking

```html
<!-- Blocked by default, activated on consent -->
<script 
  type="text/plain"
  class="optanon-category-C0002"
  src="https://analytics.example.com/script.js"
></script>

<!-- OneTrust converts type to text/javascript when C0002 is consented -->
```

### Open Preferences Center

```javascript
// Button to open cookie preferences
document.getElementById('cookie-preferences').addEventListener('click', function() {
  OneTrust.ToggleInfoDisplay();
});

// Or with link
<a href="#" onclick="OneTrust.ToggleInfoDisplay(); return false;">
  Cookie Preferences
</a>
```

## Stub Implementation

```javascript
// Minimal stub before full SDK loads
(function() {
  window.OneTrust = window.OneTrust || {};
  window.OptanonActiveGroups = window.OptanonActiveGroups || '';
  
  // Stub methods
  const stubMethods = [
    'AllowAll',
    'RejectAll', 
    'ToggleInfoDisplay',
    'Close',
    'Init',
    'LoadBanner',
    'OnConsentChanged'
  ];
  
  stubMethods.forEach(method => {
    if (!window.OneTrust[method]) {
      window.OneTrust[method] = function() {
        console.log('OneTrust.' + method + ' called (stub)');
      };
    }
  });
  
  // Stub getters
  window.OneTrust.GetActiveGroups = function() {
    return window.OptanonActiveGroups;
  };
  
  window.OneTrust.IsActiveGroup = function(group) {
    return window.OptanonActiveGroups.includes(',' + group + ',');
  };
})();
```

## Configuration

```javascript
// OneTrust configuration (loaded via CDN)
window.OptanonScriptConfig = {
  domainScript: '12345678-1234-1234-1234-123456789012',
  language: 'en',
  crossDomain: true,
  useAutoBlockingScript: true,
  customCSS: null
};

// Banner customization
window.OneTrustBannerSettings = {
  position: 'bottom',
  theme: 'dark',
  closeButton: true,
  showCloseButton: false
};
```

## Events

```javascript
// Listen for consent changes
window.addEventListener('OneTrustGroupsUpdated', function(event) {
  const { detail } = event;
  
  // detail.groups contains updated consent groups
  console.log('Consent updated:', detail.groups);
  
  // React to consent changes
  if (detail.groups.includes('C0002')) {
    initializeAnalytics();
  }
});

// Banner closed event
window.addEventListener('OneTrustBannerClosed', function() {
  console.log('User closed the banner');
});
```

## Usage in Sketchfab

```javascript
// Sketchfab's OptanonWrapper implementation
function OptanonWrapper() {
  const activeGroups = OneTrust.GetActiveGroups();
  
  // Google Analytics
  if (activeGroups.includes(',C0002,')) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      'event': 'analytics_consent_granted'
    });
  }
  
  // Marketing pixels
  if (activeGroups.includes(',C0004,')) {
    // Facebook Pixel
    // Google Ads
    // LinkedIn Insight
  }
  
  // Third-party embeds (YouTube, etc.)
  if (activeGroups.includes(',C0005,')) {
    enableThirdPartyEmbeds();
  }
}
```

## CSS for Banner

```css
/* OneTrust banner customization */
#onetrust-banner-sdk {
  font-family: 'Inter', sans-serif !important;
}

#onetrust-accept-btn-handler,
#onetrust-reject-all-handler {
  background-color: #1caad9 !important;
}

#onetrust-pc-btn-handler {
  color: #1caad9 !important;
}

.ot-sdk-show-settings {
  color: #1caad9 !important;
  cursor: pointer;
}
```

## Notes

- Cookie consent management SDK stub
- Provides OneTrust API before full SDK loads
- GDPR/CCPA compliance for cookie consent
- Categorized consent (necessary, analytics, marketing)
- Blocks scripts until consent is given
- Common privacy management platform
