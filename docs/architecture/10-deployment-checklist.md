# 10. Deployment Checklist

## Pre-Launch

- [ ] Database migrations tested (Alembic)
- [ ] Environment variables configured (Secrets Manager)
- [ ] API endpoints load-tested (200+ concurrent users)
- [ ] Celery workers tested (process 500-page PDFs)
- [ ] OAuth flow tested (sign-in, sign-out, token refresh)
- [ ] S3 permissions configured (least privilege)
- [ ] CloudFront cache settings correct
- [ ] SSL certificate installed & valid
- [ ] DNS records pointing to ALB
- [ ] Error pages (404, 500) deployed
- [ ] Monitoring alerts configured
- [ ] Backup strategy documented (RDS automated backups)
- [ ] Disaster recovery plan (what if RDS fails?)

## Launch Day

- [ ] Start ECS services (1 frontend task, 2 backend tasks, 2 workers)
- [ ] Verify health checks passing
- [ ] Monitor logs for errors (first 30 min)
- [ ] Test download functionality manually
- [ ] Send announcement to beta testers
- [ ] Stand by for support (first 2 hours)
- [ ] Auto-scaling tested (trigger high load)

---
