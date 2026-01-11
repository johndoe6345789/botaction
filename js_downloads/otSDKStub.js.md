# otSDKStub.js

## Overview
OneTrust SDK stub implementation for consent management, cookie handling, IAB Transparency & Consent Framework (TCF) integration, and Global Privacy Platform (GPP) API support.

## File Status
- **Status**: Minified
- **Vendor**: OneTrust Technologies
- **Purpose**: Privacy and consent management

## Key Components

### Consent Management
- Cookie consent tracking
- User preference management
- Consent banner display
- Consent state persistence

### IAB TCF Integration
- TCF v2.0 compliance
- Vendor consent management
- Purpose consent handling
- Consent string generation and parsing

### GPP API Implementation
- Global Privacy Platform support
- Multi-region privacy compliance
- CCPA, GDPR, and other privacy law support
- Standardized privacy signal handling

### Cookie Management
- Cookie classification (Necessary, Performance, Functional, Targeting)
- Cookie blocking/allowing based on consent
- Cookie policy enforcement
- Third-party cookie handling

## Technical Details
- Implements __tcfapi() for IAB TCF compliance
- Implements __gpp() for GPP support
- Event-driven consent updates
- Asynchronous consent loading
- CMP (Consent Management Platform) API

## Use Cases
- GDPR compliance for EU users
- CCPA compliance for California users
- Cookie consent management
- Privacy preference management
- Legal compliance across multiple jurisdictions

## Dependencies
- Browser APIs (localStorage, cookies)
- IAB TCF framework
- Global Privacy Platform specifications

## Events
- Consent changed events
- Cookie policy updates
- User preference changes
- CMP ready notifications

## Notes
This is a production SDK from OneTrust, a leading privacy management platform. It provides comprehensive consent management for websites and applications, ensuring compliance with various privacy regulations including GDPR, CCPA, and others. The stub version provides essential functionality while loading the full SDK asynchronously.
