# Story 4.1: Production Deployment

**Story Key:** 4-1-production-deployment  
**Epic:** 4 - Launch Prep & Beta  
**Week:** Week 4 (Dec 23-27)  
**Duration:** 1 day  
**Owner:** DevOps / Backend Developer  
**Status:** backlog  

---

## Overview

Deploy TransKeep to AWS production. Frontend on CloudFront + S3, backend on ECS, database on RDS, cache on ElastiCache, and observability on CloudWatch.

---

## Acceptance Criteria

### AC 4.1.1: Backend on AWS ECS ✅
- [ ] Docker image pushed to ECR
- [ ] ECS service running
- [ ] Load balancer configured
- [ ] Auto-scaling rules set
- [ ] Health checks working

### AC 4.1.2: Frontend on CloudFront + S3 ✅
- [ ] Frontend build deployed to S3
- [ ] CloudFront distribution created
- [ ] Cache invalidation working
- [ ] SSL/TLS configured
- [ ] Edge locations optimized

### AC 4.1.3: Database & Cache ✅
- [ ] RDS PostgreSQL instance created
- [ ] ElastiCache Redis cluster created
- [ ] Security groups configured
- [ ] Backups automated
- [ ] Monitoring enabled

### AC 4.1.4: Observability ✅
- [ ] OpenTelemetry sends to CloudWatch
- [ ] Logs aggregated
- [ ] Metrics visible in dashboards
- [ ] Alarms set for errors
- [ ] Log retention configured

### AC 4.1.5: Domain & SSL ✅
- [ ] Domain name purchased
- [ ] DNS records configured
- [ ] SSL certificate from AWS ACM
- [ ] HTTPS enforced
- [ ] Redirect HTTP → HTTPS

---

## Tasks & Subtasks

### Task 1: Prepare AWS Infrastructure
- [ ] Set up VPC and subnets
- [ ] Configure security groups
- [ ] Create RDS instance
- [ ] Create ElastiCache cluster
- [ ] Test connectivity

**Estimated Time:** 2 hours

### Task 2: Deploy Backend to ECS
- [ ] Create ECR repository
- [ ] Build and push Docker image
- [ ] Create ECS task definition
- [ ] Create ECS service
- [ ] Configure load balancer
- [ ] Test health checks

**Estimated Time:** 2 hours

### Task 3: Deploy Frontend to CloudFront
- [ ] Build React app for production
- [ ] Create S3 bucket
- [ ] Upload build artifacts
- [ ] Create CloudFront distribution
- [ ] Configure cache behaviors
- [ ] Test CDN

**Estimated Time:** 1.5 hours

### Task 4: Set Up OpenTelemetry Exporter
- [ ] Configure Otel to send to CloudWatch
- [ ] Create CloudWatch log groups
- [ ] Create dashboards for key metrics
- [ ] Set up alarms
- [ ] Test logging

**Estimated Time:** 1.5 hours

### Task 5: Configure Domain & SSL
- [ ] Purchase domain
- [ ] Create Route 53 hosted zone
- [ ] Request ACM certificate
- [ ] Configure DNS records
- [ ] Enable HTTPS enforcement
- [ ] Test SSL

**Estimated Time:** 1 hour

### Task 6: Final Integration Testing
- [ ] Test complete flow: upload → translate → download
- [ ] Test on production URLs
- [ ] Load testing (100+ concurrent users)
- [ ] Failover testing
- [ ] Backup verification

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- Use Infrastructure as Code (CloudFormation or Terraform) for reproducibility
- Set up proper secret management (AWS Secrets Manager)
- Configure WAF for DDoS protection
- Set up CloudTrail for audit logging
- Multi-AZ deployment for high availability

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  
