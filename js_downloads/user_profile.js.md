# user_profile.js

## Overview
Minified Sketchfab webpack module containing user profile functionality including avatars, usernames, badges, and follow functionality.

## File Status
- **Status**: Minified/Compiled
- **Build**: Webpack bundle (module 3769)
- **Purpose**: User profile display and interaction

## Key Components

### User Profile Display
- User avatar rendering
- Username display with formatting
- Display name handling
- User badges and plan indicators

### Avatar Component
- Responsive image sizing
- Multiple image resolution support
- Alt text for accessibility
- Image lazy loading

### User Badges
- Plan badges (Staff, Master, Organization, etc.)
- Account type indicators (Basic, Pro, Premium, Business, Enterprise)
- Badge linking to plan information
- Visual badge styling

### Follow Functionality
- Follow/Unfollow button component
- Follow state management
- Authentication checks
- Follow count display
- Follower/Following navigation

### User Summary
- User summary popups
- Profile hover cards
- Quick stats display (model count, view count, likes)
- Recent model thumbnails
- Follower count with formatting

## Technical Details
- React components
- Redux state management
- Conditional rendering based on user status
- Authentication integration
- Real-time state updates

## Key Functions
- `LvQi.Z`: Main username display component
- `iqY9.Z`: Follow button component
- `jyRc.Z`: Avatar component
- `BNNE.Z`: User summary card

## Use Cases
- Displaying user information across the site
- User profile cards and hovers
- Following/unfollowing users
- Showing user badges and achievements
- Quick user statistics

## Dependencies
- React
- Redux
- Sketchfab routing system
- Authentication module
- Image handling utilities

## Features
- Responsive design
- Accessibility support
- Real-time updates
- Interactive elements
- Profile navigation

## Notes
This module is core to the Sketchfab social features, enabling user interactions, profile displays, and social graph management. It's used throughout the platform wherever user information needs to be displayed.
