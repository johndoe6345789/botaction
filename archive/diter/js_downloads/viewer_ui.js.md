# viewer_ui.js

## Overview

This file contains the **Public Suffix List (PSL) data** - a comprehensive database of top-level domains and domain suffixes. Used for domain parsing, cookie scope validation, and URL handling. This is NOT UI components despite the filename.

## File Information

- **Status**: Active data module
- **Size**: ~220KB (minified)
- **Type**: Domain suffix database
- **Data Source**: publicsuffix.org

## Purpose

The Public Suffix List is used to:
1. Determine the registrable domain from a URL
2. Validate cookie domain scope
3. Parse subdomains correctly
4. Handle special TLDs (.co.uk, .com.au, etc.)

## Data Structure

```javascript
// The file contains a large rules array
const publicSuffixList = [
  // Generic TLDs
  'com',
  'net',
  'org',
  'edu',
  'gov',
  'mil',
  
  // Country-code TLDs
  'uk',
  'de',
  'fr',
  'jp',
  'cn',
  
  // Second-level domains
  'co.uk',
  'com.au',
  'co.jp',
  'com.br',
  
  // Special rules
  '*.ck',           // Wildcard: all subdomains of .ck
  '!www.ck',        // Exception: www.ck is not a suffix
  
  // Private domains (optional)
  'github.io',
  'herokuapp.com',
  'amazonaws.com',
  's3.amazonaws.com',
  
  // Many more...
];
```

## Module Functions

### Get Public Suffix

```javascript
// Find the public suffix for a domain
function getPublicSuffix(domain) {
  const parts = domain.toLowerCase().split('.');
  
  // Check from longest to shortest
  for (let i = 0; i < parts.length; i++) {
    const candidate = parts.slice(i).join('.');
    
    if (isPublicSuffix(candidate)) {
      return candidate;
    }
  }
  
  return parts[parts.length - 1];
}

// Examples:
getPublicSuffix('www.example.com');       // 'com'
getPublicSuffix('www.example.co.uk');     // 'co.uk'
getPublicSuffix('foo.bar.tokyo.jp');      // 'tokyo.jp'
getPublicSuffix('test.github.io');        // 'github.io'
```

### Get Registrable Domain

```javascript
// Get the registrable domain (public suffix + one label)
function getRegistrableDomain(domain) {
  const suffix = getPublicSuffix(domain);
  const parts = domain.toLowerCase().split('.');
  const suffixParts = suffix.split('.');
  
  // Get one label before the suffix
  const registrableParts = parts.slice(-(suffixParts.length + 1));
  return registrableParts.join('.');
}

// Examples:
getRegistrableDomain('www.example.com');      // 'example.com'
getRegistrableDomain('www.example.co.uk');    // 'example.co.uk'
getRegistrableDomain('foo.bar.example.com');  // 'example.com'
getRegistrableDomain('username.github.io');   // 'username.github.io'
```

### Is Public Suffix

```javascript
// Check if a domain is a public suffix
function isPublicSuffix(domain) {
  return publicSuffixList.includes(domain.toLowerCase());
}

// Examples:
isPublicSuffix('com');        // true
isPublicSuffix('co.uk');      // true
isPublicSuffix('example.com'); // false
```

### Parse Domain

```javascript
// Full domain parsing
function parseDomain(url) {
  const hostname = new URL(url).hostname;
  const publicSuffix = getPublicSuffix(hostname);
  const registrableDomain = getRegistrableDomain(hostname);
  
  const parts = hostname.split('.');
  const regParts = registrableDomain.split('.');
  const subdomain = parts.slice(0, -(regParts.length)).join('.');
  const domainName = regParts[0];
  
  return {
    hostname,           // 'www.example.co.uk'
    subdomain,          // 'www'
    domain: domainName, // 'example'
    publicSuffix,       // 'co.uk'
    registrableDomain   // 'example.co.uk'
  };
}

// Example:
parseDomain('https://www.example.co.uk/path');
// {
//   hostname: 'www.example.co.uk',
//   subdomain: 'www',
//   domain: 'example',
//   publicSuffix: 'co.uk',
//   registrableDomain: 'example.co.uk'
// }
```

## Cookie Domain Validation

```javascript
// Validate cookie domain scope
function isValidCookieDomain(cookieDomain, requestDomain) {
  // Cookie domain must be the request domain or a parent
  if (!requestDomain.endsWith(cookieDomain)) {
    return false;
  }
  
  // Cannot set cookie for a public suffix
  if (isPublicSuffix(cookieDomain.replace(/^\./, ''))) {
    return false;
  }
  
  return true;
}

// Examples:
isValidCookieDomain('.example.com', 'www.example.com');  // true
isValidCookieDomain('.com', 'www.example.com');          // false (public suffix)
isValidCookieDomain('.co.uk', 'www.example.co.uk');      // false (public suffix)
```

## Wildcard Rules

```javascript
// Handle wildcard rules like *.ck
function matchesWildcard(domain, rule) {
  if (rule.startsWith('*.')) {
    const suffix = rule.slice(2);
    return domain.endsWith('.' + suffix) && 
           domain.split('.').length > suffix.split('.').length;
  }
  return false;
}

// Handle exception rules like !www.ck
function isException(domain, rule) {
  if (rule.startsWith('!')) {
    return domain === rule.slice(1);
  }
  return false;
}
```

## Use Cases in Sketchfab

### Cross-Origin Checks

```javascript
// Check if two URLs are same-site
function isSameSite(url1, url2) {
  const domain1 = getRegistrableDomain(new URL(url1).hostname);
  const domain2 = getRegistrableDomain(new URL(url2).hostname);
  return domain1 === domain2;
}

isSameSite('https://sketchfab.com', 'https://api.sketchfab.com');  // true
isSameSite('https://sketchfab.com', 'https://evil.com');          // false
```

### Embed Domain Validation

```javascript
// Validate embed allowed domains
function isEmbedAllowed(embedDomain, allowedDomains) {
  const registrable = getRegistrableDomain(embedDomain);
  
  return allowedDomains.some(allowed => {
    const allowedRegistrable = getRegistrableDomain(allowed);
    return registrable === allowedRegistrable;
  });
}
```

## Data Categories

The PSL includes:

1. **ICANN Domains** - Official TLDs
   - Generic: .com, .org, .net
   - Country-code: .uk, .de, .jp
   - New gTLDs: .xyz, .app, .dev

2. **Private Domains** - Services that act like TLDs
   - Platform: github.io, herokuapp.com
   - Cloud: amazonaws.com, azurewebsites.net
   - CDN: cloudfront.net, akamaized.net

## Notes

- Filename is misleading - contains domain suffix data, not UI components
- Essential for correct domain parsing
- Used for cookie scope validation
- Updated periodically from publicsuffix.org
- Large data file (~220KB of domain rules)
