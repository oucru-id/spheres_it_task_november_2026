# Task 2: Design Answer Key

## 1. Exactly-Once Delivery

**Strong:** Client-generated UUID per record. Server stores seen UUIDs and returns `duplicate` on re-send. Batch-level idempotency by `batch_id`. Acknowledges that "exactly once" is really "at least once + idempotent processing." Mentions the ack problem: device crashes after server processes but before receiving the response.

**Acceptable:** Client UUID + server dedup. May not distinguish batch vs record idempotency. Mentions retry safety.

**Weak:** "Use a message queue" without explaining dedup. Assumes the network is reliable. No concrete mechanism.

**Red flags:** Auto-increment IDs from the server (requires connectivity). Relying on timestamps for ordering. "Use Kafka" without explaining consumer idempotency.

## 2. Duplicate Patients

**Strong:** Accept both, flag for human review. Explains why auto-merge by name similarity is dangerous (different people with similar names exist). Proposes a review queue with enough context for a clerk to decide. Acknowledges placeholder NIK as a special case.

**Acceptable:** Flag and queue. May propose fuzzy matching with a threshold but acknowledges false positives.

**Weak:** Auto-merge by name similarity. No human review step.

**Red flags:** Auto-merge by name similarity ("use Levenshtein distance > 0.8 to merge"). Blocking sync until a human reviews. Assuming NIK is always unique and reliable.

## 3. Stock Conflicts

**Strong:** Always allow dispensing. Clinics cannot refuse medicine because of a data sync issue. Record the dispensing, let stock go negative, flag for reconciliation. Physical stock count resolves the discrepancy. Separates "logical stock" (server) from "physical stock" (shelf).

**Acceptable:** Allow dispensing with negative stock warning. Mentions reconciliation.

**Weak:** Reject dispensing when stock is insufficient. Queue dispensing until sync resolves.

**Red flags:** "Reject the dispensing and tell the health worker to sync first." "Use a distributed lock on stock." Designing a reservation system for a 2-month MVP.

## 4. Wrong Device Clock

**Strong:** Server-assigned `received_at` for ordering. `device_recorded_at` stored for audit but never used for business logic. May flag records with implausible timestamps for review. Explains that NTP sync on low-end phones is unreliable.

**Acceptable:** Server timestamp for ordering. Stores device time as metadata.

**Weak:** Trust the device clock. "Require NTP sync before allowing data entry."

**Red flags:** Ordering records by `device_recorded_at`. Rejecting records with old timestamps.

## 5. Lost Device

**Strong:** Addresses data leakage (PII on device), recovery (unsynced records are lost unless device had encrypted backup). Proposes: on-device encryption at rest, remote wipe capability, server tracks last sync per device so clinic knows what's missing. Acknowledges the tradeoff: encryption adds complexity on 2 GB RAM phones.

**Acceptable:** Mentions encryption and "those records are lost." Remote wipe.

**Weak:** "Back up to cloud continuously" (contradicts offline-first).

**Red flags:** No mention of PII risk. "Just re-enter the data" without addressing the security angle.

## 6. Schema Migration

**Strong:** Version the local schema. Records carry `schema_version`. Server accepts old versions with best-effort parsing, rejects unknown future versions. App stores data in old schema until sync completes, then migrates locally. Mentions the hazard: app update happens mid-batch.

**Acceptable:** Schema version on records. Server handles old versions.

**Weak:** "Force update the app before syncing." No versioning strategy.

**Red flags:** Assume all devices update simultaneously. "Drop unsynced records and re-download."

## 7. MVP Scope

**Strong:** Names specific things to cut: conflict resolution UI (use a simple list), real-time sync (batch is enough), push notifications, offline analytics, multi-tenancy. Explains why each is deferred. Identifies what IS needed: idempotent sync, patient dedup flagging, stock tracking.

**Acceptable:** Reasonable list of deferrals with brief reasoning.

**Weak:** "Build everything" or a vague list like "optimize later."

**Red flags:** CRDTs for a 2-month MVP. Event sourcing. Building a custom sync protocol instead of using HTTP. Designing for 10,000 devices when there are 40 clinics.
