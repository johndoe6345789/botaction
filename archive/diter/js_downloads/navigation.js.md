# navigation.js

## Overview

This file contains **Sketchfab's site-wide navigation and header components**, including the main navigation bar, search functionality, category navigation, and authentication UI.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~107KB (minified)
- **Type**: React navigation components
- **Framework**: React with Redux

## Core Components

### 1. PageHeader

Main site header component:

```javascript
<PageHeader
  transparent={false}    // For hero sections
  sticky={true}          // Fixed positioning
  showSearch={true}      // Search bar visibility
/>

// Structure:
// <header>
//   <Logo />
//   <NavigationMenu />
//   <SearchBar />
//   <AuthButtons /> or <UserMenu />
// </header>
```

### 2. NavigationHighlights

Quick access links:

```javascript
const highlights = [
  { key: 'popular', label: 'Popular', href: '/store/popular' },
  { key: 'staffPicks', label: 'Staff Picks', href: '/store/staff-picks' },
  { key: 'downloadable', label: 'Downloadable', href: '/store/downloadable' },
  { key: 'collections', label: 'Collections', href: '/store/collections' }
];
```

### 3. CategoryNavigation

Hierarchical category browser:

```javascript
// Main categories:
// Animals & Pets, Architecture, Art & Abstract,
// Cars & Vehicles, Characters & Creatures,
// Cultural Heritage, Electronics, Fashion,
// Food & Drink, Furniture, Music, Nature,
// People, Places & Travel, Science & Tech,
// Sports & Fitness, Weapons & Military

// Features:
// - Expandable subcategories
// - Model count badges
// - Keyboard navigation
```

### 4. SearchOverlay

Full-screen search:

```javascript
// Features:
// - Autocomplete suggestions
// - Recent searches (localStorage)
// - Filter by: Models, Collections, Users
// - Tag/user search syntax: "tag:vehicle user:john car"

// Keyboard shortcuts:
// Escape - Close
// Enter - Execute search
// Up/Down - Navigate suggestions
```

### 5. AuthButtons

```javascript
// Unauthenticated:
<AuthButtons>
  <Button variant="secondary" onClick={openLogin}>Log In</Button>
  <Button variant="primary" onClick={openSignup}>Sign Up</Button>
</AuthButtons>

// Authenticated: Shows UserMenu with dropdown
```

### 6. UploadDropdown

Model upload menu:

```javascript
// Menu items:
// - Upload 3D Model (main)
// - Import from URL
// - Create from AI (feature flagged)

// Supports drag-and-drop file zone
```

### 7. Store Navigation

E-commerce section:

```javascript
const sections = [
  { title: 'Browse', items: ['All Models', 'Categories', 'Collections'] },
  { title: 'Trending', items: ['New', 'Popular', 'Staff Picks'] },
  { title: 'Sell', items: ['Become a Seller', 'Seller Dashboard'] }
];
```

## Transparent Header Mode

For hero images:

```javascript
// Starts transparent, becomes solid on scroll
useEffect(() => {
  const handleScroll = () => {
    setIsScrolled(window.scrollY > 100);
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  return () => window.removeEventListener('scroll', handleScroll);
}, []);
```

## Mobile Navigation

Responsive hamburger menu:

```javascript
// Breakpoints:
// Desktop (>1024px): Full navigation bar
// Tablet (768-1024px): Collapsed secondary items
// Mobile (<768px): Hamburger with slide-out menu
```

## AI Feature Integration

```javascript
// Feature flags checked:
const AI_FEATURES = {
  textTo3D: 'ai_text_to_3d',
  imageToMesh: 'ai_image_to_mesh',
  autoRigging: 'ai_auto_rigging'
};

// Conditional menu items based on user.features
```

## Search Query Syntax

```javascript
// Supported syntax:
"car"                      // Simple search
"tag:vehicle"              // Filter by tag
"user:john"                // Filter by user
"tag:vehicle user:john car" // Combined

// Parser extracts:
{ tags: ["vehicle"], user: "john", q: "car" }
```

## Redux Integration

```javascript
// Connected state
const mapStateToProps = {
  user: authSelectors.user,
  isAuthenticated: authSelectors.isAuthenticated,
  categories: entitySelectors.allCategories,
  cartCount: cartSelectors.itemCount
};

// Actions
const mapDispatchToProps = {
  openLoginPopup,
  openSignupPopup,
  logout
};
```

## Accessibility

```javascript
// ARIA attributes
<nav role="navigation" aria-label="Main navigation">
<button aria-expanded={isOpen} aria-controls="mobile-menu">
<ul role="menubar">
<li role="menuitem">

// Keyboard: Tab, Enter/Space, Arrow keys, Escape
```

## Styling

```css
.page-header { }
.page-header--transparent { }
.page-header--scrolled { }
.nav-menu { }
.nav-menu__item { }
.nav-menu__dropdown { }
```
