# ADR 0002: Proof Verification Architecture

## Status
Accepted

## Context
The application requires users to provide proof of task/challenge completion. Proofs can be self-attestation, photos, videos, documents, peer verification, or sensor data.

## Decision
### Proof Types (MVP)
1. **SELF** - Simple self-confirmation (checkbox)
2. **PHOTO** - Image upload with metadata
3. **PEER** - Requires N approvals from designated peers

### Proof Storage
- Files stored in S3-compatible storage with user-isolated paths
- Signed URLs for secure access (expiring)
- Server-side MIME type validation
- Size limits enforced (configurable, default 10MB for images, 100MB for videos)

### Proof Workflow
1. User submits proof attached to a Contribution
2. Proof status: `pending` → `approved` / `rejected`
3. For PEER proofs: N approvals required (configurable per challenge)
4. ProofReview records each approval/rejection with reviewer info

### Later Phases
- VIDEO proof (Phase 2)
- SENSOR integration via OAuth (Phase 3)
- AI-assisted verification hints (Phase 4)

## Rationale
- Start simple with SELF/PHOTO/PEER
- Peer verification provides social accountability without complexity of AI
- Isolated storage prevents cross-user access vulnerabilities

## Consequences
- Need to implement file upload validation middleware
- Peer verification requires notification system
- Storage costs scale with user engagement
