# Admin Sign Up and Email Approval Workflow

This document outlines the proposed technical plan to implement an exclusive Admin registration flow where an admin submits a sign-up request, and the master admin approves it via email.

## Recommended Approach and Tools

For the tool, we will use **Resend**, because:
1. **It's Free:** It has a generous free tier of 3,000 emails/month which perfectly suits admin request volumes.
2. **Already Integrated:** Since it's already configured in your application (`EmailService`), we only need to add a new method for sending the admin approval email.

The best approach is to use a **Magic Link / JWT Token** flow to authorize the approval securely without requiring the master admin to be logged in at the moment they click the link (or enforcing login first). 

## Proposed Changes

### Database & Authentication Models (Backend)
No new tables are required. We will reuse the existing `User` table, setting `role=UserRole.ADMIN`, `is_verified=False` and `is_active=False` (meaning the account is pending). 

***

### Backend Component

#### [MODIFY] `app/services/email_service.py`
- Add a static method `send_admin_approval_request`
- Takes the admin `username`, `email` and the generated `approval_link`.
- The email is sent to the address defined by `settings.MASTER_ADMIN_EMAIL`.
- The `approval_link` is dynamically generated using `settings.FRONTEND_URL` so it routes correctly based on the environment (local vs production).

#### [MODIFY] `app/api/routes/auth.py`
- **New Endpoint `POST /api/auth/admin/register`:** Validates request (like regular signup). Creates the user with `is_active=False` and `role=UserRole.ADMIN`. Generates an approval JWT and invokes `email_service.send_admin_approval_request`.
- **New Endpoint `POST /api/auth/admin/approve`:** Receives the token, extracts the user ID, validates the `admin_approval` intent, and sets the user's `is_active=True` and `is_verified=True`. 

***

### Frontend Component

#### [NEW] `app/admin/signup/page.tsx`
- A dedicated Next.js app router page for Admin registration.
- Uses the same aesthetics as your existing `/signup` page but includes context indicating that sign-ups are "Subject to Master Admin Approval".
- Submits form data to the new `/api/auth/admin/register` backend endpoint.

#### [NEW] `app/admin/approve/page.tsx`
- A minimal landing page for the Master Admin when they click the email link.
- Retrieves the `token` from URL parameters and posts it to `/api/auth/admin/approve`.
- Displays a success (or error) message and gives a link to login.

## Open Questions / Clarifications

> [!NOTE]
> **Email Configuration:** The master admin email will be sourced from an environment variable (`MASTER_ADMIN_EMAIL`) instead of being hardcoded.

> [!WARNING]
> **Local Testing Constraint:**
> If you test this locally without a domain, the frontend URL will be `http://localhost:3000`. The master admin will receive an email linking to `http://localhost:3000/admin/approve...`
> - If they click this link on the **same computer** running the server, it will work perfectly.
> - If they click this link on their **mobile phone or a different computer**, it will **fail** because `localhost` points to their phone, not your computer.
> - To test approval from a *different* device while developing locally, you would need to use a tunneling tool like **ngrok** to get a public URL for your localhost, and set `FRONTEND_URL` to that ngrok URL. On production, your configured domain will be used and it will work everywhere.

## Verification Plan

### Automated Tests
- Test regular signups to ensure they remain unaffected.
- Test admin signups to confirm inactive creation and token generation.

### Manual Verification
- Navigate to `/admin/signup`.
- Try to register an admin. Verify the frontend form properly restricts access until submission.
- Check Resend logs (or local logs if API is missing) to ensure the email content is correct.
- Verify that attempting to login before approval throws an "Account is inactive" error.
- Open the `/admin/approve?token=...` link and ensure the account gets activated successfully.
- Verify the newly activated admin can now log in correctly.
