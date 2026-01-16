# ADR 0001: Project Stack Decision

## Status
Accepted

## Context
CommitQuest needs a robust, secure, and maintainable technology stack for building a commitment-based ToDo application with proof verification, team challenges, and rewards.

## Decision
We will use the following stack:

### Backend
- **Django 5.x** with Django REST Framework for API
- **PostgreSQL** as primary database
- **Redis + Celery** for caching and async tasks
- **JWT (SimpleJWT)** for authentication with short-lived tokens

### Frontend
- **React 19** with TypeScript
- **Material-UI** for component library (Apple-like customization)
- **React Router v7** for routing
- **React Hook Form** for form handling

### Infrastructure
- **Docker & Docker Compose** for development
- **GitHub Actions** for CI/CD
- **S3-compatible storage** for file uploads

## Rationale
1. **Django + DRF**: Mature ecosystem, strong security defaults, excellent ORM for complex relationships
2. **PostgreSQL**: ACID compliance, JSON support, excellent for relational data with complex queries
3. **React + TypeScript**: Type safety, component reusability, large ecosystem
4. **JWT**: Stateless auth, mobile-friendly, but with short expiry for security

## Consequences
- Team must be familiar with Python/Django and TypeScript/React
- JWT requires careful token lifecycle management
- PostgreSQL requires managed service or self-hosted maintenance
