# AUTHORA Post-Deploy Validation Checklist

Run immediately after production deployment.

---

## Immediate (0–15 min)

- [ ] GET /health returns 200
- [ ] GET /health/ready returns 200
- [ ] Frontend loads at production URL
- [ ] Login works
- [ ] Register works
- [ ] Dashboard loads for authenticated user
- [ ] No 5xx in logs

## Short-Term (15–60 min)

- [ ] Create project
- [ ] Create book
- [ ] Create chapter
- [ ] Edit and save
- [ ] Export (TXT/DOCX/EPUB)
- [ ] Admin panel accessible (admin user)
- [ ] Audit logs recording

## Monitoring (First 24h)

- [ ] Error rate acceptable
- [ ] Latency p95 acceptable
- [ ] No memory leaks (process stable)
- [ ] Cron jobs complete (if scheduled)
- [ ] Backup completed

## Sign-Off

- [ ] All critical paths verified
- [ ] No blocking issues
- [ ] Support ready for tickets
