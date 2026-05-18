# DevFlow — Event-Driven Microservices Platform

[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-blue?logo=github-actions)](https://github.com/DevFlow/ci)
[![Docker](https://img.shields.io/badge/Docker-Passing-success?logo=docker)](https://hub.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)

## What Is DevFlow?

DevFlow is an advanced, fully containerized event-driven microservices platform. It simulates a modern web ecosystem where various independent domains (Users, Orders, Notifications, Analytics) collaborate asynchronously. This platform solves the challenge of tight coupling in monolithic applications by leveraging a robust Pub/Sub mechanism, ensuring that services remain fully independent and scalable.

What makes DevFlow interesting is its implementation of real-time monitoring and resilient architecture patterns. It ships with a fully operational Circuit Breaker pattern, dynamic Nginx Rate Limiting, real-time WebSocket event streaming, and comprehensive observability via Prometheus and Grafana, providing a production-ready template for scalable backend architectures.

## Architecture

```text
  React Dashboard (Vite :3000)
       ↓
  Nginx (API Gateway :8080)
  ↙    ↓    ↘         ↘
User  Order Notif  Analytics  EventBus
 ↓      ↓     ↓        ↓          ↓
PG1   PG2   PG3       PG4       Redis
              ↑_________________________|
              (all services pub/sub to Redis)
```

## Event Flow

When a `POST /api/users` request is called:
1. **API Gateway**: Nginx receives the request, applies rate limits, and proxies it to `user-service`.
2. **User Service**: Validates the payload and saves the new User to its dedicated Postgres database (`postgres-users`).
3. **Event Publishing**: `user-service` publishes a `user.created` event to the Redis Pub/Sub broker.
4. **Analytics Service**: The background subscriber task in `analytics-service` picks up the event and logs it to `postgres-analytics`.
5. **EventBus Service**: The `eventbus` WebSocket server intercepts the event and streams it live to the React Dashboard.

## Services Reference

| Service | Port | Database | Publishes | Subscribes |
|---------|------|----------|-----------|------------|
| user-service | 8001 | postgres-users | `user.created` | None |
| order-service | 8002 | postgres-orders | `order.created` | None |
| notification-service | 8003 | postgres-notifications | None | `user.created`, `order.created` |
| analytics-service | 8004 | postgres-analytics | None | `*` (All events) |
| eventbus | 8005 | None | None | `*` (All events) |

## Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| Frontend | React 18 + Vite | Modern, blazing-fast dashboard UI. |
| Backend | Python 3.11, FastAPI | High-performance async API development. |
| Database | PostgreSQL 15 | Isolated persistent storage per microservice. |
| Messaging | Redis 7 | High-throughput Pub/Sub message broker. |
| Gateway | Nginx | Reverse proxy, rate limiting, and routing. |
| Monitoring | Prometheus, Grafana | Metrics scraping, instrumentation, and visualization. |
| DevOps | Docker, Docker Compose, GitHub Actions | Container orchestration and automated CI/CD pipeline. |

## Quick Start

**Prerequisites:** Docker and Docker Compose installed.

1. Clone the repository and navigate to the project root.
2. Build and start the platform:
   ```bash
   docker-compose up --build -d
   ```
3. Access the dashboard: [http://localhost:8080](http://localhost:8080)

## Monitoring

DevFlow includes enterprise-grade observability out of the box:
- **Prometheus**: Available at [http://localhost:9090](http://localhost:9090). It automatically scrapes the `/metrics` endpoints of all FastAPI services.
- **Grafana**: Available at [http://localhost:3001](http://localhost:3001) (Login: `admin` / `devflow123`). Contains pre-configured dashboards visualizing HTTP Requests per Second, Request Duration p99, Error Rates, and Active WebSockets.

## API Reference

**User Service:**
- `POST /api/users`: Create a user. `{"name": "Alice", "email": "alice@test.com"}`
- `GET /api/users`: List all users.
- `GET /api/users/{id}`: Get a specific user by ID.
- `POST /api/users/simulate-failure`: Cause the next 5 requests to fail (triggers circuit breaker).

**Order Service:**
- `POST /api/orders`: Create an order. `{"user_id": 1, "product": "Laptop", "amount": 999.99}`
- `GET /api/orders`: List all orders.

**Notification & Analytics:**
- `GET /api/notifications`: Retrieve notification logs.
- `GET /api/analytics/summary`: View aggregated events and metrics.

**WebSockets:**
- `WS ws://localhost:8080/ws`: Connect to the live event stream.

## Architecture Decisions

- **Separate PostgreSQL per service**: Enforces true bounded contexts. Services cannot perform complex JOINs across domains, preventing "distributed monolith" anti-patterns.
- **Redis pub/sub**: Chosen over direct HTTP calls to decouple event producers from consumers, significantly improving fault tolerance and latency.
- **Nginx gateway**: Centralizes cross-cutting concerns like Rate Limiting, routing, and CORS, abstracting backend complexity from the frontend.
- **Conditional Map-Based Rate Limiting**: In production environments, standard `limit_except` rate-limiting nesting in Nginx location blocks is prohibited. We solved this by mapping `$request_method` dynamically (only tracking `POST` operations under custom keys) to target write operations specifically while maintaining maximum speed for standard query/read operations.
- **FastAPI**: Provides native `asyncio` support and automatic OpenAPI documentation, making it the fastest and most developer-friendly framework for Python microservices.
- **Circuit Breaker pattern**: Ensures that cascading failures are stopped. If `user-service` goes down, `order-service` degrades gracefully instead of hanging and crashing.

## CI/CD Pipeline

```text
Lint ───> Test ───> Docker Build ───> Integration Test
```
- **Lint**: Runs `flake8` to enforce PEP-8 code quality standards.
- **Test**: Spins up ephemeral Postgres and Redis containers, installs `pytest`, and runs unit tests for all microservices, uploading coverage artifacts.
- **Docker Build**: Validates that all Dockerfiles compile successfully using `docker-compose build`.
- **Integration Test**: Boots the entire 12-container stack, runs API health checks, and simulates an end-to-end user creation flow.

## What I Learned

- Designing and orchestrating a multi-container environment efficiently using `docker-compose` networks and `depends_on` healthchecks.
- Implementing the Circuit Breaker pattern from scratch to handle transient failures in distributed systems.
- Utilizing Nginx `limit_req_zone` blocks to apply targeted API rate-limiting against denial-of-service attacks.
- Exporting, scraping, and visualizing system metrics in real-time using the Prometheus and Grafana stack.
- The nuances of Python `asyncio` background tasks and the importance of holding strong references to prevent premature garbage collection.
