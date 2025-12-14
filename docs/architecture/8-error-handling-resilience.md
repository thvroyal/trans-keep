# 8. Error Handling & Resilience

## 8.1 Error Categories & Responses

| Error | HTTP Status | User Message | Action |
|-------|-------------|--------------|--------|
| Invalid file format | 400 | "Please upload a PDF file" | Retry with valid file |
| File too large | 413 | "File exceeds 100MB limit" | Split file |
| Unauthorized (no token) | 401 | "Please sign in" | Redirect to login |
| Quota exceeded | 429 | "You've used your free documents" | Upgrade subscription |
| Processing failed | 500 | "Translation failed. Retry?" | Retry from upload |
| Download expired | 410 | "Download link expired" | Re-upload to translate again |
| Network timeout | 504 | "Server busy. Please try again" | Retry (transparent to user) |

## 8.2 Retry Logic (Client & Server)

**Client-side (Exponential Backoff):**
```typescript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fetch(url, options)
    } catch (error) {
      const delay = Math.pow(2, attempt) * 1000 // 1s, 2s, 4s
      if (attempt < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay))
      } else {
        throw error
      }
    }
  }
}
```

**Server-side (Celery Task Retry):**
```python
@celery_app.task(bind=True, max_retries=3)
def extract_translate(self, job_id):
    try:
        # Process
    except Exception as exc:
        # Exponential backoff: 60s, 120s, 300s
        self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)
```

## 8.3 Graceful Degradation

**If DeepL API Down:**
- Fall back to Google Translate API (lower quality)
- Notify user: "Using backup translation service (lower quality)"
- Alert ops team

**If Claude API Down (Tone):**
- Skip tone customization
- Deliver base translation only
- Notify user: "Tone customization temporarily unavailable"

**If S3 Down:**
- Buffer in Redis
- Retry periodically (every 30s for 24 hours)
- Alert ops team

---
