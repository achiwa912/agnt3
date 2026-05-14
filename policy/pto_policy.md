# Corporate PTO & Leave Policy (v2026.2)

**Internal Reference:** HR-COMP-2026
**Status:** Active
**Last Updated:** 2026-05-14

---

## 1. Introduction
This document outlines the mandatory Paid Time Off (PTO) and leave policies for all employees. To ensure regulatory compliance and operational continuity, all requests are processed via the **agnt3** autonomous system. 

**Note on HITL:** High-stakes actions (denials or policy overrides) require Human-in-the-loop (HITL) dashboard approval.

---

## 2. Core Policies

### POL-001: Standard Accrual Rate
- Employees accrue **1.67 days** of PTO per month.
- Maximum carry-over balance is **10 days** per calendar year. Any excess is forfeited on January 1st.

### POL-002: Blackout Periods
- No PTO may be taken during the **Q4 audit window** (December 1st – December 31st).
- Exceptions are VP approval required

### POL-003: "Mental Health Day" Spontaneity
- Employees are entitled to **2 "Spontaneous Wellness" days** per year.
- Notification must be sent via the agent at least **2 hours** before shift start.

### POL-004: Consecutive Day Limit
- Any single PTO request exceeding **10 consecutive business days** triggers a mandatory "Conflict of Interest" review and VP approval required.

### POL-005: Sick Leave Validation
- Sick leave exceeding **3 consecutive days** requires an official medical certificate.
- The agent will prompt for a file upload to the audit log.

### POL-006: Bereavement Protocol
- **5 days** of paid leave for immediate family.
- **1 day** for non-immediate family or close relations.

### POL-007: Work-from-Anywhere (WFA) "Work-ation"
- Employees may work remotely from a different country for up to **14 days** annually.
- Must maintain a minimum **4-hour overlap** with the Boston (EST) timezone.

### POL-008: Jury Duty & Civic Obligations
- Paid leave is granted for the duration of the service.
- Employees must return to work if released from duty for more than **4 hours** of their scheduled shift.

### POL-009: Paternity/Maternity Top-up
- 100% salary coverage for the first **12 weeks** of parental leave, inclusive of state benefits.

### POL-010: Emergency Sabbatical
- Unpaid leave of up to **3 months** for employees with **5+ years** of tenure.
- Requires a "Re-entry Plan" submitted 30 days prior to departure.

---

## 3. Compliance & Audit Trail (HOTL)
Every interaction with these policies by the AI Agent is logged with:
- **Timestamp:** UTC
- **Policy ID:** (e.g., POL-002)
- **Agent Reasoning:** Step-by-step logic provided by LLM model
- **HITL Status:** (APPROVED | DENIED | PENDING)
