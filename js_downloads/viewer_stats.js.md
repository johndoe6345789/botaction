# viewer_stats.js

## Overview

This file contains **model transfer popup and ownership transfer** components. It handles the UI for transferring model ownership between users. NOT viewer statistics as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~25KB (minified)
- **Type**: React modal components
- **Framework**: React

## Core Components

### 1. ModelTransferPopup

Modal for transferring model ownership:

```javascript
<ModelTransferPopup
  model={model}
  isOpen={isTransferOpen}
  onClose={() => setTransferOpen(false)}
  onTransfer={handleTransfer}
/>
```

### Transfer Flow

```javascript
// Step 1: Search for recipient
<UserSearch
  onSelect={setRecipient}
  placeholder="Search for user..."
  excludeUsers={[currentUser.uid]}
/>

// Step 2: Confirm transfer
<TransferConfirmation
  model={model}
  recipient={recipient}
  onConfirm={handleConfirm}
  onCancel={() => setRecipient(null)}
/>

// Step 3: Transfer complete
<TransferSuccess
  model={model}
  recipient={recipient}
  onClose={handleClose}
/>
```

### 2. UserSearch

Search for transfer recipient:

```javascript
<UserSearch
  value={searchQuery}
  onChange={setSearchQuery}
  onSelect={handleSelectUser}
  excludeUsers={[currentUser.uid]}  // Can't transfer to self
  minChars={3}
/>
```

### Search Results

```javascript
function UserSearchResults({ results, onSelect }) {
  if (results.length === 0) {
    return <div className="no-results">No users found</div>;
  }
  
  return (
    <ul className="user-results">
      {results.map(user => (
        <li key={user.uid} onClick={() => onSelect(user)}>
          <UserAvatar user={user} size="small" />
          <div className="user-info">
            <span className="display-name">{user.displayName}</span>
            <span className="username">@{user.username}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}
```

### 3. TransferConfirmation

Confirm transfer details:

```javascript
<TransferConfirmation
  model={model}
  recipient={recipient}
>
  <div className="transfer-warning">
    <WarningIcon />
    <h4>This action cannot be undone</h4>
    <p>
      You are about to transfer ownership of "{model.name}" to {recipient.displayName}.
      You will no longer be able to edit or delete this model.
    </p>
  </div>
  
  <div className="transfer-details">
    <TransferItem label="Model" value={model.name} />
    <TransferItem label="From" value={currentUser.displayName} />
    <TransferItem label="To" value={recipient.displayName} />
  </div>
  
  <ConfirmationCheckbox
    label="I understand that this transfer is permanent"
    checked={confirmed}
    onChange={setConfirmed}
  />
</TransferConfirmation>
```

### 4. TransferSuccess

Success confirmation:

```javascript
<TransferSuccess>
  <SuccessIcon />
  <h3>Transfer Complete</h3>
  <p>
    "{model.name}" has been transferred to {recipient.displayName}.
  </p>
  <Button onClick={onClose}>Close</Button>
</TransferSuccess>
```

## Transfer API

```javascript
// Transfer model API call
async function transferModel(modelId, recipientUserId) {
  const response = await fetch(`/api/v3/models/${modelId}/transfer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      recipientUserId
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  
  return response.json();
}
```

## Transfer Validation

```javascript
const transferValidation = {
  // Can only transfer own models
  isOwner: (model, user) => model.user.uid === user.uid,
  
  // Recipient must be a valid user
  validRecipient: (recipient) => 
    recipient && 
    recipient.uid && 
    !recipient.isDeleted,
  
  // Model must be transferable
  isTransferable: (model) => 
    !model.isDeleted && 
    !model.isPendingTransfer &&
    model.status === 'published'
};

function canTransfer(model, recipient, currentUser) {
  return (
    transferValidation.isOwner(model, currentUser) &&
    transferValidation.validRecipient(recipient) &&
    transferValidation.isTransferable(model) &&
    recipient.uid !== currentUser.uid
  );
}
```

## Full Component

```jsx
function ModelTransferPopup({ model, isOpen, onClose }) {
  const [step, setStep] = useState('search');  // 'search' | 'confirm' | 'success'
  const [recipient, setRecipient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleSelectRecipient = (user) => {
    setRecipient(user);
    setStep('confirm');
  };
  
  const handleConfirmTransfer = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await transferModel(model.uid, recipient.uid);
      setStep('success');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const handleClose = () => {
    setStep('search');
    setRecipient(null);
    setError(null);
    onClose();
  };
  
  return (
    <Modal isOpen={isOpen} onClose={handleClose}>
      <Modal.Header>
        <h2>Transfer Model</h2>
      </Modal.Header>
      
      <Modal.Body>
        {step === 'search' && (
          <UserSearch onSelect={handleSelectRecipient} />
        )}
        
        {step === 'confirm' && (
          <TransferConfirmation
            model={model}
            recipient={recipient}
            error={error}
            loading={loading}
            onConfirm={handleConfirmTransfer}
            onCancel={() => {
              setRecipient(null);
              setStep('search');
            }}
          />
        )}
        
        {step === 'success' && (
          <TransferSuccess
            model={model}
            recipient={recipient}
            onClose={handleClose}
          />
        )}
      </Modal.Body>
    </Modal>
  );
}
```

## CSS Classes

```css
/* Transfer Popup */
.transfer-popup { }
.transfer-popup__header { }
.transfer-popup__body { }

/* User Search */
.user-search { }
.user-search__input { }
.user-search__results { }
.user-search__result { }
.user-search__result--selected { }

/* Confirmation */
.transfer-confirmation { }
.transfer-warning { }
.transfer-details { }
.transfer-item { }
.transfer-item__label { }
.transfer-item__value { }

/* Success */
.transfer-success { }
.transfer-success__icon { }
.transfer-success__message { }
```

## Notes

- Filename is misleading - contains transfer popup, not viewer stats
- Multi-step wizard flow
- User search for recipient selection
- Confirmation step with warnings
- API integration for transfer
- Error handling and loading states
