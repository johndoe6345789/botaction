# user_profile.js

## Overview

This file contains **user profile display components** including follow functionality, user cards, and profile information display.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~65KB (minified)
- **Type**: React user profile components
- **Framework**: React

## Core Components

### 1. FollowButton

Follow/unfollow user action:

```javascript
<FollowButton
  user={user}
  isFollowing={isFollowing}
  onFollow={() => handleFollow(user.uid)}
  onUnfollow={() => handleUnfollow(user.uid)}
  size="medium"  // 'small' | 'medium' | 'large'
/>

// States:
// - "Follow" (not following)
// - "Following" (currently following)
// - Loading state during action
```

### 2. UserAvatar

User avatar display:

```javascript
<UserAvatar
  user={user}
  size="large"   // 'small' | 'medium' | 'large' | 'xlarge'
  showBadge={true}
  linked={true}  // Link to profile
/>

// Features:
// - Multiple size presets
// - Verified badge
// - Pro badge
// - Fallback for missing avatar
```

### 3. UserName

Username with badges:

```javascript
<UserName
  user={user}
  showBadges={true}
  linked={true}
/>

// Badges:
// - Verified checkmark
// - Pro account indicator
// - Staff badge
// - Seller badge
```

### 4. UserSummary Popup

Hover card with user info:

```javascript
<UserSummary
  user={user}
  trigger={<UserName user={user} />}
  placement="bottom"
/>

// Shows:
// - Avatar
// - Display name / username
// - Bio (truncated)
// - Follower/following counts
// - Model count
// - Model thumbnails
// - Follow button
```

### 5. ToggleFollow HOC

Higher-order component for follow state:

```javascript
const EnhancedComponent = withToggleFollow(BaseComponent);

// Provides:
// - isFollowing
// - onToggleFollow
// - isLoading
```

## User Object Structure

```javascript
const user = {
  uid: 'user-123',
  username: 'johndoe',
  displayName: 'John Doe',
  
  // Avatar
  avatars: {
    images: [
      { url: '...', size: 32 },
      { url: '...', size: 64 },
      { url: '...', size: 128 }
    ]
  },
  
  // Profile
  bio: 'User bio description...',
  location: 'New York, USA',
  website: 'https://example.com',
  
  // Stats
  followerCount: 1500,
  followingCount: 250,
  modelCount: 45,
  likeCount: 3200,
  
  // Status
  isVerified: true,
  isPro: false,
  isStaff: false,
  isSeller: true,
  
  // Timestamps
  createdAt: '2020-01-15T00:00:00Z',
  lastSeenAt: '2023-06-01T12:00:00Z'
};
```

## User Stats Component

```javascript
<UserStats user={user} />

// Displays:
// - Models: 45
// - Followers: 1.5K
// - Following: 250
// - Likes received: 3.2K
```

## User Profile Card

```javascript
<UserProfileCard
  user={user}
  showStats={true}
  showBio={true}
  showFollow={true}
  compact={false}
/>

// Full profile card with:
// - Avatar
// - Name and username
// - Bio
// - Stats
// - Follow button
// - Social links
```

## Follow Modal

```javascript
<FollowersModal
  user={user}
  type="followers"  // 'followers' | 'following'
  isOpen={isOpen}
  onClose={handleClose}
/>

// Shows paginated list of:
// - User avatar
// - User name
// - Follow/unfollow button
// - User stats preview
```

## Usage Examples

### Profile Page Header

```jsx
function ProfileHeader({ user }) {
  const currentUser = useCurrentUser();
  const isOwnProfile = currentUser?.uid === user.uid;
  
  return (
    <header className="profile-header">
      <UserAvatar user={user} size="xlarge" />
      
      <div className="profile-info">
        <UserName user={user} showBadges />
        <span className="username">@{user.username}</span>
        {user.bio && <p className="bio">{user.bio}</p>}
        <UserStats user={user} />
      </div>
      
      {!isOwnProfile && (
        <FollowButton 
          user={user}
          size="large"
        />
      )}
    </header>
  );
}
```

### User Hover Card

```jsx
function ModelAuthor({ model }) {
  return (
    <UserSummary 
      user={model.user}
      trigger={
        <div className="author">
          <UserAvatar user={model.user} size="small" />
          <UserName user={model.user} />
        </div>
      }
    />
  );
}
```

### Followers List

```jsx
function FollowersList({ user }) {
  const [modalType, setModalType] = useState(null);
  
  return (
    <>
      <div className="stats">
        <button onClick={() => setModalType('followers')}>
          {formatCount(user.followerCount)} followers
        </button>
        <button onClick={() => setModalType('following')}>
          {formatCount(user.followingCount)} following
        </button>
      </div>
      
      <FollowersModal
        user={user}
        type={modalType}
        isOpen={!!modalType}
        onClose={() => setModalType(null)}
      />
    </>
  );
}
```

## CSS Classes

```css
.user-avatar { }
.user-avatar--small { width: 32px; height: 32px; }
.user-avatar--medium { width: 48px; height: 48px; }
.user-avatar--large { width: 64px; height: 64px; }
.user-avatar--xlarge { width: 128px; height: 128px; }

.user-name { }
.user-name__display { }
.user-name__badges { }
.user-name__badge { }
.user-name__badge--verified { }
.user-name__badge--pro { }

.user-summary { }
.user-summary__card { }
.user-summary__header { }
.user-summary__stats { }
.user-summary__models { }

.follow-button { }
.follow-button--following { }
.follow-button--loading { }
```

## Notes

- Complete user profile component system
- Hover card for quick user preview
- Follow/unfollow with optimistic updates
- Responsive avatar sizes
- Badge system for user types
