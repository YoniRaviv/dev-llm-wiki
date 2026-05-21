# Topic Seeds

Starter topic vocabularies organized by stack and project kind. The `init-vault` skill consults this file in Step 6 to propose a starter `wiki/topics.md` based on the user's stack and project-kind answers.

The lists are intentionally short — 10-15 topics per bucket. The vocabulary should grow organically as the user ingests sources; this is just the seed. Aim for fewer, higher-quality topics over more.

## Composition rule

When seeding, take:
- 5-7 topics from the user's **stack** bucket
- 3-5 topics from the user's **project-kind** bucket
- 3-5 from the **cross-cutting** bucket
- Cap at 20 total to keep the initial vocabulary tight

If a topic appears in two buckets (e.g., `postgres` shows up in multiple stacks), include it once.

## By stack

### TypeScript-React
- typescript
- react
- next-js
- node
- tailwind
- shadcn-ui
- postgres
- prisma
- tanstack-query
- vite
- esm-cjs
- vercel-deployment

### Python-ML
- python
- pytorch
- pandas
- jupyter
- llm
- prompt-engineering
- rag
- embeddings
- vector-db
- fastapi
- pydantic
- huggingface

### Go
- go
- grpc
- postgres
- redis
- kubernetes
- docker
- prometheus
- protobuf
- testify
- gin-fiber

### Rust
- rust
- tokio
- axum
- serde
- sqlx
- postgres
- wasm
- cargo
- traits-generics
- error-handling-rust

### Ruby-Rails
- ruby
- rails
- active-record
- sidekiq
- postgres
- redis
- rspec
- hotwire-turbo
- stimulus

### Java-Kotlin
- java
- kotlin
- spring-boot
- gradle
- postgres
- kafka
- jvm-tuning
- mockito
- testcontainers

## By project kind

### SaaS products
- auth
- billing
- multi-tenancy
- onboarding
- analytics
- email-delivery
- webhooks
- rate-limiting

### Libraries-tools
- api-design
- versioning
- breaking-changes
- documentation
- ci-cd
- package-distribution

### Internal-business apps
- internal-tooling
- access-control
- audit-logging
- reporting
- data-export
- admin-ui

### Research-POCs
- experimentation
- prototyping
- benchmark
- baseline-vs-novel
- ablation
- reproducibility

### Mixed
Pull from the most relevant stack and project-kind buckets; if uncertain, ask the user which kind of project they want the seed weighted toward.

## Cross-cutting (always relevant)

- testing
- observability
- deployment
- error-handling
- performance
- security
- caching
- async-state
