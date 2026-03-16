# AUTHORA Launch Gate System

Final go/no-go system to prevent launch unless critical production conditions are met.

**Principle:** Do not launch with known blockers. Degraded-but-intentional modes (e.g. AI off, billing disabled) are acceptable if documented.

---

## 1. Launch Gate Checklist

All items must pass before launch. Mark each with initials and timestamp.

### Infrastructure & Reachability

| # | Check | Command / Action | ✓ |
|---|-------|------------------|---|
| 1 | Domain and SSL live | `curl -sI https://api.your-domain/health` → 200 over HTTPS | |
| 2 | Core app reachable | Web app loads at production URL; no cert warnings | |
| 3 | API reachable | `./scripts/healthcheck.sh https://api.your-domain` | |
| 4 | Health endpoints green | `curl -sf https://api.your-domain/health` → `{"status":"ok"}` | |
| 5 | Readiness green | `curl -sf https://api.your-domain/health/ready` → `{"status":"ready"}` | |

### Auth & Onboarding

| # | Check | Command / Action | ✓ |
|---|-------|------------------|---|
| 6 | Login working | Sign in with test account | |
| 7 | Signup working | Register new user | |
| 8 | Onboarding working | Complete setup wizard or skip flow | |
| 9 | First project creation | Create project, verify in dashboard | |

### Core Product

| # | Check | Command / Action | ✓ |
|---|-------|------------------|---|
| 10 | Editor / autosave | Create chapter, edit, refresh; content persists | |
| 11 | AI assist | Run AI action (or confirm degraded mode) | |
| 12 | Exports working | Export TXT/DOCX/EPUB; file downloads | |
| 13 | Billing | Checkout or confirm intentionally disabled | |

### Admin & Ops

| # | Check | Command / Action | ✓ |
|---|-------|------------------|---|
| 14 | Admin access | Admin user can reach `/dashboard/admin` | |
| 15 | Backup completed | `./scripts/backup.sh` runs successfully | |
| 16 | Restore validated | Restore from backup, verify app works | |
| 17 | Monitoring / logging | Log aggregation / alerting active | |
| 18 | Collaboration invites | Create invite, accept with second user | |
| 19 | Critical permissions | Beta reader cannot see author notes; client cannot see internal chatter | |

### Quality & Docs

| # | Check | Command / Action | ✓ |
|---|-------|------------------|---|
| 20 | No known blocker bugs | No P1/P2 open in tracker | |
| 21 | Launch docs complete | This doc + [RELEASE_GATES](RELEASE_GATES.md) + [INCIDENT_RESPONSE_RUNBOOK](INCIDENT_RESPONSE_RUNBOOK.md) reviewed | |

**Sign-off:** _________________ Date: _________

---

## 2. Launch Blocker List

**Do not launch if any of the following are true.**

| Blocker | Severity | Resolution |
|---------|----------|------------|
| Domain/SSL not live | P1 | Fix DNS, certs; verify HTTPS |
| API unreachable | P1 | Fix deployment, health checks |
| Login/signup broken | P1 | Fix auth; verify sessions |
| Onboarding broken | P1 | Fix setup wizard or skip path |
| Cannot create project | P1 | Fix project creation flow |
| Editor/autosave broken | P1 | Fix save path; verify DB writes |
| Exports broken | P1 | Fix export service |
| Admin inaccessible | P1 | Fix admin routes; bootstrap first admin |
| Backup fails | P1 | Fix backup script; verify restore |
| Restore not validated | P1 | Run restore drill; document steps |
| Monitoring inactive | P1 | Enable logging/alerting |
| Health endpoints failing | P1 | Fix DB/Redis; verify probes |
| Collaboration invites broken | P2 | Fix invite accept; verify expiry handling |
| Critical permission leak | P1 | Beta reader seeing notes; client seeing internal chatter |
| Known P1/P2 bug | P1/P2 | Fix or defer launch |
| SECRET_KEY default | P1 | `openssl rand -hex 32`; update .env |

**Acceptable degraded modes (document in launch notes):**

- AI assist off (no provider configured) – users informed
- Billing disabled – launch without payments
- API docs disabled in prod – security choice

---

## 3. Post-Launch First 24 Hours Checklist

| Time | Check | Action |
|------|-------|--------|
| **T+0** | Health | `./scripts/healthcheck.sh https://api.your-domain` |
| **T+0** | Login | Sign in; verify dashboard |
| **T+0** | Project | Create project; create book; create chapter |
| **T+0** | Autosave | Edit chapter; refresh; confirm content saved |
| **T+0** | Export | Export DOCX; verify download |
| **T+15m** | Logs | Check for 5xx; verify no SECRET_KEY warning |
| **T+15m** | Admin | Access admin panel; check system health |
| **T+1h** | Backup | Verify backup ran (cron or manual) |
| **T+1h** | AI | Test AI action (or confirm degraded) |
| **T+1h** | Billing | Test checkout (or confirm disabled) |
| **T+4h** | Error rate | Review logs; acceptable 4xx/5xx |
| **T+4h** | Latency | p95 acceptable |
| **T+24h** | Audit logs | Review for anomalies |
| **T+24h** | Restore drill | Optional: restore from backup, verify |

---

## 4. Rollback Decision Checklist

**Trigger rollback if any of the following are true.**

| Condition | Action |
|-----------|--------|
| Health checks fail repeatedly (3+ in 5 min) | Rollback |
| Login/signup completely broken | Rollback |
| Data corruption detected | Rollback immediately |
| Security incident (breach, credential leak) | Rollback + incident response |
| Critical auth bypass | Rollback |
| Export or save path broken for all users | Rollback |
| Database unreachable | Rollback (or fix infra first) |

**Consider fix-forward instead of rollback if:**

- Single feature broken; workaround exists
- Degraded but not critical (e.g. AI slow)
- Fix is small and low-risk
- Rollback would lose recent good data

**Rollback procedure:** See [INCIDENT_RESPONSE_RUNBOOK](INCIDENT_RESPONSE_RUNBOOK.md).

---

## 5. Operator Quick-Response Sheet

| Situation | Command / Action |
|-----------|------------------|
| **Health check** | `./scripts/healthcheck.sh https://api.your-domain` |
| **API down** | `docker compose logs api`; restart: `docker compose restart api` |
| **DB connection** | `curl -s https://api.your-domain/health/ready` → check `database` |
| **Redis connection** | Same; check `redis` in readiness |
| **Backup now** | `./scripts/backup.sh` |
| **Restore** | `./scripts/restore.sh ./backups/authora_YYYYMMDD_HHMMSS.dump` |
| **Rollback** | `./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod` |
| **First admin** | `./scripts/first-admin.sh --docker --prod` |
| **Validate env** | `source .env && ./scripts/validate-env.sh production` |
| **Go-live verify** | `./scripts/verify-go-live.sh https://api.your-domain https://your-domain` |
| **Migrations** | `./scripts/db-migrate.sh --docker --prod` |
| **Billing health** | `curl -H "Authorization: Bearer $ADMIN_TOKEN" https://api.your-domain/api/v1/billing/admin/health` |
| **AI health** | `curl -s https://api.your-domain/health/ai` |
| **Lock user** | Set `is_active=false` in `users` table |
| **Incident** | See [INCIDENT_RESPONSE_RUNBOOK](INCIDENT_RESPONSE_RUNBOOK.md) |

---

## Related Docs

- [RELEASE_GATES](RELEASE_GATES.md) – Pre-release gates (tests, migrations, etc.)
- [GO-LIVE-RECOMMENDATIONS](GO-LIVE-RECOMMENDATIONS.md) – Environment, secrets, observability
- [INCIDENT_RESPONSE_RUNBOOK](INCIDENT_RESPONSE_RUNBOOK.md) – Severity, rollback, triage
- [OPERATOR_COMMANDS](OPERATOR_COMMANDS.md) – Full command reference
