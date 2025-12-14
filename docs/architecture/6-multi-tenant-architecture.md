# 6. Multi-Tenant Architecture

## 6.1 Data Isolation

**Tenant Context Extraction:**
```python
# Every request includes tenant_id (derived from user's subscription)
async def get_current_user(token: str) -> User:
    payload = verify_jwt(token)
    user_id = payload["sub"]
    
    # User is the tenant (MVP)
    # Later: User belongs to Tenant → Multi-user tenant (Phase 2)
    tenant_id = user_id
    
    return User(id=user_id, tenant_id=tenant_id)
```

**Query-Level Isolation:**
```python
# Every query includes tenant filter
async def get_translation(job_id: str, tenant_id: str):
    return await db.query(Translation).filter(
        Translation.job_id == job_id,
        Translation.tenant_id == tenant_id  # CRITICAL
    ).first()
```

**Storage-Level Isolation:**
```
S3 Structure:
s3://transkeep-bucket/
  ├─ uploads/
  │  ├─ {tenant_id}/
  │  │  ├─ {job_id}/
  │  │  │  └─ original.pdf
  ├─ translations/
  │  ├─ {tenant_id}/
  │  │  ├─ {job_id}/
  │  │  │  └─ translated.pdf
```

## 6.2 Multi-Tenant Roadmap

**MVP (User = Tenant):**
- One user account = One tenant
- Simple, secure, fast to build

**Phase 2 (Organization Tenants):**
- Team creates organization
- Multiple users share glossary, settings
- Role-based access (owner, editor, viewer)
- Shared billing

---
