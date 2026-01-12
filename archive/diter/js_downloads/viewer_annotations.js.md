# viewer_annotations.js

## Overview

This file contains **banner and countdown components** - promotional banners, sale countdowns, and notification bar components. NOT 3D annotation features as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~38KB (minified)
- **Type**: React promotional components
- **Framework**: React

## Core Components

### 1. PromoBanner

Site-wide promotional banner:

```javascript
<PromoBanner
  id="black-friday-2024"
  message="Black Friday Sale - 50% off Pro plans!"
  link="/plans"
  linkText="Get the deal"
  backgroundColor="#1a1a1a"
  textColor="#ffffff"
  dismissible={true}
  onDismiss={() => handleDismiss('black-friday-2024')}
/>
```

### Banner Configuration

```javascript
const bannerConfig = {
  // Identification
  id: 'promo-123',          // Unique ID for dismiss tracking
  
  // Content
  message: 'Sale message',
  link: '/url',
  linkText: 'Click here',
  icon: 'sale',             // Optional icon
  
  // Styling
  backgroundColor: '#1caad9',
  textColor: '#ffffff',
  accentColor: '#ffd700',
  
  // Behavior
  dismissible: true,
  autoDismiss: false,
  autoDismissDelay: 10000,  // ms
  
  // Display
  position: 'top',          // 'top' | 'bottom'
  sticky: true,
  
  // Scheduling
  startDate: '2024-11-25T00:00:00Z',
  endDate: '2024-11-30T23:59:59Z'
};
```

### 2. CountdownTimer

Sale/event countdown:

```javascript
<CountdownTimer
  endDate="2024-12-01T00:00:00Z"
  onComplete={() => handleCountdownEnd()}
  showDays={true}
  showHours={true}
  showMinutes={true}
  showSeconds={true}
  compact={false}
/>
```

### Countdown Implementation

```javascript
function useCountdown(endDate) {
  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft(endDate));
  
  useEffect(() => {
    const timer = setInterval(() => {
      const remaining = calculateTimeLeft(endDate);
      setTimeLeft(remaining);
      
      if (remaining.total <= 0) {
        clearInterval(timer);
      }
    }, 1000);
    
    return () => clearInterval(timer);
  }, [endDate]);
  
  return timeLeft;
}

function calculateTimeLeft(endDate) {
  const total = new Date(endDate) - new Date();
  
  if (total <= 0) {
    return { total: 0, days: 0, hours: 0, minutes: 0, seconds: 0 };
  }
  
  return {
    total,
    days: Math.floor(total / (1000 * 60 * 60 * 24)),
    hours: Math.floor((total / (1000 * 60 * 60)) % 24),
    minutes: Math.floor((total / (1000 * 60)) % 60),
    seconds: Math.floor((total / 1000) % 60)
  };
}
```

### 3. NotificationBar

Top notification strip:

```javascript
<NotificationBar
  type="info"        // 'info' | 'warning' | 'success' | 'error'
  message="Scheduled maintenance on Sunday at 2AM UTC"
  dismissible={true}
  icon={<InfoIcon />}
/>
```

### Notification Types

```javascript
const notificationTypes = {
  info: {
    backgroundColor: '#e3f2fd',
    borderColor: '#1976d2',
    textColor: '#1565c0',
    icon: 'info-circle'
  },
  warning: {
    backgroundColor: '#fff3e0',
    borderColor: '#f57c00',
    textColor: '#e65100',
    icon: 'exclamation-triangle'
  },
  success: {
    backgroundColor: '#e8f5e9',
    borderColor: '#4caf50',
    textColor: '#2e7d32',
    icon: 'check-circle'
  },
  error: {
    backgroundColor: '#ffebee',
    borderColor: '#f44336',
    textColor: '#c62828',
    icon: 'times-circle'
  }
};
```

### 4. SaleBadge

Product/plan sale indicator:

```javascript
<SaleBadge
  originalPrice={29.99}
  salePrice={14.99}
  percentOff={50}
  endDate="2024-12-01"
/>

// Renders:
// 50% OFF
// Was $29.99
// $14.99
```

### 5. AnnouncementBanner

Large announcement with image:

```javascript
<AnnouncementBanner
  title="Introducing AI Tools"
  description="Create 3D models from text or images with our new AI-powered tools."
  image="/images/ai-tools-banner.jpg"
  ctaText="Try Now"
  ctaLink="/ai-tools"
  secondaryCtaText="Learn More"
  secondaryCtaLink="/blog/ai-tools"
/>
```

## Scheduled Banners

```javascript
// Banner scheduling system
const scheduledBanners = [
  {
    id: 'black-friday',
    startDate: '2024-11-25',
    endDate: '2024-11-30',
    priority: 10,
    banner: <BlackFridayBanner />
  },
  {
    id: 'cyber-monday',
    startDate: '2024-12-01',
    endDate: '2024-12-02',
    priority: 10,
    banner: <CyberMondayBanner />
  },
  {
    id: 'default-promo',
    startDate: null,
    endDate: null,
    priority: 1,
    banner: <DefaultPromoBanner />
  }
];

function getActiveBanner(banners) {
  const now = new Date();
  
  return banners
    .filter(b => {
      if (b.startDate && new Date(b.startDate) > now) return false;
      if (b.endDate && new Date(b.endDate) < now) return false;
      return true;
    })
    .sort((a, b) => b.priority - a.priority)[0];
}
```

## Dismiss Tracking

```javascript
// Track dismissed banners in localStorage
const DISMISSED_KEY = 'dismissed_banners';

function isDismissed(bannerId) {
  const dismissed = JSON.parse(localStorage.getItem(DISMISSED_KEY) || '[]');
  return dismissed.includes(bannerId);
}

function dismissBanner(bannerId) {
  const dismissed = JSON.parse(localStorage.getItem(DISMISSED_KEY) || '[]');
  if (!dismissed.includes(bannerId)) {
    dismissed.push(bannerId);
    localStorage.setItem(DISMISSED_KEY, JSON.stringify(dismissed));
  }
}

function resetDismissed() {
  localStorage.removeItem(DISMISSED_KEY);
}
```

## Usage Examples

### Sale Page Banner

```jsx
function SalePage() {
  const saleEnd = '2024-12-01T00:00:00Z';
  const [saleEnded, setSaleEnded] = useState(false);
  
  return (
    <div className="sale-page">
      <PromoBanner
        message="Flash Sale! 50% off all plans"
        backgroundColor="#ff4444"
      />
      
      <div className="sale-header">
        <h1>Black Friday Sale</h1>
        
        {!saleEnded ? (
          <>
            <p>Sale ends in:</p>
            <CountdownTimer
              endDate={saleEnd}
              onComplete={() => setSaleEnded(true)}
            />
          </>
        ) : (
          <p>Sale has ended</p>
        )}
      </div>
      
      <PlanPricing showSalePrices={!saleEnded} />
    </div>
  );
}
```

### Site-Wide Notification

```jsx
function Layout({ children }) {
  const [notification, setNotification] = useState(null);
  
  useEffect(() => {
    fetchSiteNotification().then(setNotification);
  }, []);
  
  return (
    <>
      {notification && (
        <NotificationBar
          type={notification.type}
          message={notification.message}
          dismissible={notification.dismissible}
          onDismiss={() => setNotification(null)}
        />
      )}
      
      <Header />
      <main>{children}</main>
      <Footer />
    </>
  );
}
```

## CSS Classes

```css
/* Promo Banner */
.promo-banner { }
.promo-banner__content { }
.promo-banner__message { }
.promo-banner__link { }
.promo-banner__dismiss { }

/* Countdown */
.countdown { }
.countdown__item { }
.countdown__value { }
.countdown__label { }
.countdown--compact { }

/* Notification Bar */
.notification-bar { }
.notification-bar--info { }
.notification-bar--warning { }
.notification-bar--success { }
.notification-bar--error { }
.notification-bar__icon { }
.notification-bar__message { }
.notification-bar__dismiss { }

/* Sale Badge */
.sale-badge { }
.sale-badge__percent { }
.sale-badge__original-price { }
.sale-badge__sale-price { }
```

## Notes

- Filename is misleading - contains promotional banners, not 3D annotations
- Countdown timer with automatic updates
- Dismissible banners with localStorage persistence
- Scheduled banner system
- Various notification types (info, warning, error, success)
