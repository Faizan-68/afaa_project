# Google OAuth Referral System - Testing Guide

## How it Works

### 1. Normal Signup (Manual Form)
- User fills signup form with referral code
- Referral processed in `views.py` 
- Works: ✅

### 2. Google Signup with Referral 
- User visits: `http://localhost:8000/signup/?ref=faizan`
- Referral code stored in session
- User clicks "Continue with Google"
- After Google auth, referral assigned via signals
- Works: ✅ (Now implemented)

### 3. Direct Google Login with Referral
- User visits: `http://localhost:8000/accounts/google/login/?ref=faizan`
- Middleware captures referral code
- Signal assigns referral after login
- Works: ✅ (Now implemented)

## Testing URLs

### Test 1: Signup Page with Referral
```
http://127.0.0.1:8000/signup/?ref=faizan
```
- Should store 'faizan' in session
- Google button should include referral in URL
- After Google signup, user should have referral set

### Test 2: Direct Google Login with Referral  
```
http://127.0.0.1:8000/accounts/google/login/?ref=faizan
```
- Should work for both new and existing users
- Referral assigned via middleware + signals

## What Happens

1. **Middleware**: Captures `?ref=` or `?referral=` parameters
2. **Session**: Stores referral code across requests
3. **Signals**: `social_account_added` signal assigns referral for new users
4. **Signals**: `pre_social_login` signal assigns referral for existing users
5. **Referral Chain**: Automatically creates 3-level referral chain

## Files Modified

1. **accounts/signals.py** - Social login signal handlers
2. **accounts/middleware.py** - Referral URL parameter capture  
3. **accounts/views.py** - Signup view referral handling
4. **accounts/templates/signup.html** - Google button URL modification
5. **afaa_project/settings.py** - Added middleware
6. **accounts/apps.py** - Signal registration

## Debug Output

Check terminal for messages like:
```
Middleware: Stored referral code in session: faizan
Social account added for newuser, referral_code in session: faizan
Social signup: Set referral newuser -> faizan
```