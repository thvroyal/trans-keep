# 7. Security & Compliance

## 7.1 Authentication & Authorization

**Google OAuth Flow:**
```
1. User clicks "Sign in with Google"
2. Frontend redirects to Google OAuth consent screen
3. User approves → Google redirects to backend with code
4. Backend exchanges code for ID token
5. Backend verifies token signature (Google public key)
6. Backend creates user in DB if first time
7. Backend generates JWT token
8. Frontend stores JWT in localStorage (or httpOnly cookie)
9. All API requests include Authorization header
```

**JWT Token:**
```
Header: {alg: "HS256", typ: "JWT"}
Payload: {sub: "user_id", tenant_id, exp: now + 7days, iat: now}
Signature: HMAC(header.payload, SECRET_KEY)
```

**Token Refresh:**
- Token expires in 7 days
- Frontend detects expired token (401 response)
- Redirects to re-authenticate with Google
- No refresh token (for simplicity)

## 7.2 Data Security

**In Transit:**
- All connections HTTPS/TLS
- Certificate from AWS Certificate Manager
- Enforced by ALB (no unencrypted traffic)

**At Rest:**
- PostgreSQL: Encrypted by RDS
- S3: Encrypted with AWS KMS
- Redis: Encrypted by ElastiCache

**File Handling:**
- PDF uploads: Virus scan via AWS Macie (Phase 2)
- Temp files: Deleted after 24 hours
- No permanent document storage (except user downloads)

## 7.3 Privacy & GDPR

**Data Retention:**
- User's original PDF: Deleted after 1 hour (MVP), 24 hours (Phase 2)
- Translation result: Available for 24 hours for download
- Permanent storage: Only if user requests saved project (Phase 2)

**User Data Export:**
- Endpoint: GET /api/v1/export (export all user's data)
- Format: JSON with metadata, no raw PDFs (too large)

**Right to Delete:**
- Endpoint: DELETE /api/v1/user/delete-account
- Cascades: Delete user, all translations, all files
- Processed asynchronously (via Celery job)

---
