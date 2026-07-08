# Cloud-Based AI Python Code Generator and Live Preview Platform

**A Cloud-Native AI Platform for Automated Python Code Generation and Secure, Real-Time Execution**

*MCA Final Year Project — Specialization: Cloud Computing*

> This system is designed and engineered as a **Cloud-Native AI Platform**, built on modern cloud computing principles, clean/modular software architecture, and secure distributed-systems practices — not as a conventional "full-stack CRUD project." Every architectural decision below is made with **portability, scalability, and cloud-provider independence** as first-class goals.

---

## 1. Project Vision and Objectives

### 1.1 Problem Statement
Learning and prototyping in Python typically requires a local development environment (interpreter, IDE, dependency management), which creates friction for students, educators, and rapid prototypers. There is a need for a platform that can:
- Generate Python code from natural-language intent using AI.
- Execute that code safely, without exposing the host system to risk.
- Provide instant, live feedback (like a "preview") of program output.
- Do all of this in a way that is cloud-deployable, horizontally scalable, and portable across cloud vendors.

### 1.2 Project Objectives
| # | Objective | Cloud Computing Principle Demonstrated |
|---|-----------|------------------------------------------|
| 1 | AI-assisted Python code generation via Google Gemini | AI-as-a-Service integration, API-driven architecture |
| 2 | Secure, isolated code execution using Docker sandboxes | Containerization, workload isolation |
| 3 | Live preview of code execution results | Real-time cloud service orchestration |
| 4 | Storage Abstraction Layer (local disk / S3 / GCS interchangeable) | Cloud storage abstraction, vendor neutrality |
| 5 | Stateless, horizontally scalable backend | Elastic scalability, 12-factor app design |
| 6 | Modular, layered (Clean Architecture) codebase | Separation of concerns, maintainability |
| 7 | Containerized deployment via Docker Compose / Kubernetes | Cloud-native deployment, orchestration |
| 8 | CI/CD automated pipeline | DevOps automation |
| 9 | Documented migration path to AWS (ECS/EKS, S3, RDS, Lambda) | Multi-cloud readiness |
| 10 | Security-first backend (JWT auth, sandbox isolation, rate limiting) | Cloud security engineering |

### 1.3 Why This Qualifies as "Cloud Computing," Not Just "Web Development"
The distinguishing factors are explicitly engineered into the design, not just deployment details:
- **On-demand resource provisioning**: Each code execution request spins up an ephemeral, resource-capped container — a direct analogue of cloud elastic compute (like AWS Fargate/Lambda).
- **Storage abstraction**: The platform never talks to "the filesystem" directly — it talks to an interface that could be backed by local disk today and Amazon S3 / Google Cloud Storage tomorrow, with zero application code changes.
- **Statelessness**: The API layer keeps no session state in memory, enabling horizontal scaling behind a load balancer — a core cloud-native tenet.
- **Infrastructure as Code**: Deployment topology (containers, networks, scaling rules) is declared in versioned config (Docker Compose / Kubernetes manifests / Terraform stubs), not manually configured.
- **Managed AI service consumption**: Code generation is offloaded to Google Gemini (a managed cloud AI service) rather than a self-hosted model, mirroring real-world cloud architecture patterns (consume managed services, don't reinvent them).

---

## 2. High-Level System Architecture

```
                                   ┌───────────────────────────────┐
                                   │         Client Layer          │
                                   │  React/Next.js SPA (Browser)  │
                                   │  Monaco Editor + Live Preview │
                                   └───────────────┬───────────────┘
                                                   │ HTTPS / WSS (JWT)
                                                   ▼
                         ┌─────────────────────────────────────────────────┐
                         │              API Gateway / Ingress               │
                         │   (NGINX / Cloud Load Balancer — TLS, routing,   │
                         │        rate limiting, request validation)        │
                         └───────────────────────┬─────────────────────────┘
                                                  │
                     ┌────────────────────────────┼────────────────────────────┐
                     ▼                            ▼                            ▼
        ┌─────────────────────┐     ┌───────────────────────────┐   ┌─────────────────────┐
        │   Auth Service       │     │   Core Backend API        │   │  Execution Orchestr. │
        │  (FastAPI module)    │     │  (FastAPI - Clean Arch)   │   │  (Docker Executor)   │
        │  JWT issue/verify    │     │  Presentation → Use Cases │   │  Container lifecycle │
        │  User mgmt, RBAC     │     │  → Domain → Infra layers  │   │  Resource limits     │
        └──────────┬──────────┘     └──────────────┬────────────┘   └──────────┬───────────┘
                    │                               │                          │
                    ▼                               ▼                          ▼
        ┌─────────────────────┐     ┌───────────────────────────┐   ┌─────────────────────┐
        │   PostgreSQL         │     │   Google Gemini API        │   │  Ephemeral Docker    │
        │  (Users, Snippets,   │     │  (AI Code Generation /     │   │  Sandbox Containers  │
        │   Sessions, Audit)   │     │   Explanation / Fix-it)    │   │  (gVisor/seccomp,    │
        └─────────────────────┘     └───────────────────────────┘   │   no net, read-only) │
                    ▲                                                └──────────┬───────────┘
                    │                                                           │
                    │                         ┌─────────────────────────────────┘
                    │                         ▼
        ┌───────────┴─────────────────────────────────┐
        │        Storage Abstraction Layer (SAL)        │
        │  StorageService interface                     │
        │   ├── LocalDiskStorageAdapter  (Dev/On-Prem)  │
        │   ├── S3StorageAdapter          (AWS - future)│
        │   └── GCSStorageAdapter         (GCP - option) │
        └───────────────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────────────┐
        │   Redis (Cache, Rate Limiter, Job Queue,      │
        │           Pub/Sub for live logs streaming)     │
        └─────────────────────────────────────────────┘

        Cross-cutting: Prometheus + Grafana (metrics) · ELK / Loki (logs)
                        GitHub Actions CI/CD · Docker Registry
```

### 2.1 Architectural Style
The platform follows a **Modular Monolith with Clean Architecture boundaries**, deliberately chosen over microservices for an MCA project because:
- It keeps operational complexity appropriate for an academic/demo deployment.
- Internal module boundaries (Auth, Codegen, Execution, Storage) are strict enough that **any module can be extracted into an independent microservice later** without redesign — this is explicitly called out as a scalability growth path in Section 9.

### 2.2 Core Architectural Layers (Clean Architecture)

```
┌──────────────────────────────────────────────────────────┐
│  Presentation Layer      (FastAPI routers, Pydantic DTOs) │
├──────────────────────────────────────────────────────────┤
│  Application Layer       (Use Cases / Services)           │
│    - GenerateCodeUseCase                                  │
│    - ExecuteCodeUseCase                                   │
│    - SaveSnippetUseCase                                   │
│    - AuthenticateUserUseCase                               │
├──────────────────────────────────────────────────────────┤
│  Domain Layer            (Entities, Value Objects,        │
│                            Domain Interfaces / Ports)      │
│    - CodeSnippet, ExecutionResult, User, Session           │
│    - IStorageService, ICodeExecutor, IAIProvider (ports)   │
├──────────────────────────────────────────────────────────┤
│  Infrastructure Layer    (Adapters implementing ports)     │
│    - GeminiAIAdapter, DockerExecutorAdapter                │
│    - S3StorageAdapter, LocalStorageAdapter                 │
│    - PostgresRepository, RedisCacheAdapter                 │
└──────────────────────────────────────────────────────────┘
        Dependency Rule: dependencies point INWARD only.
        Domain layer has ZERO knowledge of FastAPI, Docker, or Gemini.
```

This ensures the **domain/business logic is fully testable in isolation** and that swapping Gemini for another LLM, or Docker for Firecracker microVMs, requires touching only the infrastructure layer.

---

## 3. Technology Stack

### 3.1 Frontend
| Component | Technology | Justification |
|---|---|---|
| Framework | React 18 + Next.js 14 (App Router) | SSR-capable, cloud-CDN friendly, fast iteration |
| Code Editor | Monaco Editor (VS Code engine) | Syntax highlighting, IntelliSense, industry-standard |
| Styling | Tailwind CSS + shadcn/ui | Consistent design tokens, accessible components |
| State Management | Zustand / React Query | Lightweight, server-state caching |
| Realtime | WebSocket client (native) | Streaming execution logs live |
| Auth | JWT stored in httpOnly cookies | XSS-resistant session handling |

### 3.2 Backend
| Component | Technology | Justification |
|---|---|---|
| API Framework | Python 3.12 + FastAPI | Async-first, OpenAPI auto-docs, high throughput |
| ORM | SQLAlchemy 2.0 (async) + Alembic | Migration-safe, type-safe DB access |
| Database | PostgreSQL 16 | ACID-compliant, JSONB support, cloud-managed options (RDS/Cloud SQL) |
| Cache / Queue | Redis 7 | Rate-limiting, pub/sub log streaming, Celery broker |
| Task Queue | Celery / Arq | Async execution job dispatch, decoupling API from execution latency |
| AI Provider | Google Gemini API (gemini-1.5-pro / gemini-2.0-flash) | Managed cloud AI service for code generation |
| Auth | OAuth2 + JWT (python-jose), bcrypt/argon2 password hashing | Industry-standard secure auth |

### 3.3 Execution Sandbox
| Component | Technology | Justification |
|---|---|---|
| Isolation | Docker (per-request ephemeral container) | Process/filesystem/network isolation |
| Hardened Runtime (optional upgrade) | gVisor (runsc) or Firecracker microVM | Kernel-level syscall sandboxing for defense-in-depth |
| Resource Limits | cgroups v2 (CPU, memory, PIDs) | Prevents fork-bombs / resource exhaustion |
| Base Image | python:3.12-slim (non-root user) | Minimal attack surface |

### 3.4 Storage
| Layer | Technology | Justification |
|---|---|---|
| Abstraction | Custom IStorageService interface | Vendor-neutral persistence |
| Dev/Default Adapter | Local filesystem (Docker volume) | Zero-cost local development |
| Cloud Adapter (future) | Amazon S3 (boto3) | Production-grade object storage, seamless AWS migration |
| Alt. Cloud Adapter | Google Cloud Storage | Multi-cloud demonstration |

### 3.5 DevOps & Infrastructure
| Component | Technology | Justification |
|---|---|---|
| Containerization | Docker + Docker Compose | Local & demo-environment parity |
| Orchestration (scale path) | Kubernetes (K3s for demo / EKS for AWS) | Production-grade orchestration |
| CI/CD | GitHub Actions | Automated build, test, lint, image push |
| IaC | Terraform (stubs for AWS provider) | Declarative infra, future migration |
| Monitoring | Prometheus + Grafana | Cloud-native observability |
| Logging | Loki / ELK stack | Centralized structured logs |
| Secrets Management | Docker secrets / .env (dev), AWS Secrets Manager (prod path) | Secure credential handling |
| Reverse Proxy / Gateway | NGINX / Traefik | TLS termination, routing, rate limiting |

### 3.6 Why Google Gemini (AI Layer)
Gemini is consumed as a managed external cloud AI service via REST/SDK - the platform treats it exactly like it would treat AWS Bedrock or Vertex AI in a production system: behind an adapter (GeminiAIAdapter) implementing the IAIProvider port, so switching to another LLM provider requires only a new adapter class.

---

## 4. Storage Abstraction Layer (SAL) — Design Detail

The Storage Abstraction Layer is one of the key architectural demonstrations of cloud portability. All modules depend only on the `IStorageService` **port**; concrete adapters are injected at startup based on environment configuration.

```python
# domain/ports/storage_service.py
from abc import ABC, abstractmethod

class IStorageService(ABC):
    @abstractmethod
    async def save(self, key: str, content: bytes, content_type: str) -> str:
        """Persist content, return a retrievable URI/reference."""

    @abstractmethod
    async def read(self, key: str) -> bytes:
        """Retrieve content by key."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove content by key."""

    @abstractmethod
    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Return a temporary shareable URL (local: signed app route; S3: presigned URL)."""
```

```python
# infrastructure/storage/local_storage_adapter.py
class LocalDiskStorageAdapter(IStorageService):
    def __init__(self, base_path: str):
        self.base_path = base_path
    # implements save/read/delete against the local filesystem/Docker volume

# infrastructure/storage/s3_storage_adapter.py
class S3StorageAdapter(IStorageService):
    def __init__(self, bucket: str, region: str):
        self.client = boto3.client("s3", region_name=region)
        self.bucket = bucket
    # implements save/read/delete/get_presigned_url against Amazon S3
```

```python
# infrastructure/storage/storage_factory.py
def get_storage_service(settings: Settings) -> IStorageService:
    if settings.STORAGE_BACKEND == "s3":
        return S3StorageAdapter(settings.S3_BUCKET, settings.AWS_REGION)
    if settings.STORAGE_BACKEND == "gcs":
        return GCSStorageAdapter(settings.GCS_BUCKET)
    return LocalDiskStorageAdapter(settings.LOCAL_STORAGE_PATH)
```

**Switching from local storage to AWS S3 in production requires changing only one environment variable** (`STORAGE_BACKEND=s3`) — no application code changes. This is the core proof-point for "Future AWS Migration Support."

---

## 5. AI Integration — Google Gemini Code Generation Flow

### 5.1 Request Flow
1. User submits a natural-language prompt (e.g., *"Write a function to check if a number is prime"*).
2. `GenerateCodeUseCase` builds a structured prompt (system instructions + user intent + output-format constraints).
3. `GeminiAIAdapter` calls the Gemini API (`generateContent`) requesting **strict JSON output**: `{ "code": "...", "explanation": "...", "imports": [...] }`.
4. Response is validated against a Pydantic schema (`GeneratedCodeResponse`) — malformed AI output is rejected/retried, never trusted blindly.
5. Generated code is returned to the frontend editor **and** optionally auto-queued for sandboxed execution.

### 5.2 Adapter Skeleton
```python
# infrastructure/ai/gemini_adapter.py
import google.generativeai as genai

class GeminiAIAdapter(IAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    async def generate_code(self, prompt: str) -> GeneratedCodeResponse:
        system_instructions = (
            "You are a Python code generation engine. Respond ONLY with valid JSON "
            "matching: {code: string, explanation: string, imports: string[]}. "
            "Do not include markdown fences or prose outside the JSON."
        )
        response = await self.model.generate_content_async(
            [system_instructions, prompt],
            generation_config={"response_mime_type": "application/json"},
        )
        return GeneratedCodeResponse.model_validate_json(response.text)
```

### 5.3 Prompt Safety
- All user prompts are sanitized and length-capped before being sent to Gemini.
- The system prompt explicitly forbids generation of destructive OS-level commands (`os.system`, `subprocess` calls to shell, `rm -rf`, network exfiltration code) — enforced both by the prompt instructions AND a static post-generation scan (Section 6.3) before the code is ever allowed to execute.
- Gemini responses are never executed as-is; they always pass through the same sandboxed executor and static-analysis gate as manually typed code.

---

## 6. Secure Docker-Based Code Execution

This is the most security-critical subsystem. Untrusted, AI-generated, or user-typed Python code must **never** run directly on the host or inside the API process.

### 6.1 Execution Pipeline
```
User/AI Code ─▶ Static Pre-Check ─▶ Job Queue (Redis/Celery) ─▶ Executor Worker
                                                                       │
                                                                       ▼
                                                   Spin up ephemeral Docker container
                                                   (python:3.12-slim, non-root, --network=none,
                                                    --read-only rootfs, --pids-limit=64,
                                                    --memory=128m, --cpus=0.5, timeout=10s)
                                                                       │
                                                                       ▼
                                                    Capture stdout/stderr, exit code
                                                                       │
                                                                       ▼
                                            Stream result back via WebSocket/pub-sub
                                                                       │
                                                                       ▼
                                                    Destroy container (always, even on crash)
```

### 6.2 Docker Hardening Configuration
```python
# infrastructure/execution/docker_executor.py
import docker

class DockerCodeExecutor(ICodeExecutor):
    def __init__(self):
        self.client = docker.from_env()

    async def execute(self, code: str, job_id: str) -> ExecutionResult:
        container = None
        try:
            container = self.client.containers.run(
                image="sandbox-python:3.12-slim",
                command=["python3", "-c", code],
                detach=True,
                network_disabled=True,          # No network access at all
                read_only=True,                 # Immutable root filesystem
                tmpfs={"/tmp": "size=16m,noexec"},
                mem_limit="128m",
                nano_cpus=int(0.5 * 1e9),        # 0.5 CPU core
                pids_limit=64,                   # Prevent fork bombs
                user="10001:10001",              # Non-root, unprivileged UID
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],                # Drop all Linux capabilities
                stdout=True, stderr=True,
            )
            exited = container.wait(timeout=10)  # Hard execution timeout
            logs = container.logs().decode("utf-8", errors="replace")
            return ExecutionResult(
                job_id=job_id,
                exit_code=exited["StatusCode"],
                output=logs[:20_000],            # Cap output size (anti-DoS)
            )
        except Exception as exc:
            return ExecutionResult(job_id=job_id, exit_code=-1, output=str(exc))
        finally:
            if container:
                container.remove(force=True)     # Always clean up, no orphaned containers
```

### 6.3 Defense-in-Depth Layers
| Layer | Control |
|---|---|
| 1. Input validation | Reject code exceeding size/line limits before queuing |
| 2. Static analysis (AST scan) | Block dangerous imports/calls: `os.system`, `subprocess`, `socket`, `eval`, `exec`, `ctypes`, `shutil.rmtree` unless explicitly allowed in a "sandboxed subset" |
| 3. Container isolation | `--network=none`, read-only FS, dropped capabilities, non-root UID |
| 4. Resource limits | CPU/memory/PID caps via cgroups, hard wall-clock timeout |
| 5. Output limits | Truncate stdout/stderr to prevent log-flooding DoS |
| 6. Ephemeral lifecycle | One container per execution; destroyed immediately after, no persistence between runs |
| 7. (Optional hardened mode) | Run containers under gVisor (`runsc`) runtime for syscall-level kernel isolation |
| 8. Auditing | Every execution request logged (user id, code hash, timestamp, result) for traceability |

### 6.4 Why Not Just `exec()` in Python?
Running arbitrary code with Python's built-in `exec()` inside the API process would give untrusted code full access to the host process memory, filesystem, and network — a catastrophic security failure. The Docker-per-execution model guarantees **process, filesystem, network, and resource isolation** consistent with how real cloud platforms (AWS Lambda, Google Cloud Run, Judge0, Repl.it) run untrusted workloads.

---

## 7. API Design (REST + WebSocket)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register new user | Public |
| POST | `/api/v1/auth/login` | Authenticate, issue JWT | Public |
| POST | `/api/v1/auth/refresh` | Refresh access token | Refresh token |
| POST | `/api/v1/codegen/generate` | Generate Python code from prompt (Gemini) | JWT |
| POST | `/api/v1/execute` | Submit code for sandboxed execution, returns job_id | JWT |
| GET | `/api/v1/execute/{job_id}` | Poll execution status/result | JWT |
| WS | `/ws/execute/{job_id}` | Live streaming of stdout/stderr as it's produced | JWT |
| GET | `/api/v1/snippets` | List saved snippets (paginated) | JWT |
| POST | `/api/v1/snippets` | Save a code snippet (persisted via SAL) | JWT |
| GET | `/api/v1/snippets/{id}` | Retrieve a snippet | JWT |
| DELETE | `/api/v1/snippets/{id}` | Delete a snippet | JWT |
| GET | `/api/v1/health` | Liveness/readiness probe (for orchestrator) | Public |
| GET | `/api/v1/metrics` | Prometheus metrics endpoint | Internal only |

All endpoints are documented automatically via FastAPI's OpenAPI/Swagger UI at `/docs`, satisfying professional API-documentation standards expected in a cloud engineering project.

---

## 8. Database Schema (PostgreSQL)

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'user',   -- 'user' | 'admin'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE code_snippets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    prompt          TEXT,                      -- original AI prompt, if AI-generated
    storage_key     TEXT NOT NULL,              -- reference into Storage Abstraction Layer
    language        VARCHAR(20) NOT NULL DEFAULT 'python',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE execution_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snippet_id      UUID REFERENCES code_snippets(id) ON DELETE SET NULL,
    code_hash       VARCHAR(64) NOT NULL,       -- SHA-256 of executed code, for audit
    exit_code       INTEGER,
    output_excerpt  TEXT,
    duration_ms     INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_snippets_user ON code_snippets(user_id);
CREATE INDEX idx_execlogs_user ON execution_logs(user_id);
```

---

## 9. Scalability & Cloud-Native Design

### 9.1 Statelessness
The API layer holds no in-memory session/user state. Every request carries its own JWT; horizontal replicas of the API container can be load-balanced without sticky sessions.

### 9.2 Horizontal Scaling Path
```
                     ┌─────────────────┐
                     │  Load Balancer   │
                     └────────┬─────────┘
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        API Replica 1   API Replica 2   API Replica N   (auto-scaled by CPU/RPS)
              │               │               │
              └───────────────┼───────────────┘
                               ▼
                    Shared PostgreSQL + Redis
                               │
                               ▼
                  Executor Worker Pool (auto-scaled
                  independently based on queue depth)
```
- **API tier** and **Execution tier** scale independently — a burst of code-generation requests does not starve execution capacity, and vice versa (classic cloud pattern: decouple compute-bound workloads from I/O-bound workloads via a queue).
- Kubernetes **Horizontal Pod Autoscaler (HPA)** can scale API pods on CPU/RPS and executor worker pods on Redis queue depth.

### 9.3 Modular-to-Microservices Growth Path
Because Clean Architecture already isolates modules behind ports, any module can become an independently deployable service without touching business logic:

| Current Module (in-monolith) | Future Standalone Microservice |
|---|---|
| Auth module | `auth-service` (own DB, issues JWTs for all services) |
| Codegen module | `codegen-service` (scales independently, GPU/quota-sensitive) |
| Execution orchestrator | `execution-service` (scales on container-runtime capacity) |
| Storage abstraction | Already vendor-neutral; can back a `storage-service` |

### 9.4 Resilience Patterns
- **Circuit breaker** around the Gemini API adapter (falls back to a queued retry / user-facing "AI temporarily unavailable" rather than cascading failure).
- **Idempotent execution jobs** keyed by `job_id`, safe to retry.
- **Graceful shutdown**: SIGTERM handling drains in-flight requests before container exit (Kubernetes-compatible).
- **Health/readiness probes** (`/api/v1/health`) so the orchestrator only routes traffic to ready pods.

---

## 10. Security Architecture (Summary)

| Threat | Mitigation |
|---|---|
| Arbitrary code execution / RCE on host | Docker sandbox, no host `exec()`, capability dropping, gVisor option |
| Credential theft | Argon2/bcrypt password hashing, JWT short-lived access + rotating refresh tokens |
| XSS | httpOnly, SameSite cookies for tokens; React auto-escaping; CSP headers |
| CSRF | SameSite=strict cookies + CSRF token on state-changing requests |
| SQL Injection | SQLAlchemy parameterized queries (ORM), no raw string interpolation |
| Brute-force login | Rate limiting (Redis token bucket) + exponential backoff + account lockout |
| DoS via large/slow code execution | Wall-clock timeouts, memory/CPU/PID caps, output truncation |
| Malicious dependency import in sandbox | No network access in sandbox container; whitelist-only stdlib subset |
| Secrets leakage | No secrets in code/images; env-injected at runtime, AWS Secrets Manager in prod path |
| Man-in-the-middle | TLS everywhere (HTTPS/WSS), HSTS headers |
| Privilege escalation in container | `no-new-privileges`, non-root UID, `cap_drop: ALL`, read-only rootfs |
| Injection via AI-generated code | AI output is never trusted — passes through the same static scan + sandbox as user code |

### 10.1 Authentication & Authorization Flow
```
Login ──▶ Verify credentials ──▶ Issue short-lived Access JWT (15 min)
                                  + Refresh Token (7 days, rotated, stored hashed in DB)
Every request ──▶ Verify JWT signature + expiry ──▶ Extract user_id, role
Role-based guard ──▶ e.g., admin-only routes check role claim
```

---

## 11. UI/UX Design

### 11.1 Design Principles
- **Developer-first, distraction-free workspace** — inspired by VS Code / Replit, but simplified for an academic audience.
- **Split-pane layout**: Prompt/Editor on the left, Live Preview/Output console on the right.
- **Immediate feedback loops**: Loading states, streaming output, clear error surfaces (never a silent failure).
- **Accessibility**: WCAG AA color contrast, full keyboard navigation, focus states on all interactive elements.
- **Dark-mode-first** aesthetic (developer tool convention) with a light-mode toggle.

### 11.2 Core Screens
1. **Landing / Auth Screen** — minimal, value-proposition-first, login/register.
2. **Workspace Screen** (primary screen):
   - Top bar: project title, run button, save button, user menu.
   - Left panel: natural-language prompt box + "Generate Code" action; below it, Monaco code editor (editable AI output).
   - Right panel: **Live Preview / Console** — streamed stdout/stderr, execution status badge (Queued → Running → Completed/Failed), execution time and resource usage.
   - Bottom drawer (collapsible): saved snippet history.
3. **Snippet Library Screen** — grid/list of saved snippets with search, tags, timestamps.
4. **Admin/Observability Screen** *(stretch goal)* — execution metrics, active users, system health (Grafana-embedded or custom dashboard).

### 11.3 Interaction Flow
```
[User types intent] → [Click "Generate"] → (loading shimmer on editor)
    → [AI-generated code streams into Monaco editor]
    → [User optionally edits code]
    → [Click "Run"] → (status: Queued → Running, spinner + live log stream)
    → [Console shows stdout/stderr in real time via WebSocket]
    → [Completed: green check + duration] or [Failed: red badge + error trace]
    → [Optional: Save Snippet → stored via Storage Abstraction Layer]
```

### 11.4 Visual Language
- **Typography**: Inter (UI text), JetBrains Mono (code/console).
- **Color system**: Neutral dark slate background, single accent color (electric blue or teal) for primary actions, semantic colors for status (green=success, amber=running, red=error).
- **Motion**: Subtle, purposeful transitions only (state changes, panel expand/collapse) — no decorative animation that could distract from the coding workflow.

---

## 12. Project / Folder Structure (Clean Architecture, Modular)

```
cloud-ai-python-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                        # FastAPI entrypoint
│   │   ├── core/
│   │   │   ├── config.py                  # Settings (pydantic-settings, env-driven)
│   │   │   ├── security.py                # JWT, password hashing
│   │   │   └── logging.py
│   │   ├── presentation/
│   │   │   ├── routers/
│   │   │   │   ├── auth_router.py
│   │   │   │   ├── codegen_router.py
│   │   │   │   ├── execution_router.py
│   │   │   │   └── snippet_router.py
│   │   │   └── schemas/                   # Pydantic request/response DTOs
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   │   ├── generate_code_use_case.py
│   │   │   │   ├── execute_code_use_case.py
│   │   │   │   ├── save_snippet_use_case.py
│   │   │   │   └── authenticate_user_use_case.py
│   │   ├── domain/
│   │   │   ├── entities/                  # User, CodeSnippet, ExecutionResult
│   │   │   └── ports/                     # IStorageService, ICodeExecutor, IAIProvider
│   │   └── infrastructure/
│   │       ├── ai/gemini_adapter.py
│   │       ├── execution/docker_executor.py
│   │       ├── storage/
│   │       │   ├── local_storage_adapter.py
│   │       │   ├── s3_storage_adapter.py
│   │       │   ├── gcs_storage_adapter.py
│   │       │   └── storage_factory.py
│   │       ├── db/
│   │       │   ├── models.py
│   │       │   └── repositories.py
│   │       └── cache/redis_adapter.py
│   ├── tests/
│   │   ├── unit/                          # Domain + use case tests (mocked ports)
│   │   ├── integration/                   # DB, Redis integration tests
│   │   └── e2e/                           # Full API flow tests
│   ├── sandbox_image/
│   │   └── Dockerfile                     # Hardened python:3.12-slim sandbox image
│   ├── Dockerfile                         # Backend service image
│   ├── requirements.txt
│   └── alembic/                           # DB migrations
├── frontend/
│   ├── app/                               # Next.js App Router pages
│   ├── components/
│   │   ├── editor/MonacoEditor.tsx
│   │   ├── console/LivePreview.tsx
│   │   └── ui/                            # shadcn/ui components
│   ├── lib/api-client.ts
│   ├── Dockerfile
│   └── package.json
├── infra/
│   ├── docker-compose.yml                 # Local/demo multi-service orchestration
│   ├── k8s/                               # Kubernetes manifests (Deployment, Service, HPA, Ingress)
│   └── terraform/                         # AWS provider stubs (VPC, ECS/EKS, RDS, S3)
├── .github/workflows/
│   ├── ci.yml                             # Lint, test, build on PR
│   └── cd.yml                             # Build & push images, deploy on merge to main
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   └── aws-migration-plan.md
└── README.md
```

---

## 13. Docker Compose (Local / Demo Deployment)

```yaml
version: "3.9"
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on: [backend]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://app:app@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379/0
      - STORAGE_BACKEND=local
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock   # required to spawn sandbox containers
      - storage_data:/app/storage
    depends_on: [postgres, redis]

  executor-worker:
    build: ./backend
    command: ["celery", "-A", "app.worker", "worker", "--loglevel=info"]
    environment:
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on: [redis, backend]

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=app
      - POSTGRES_DB=appdb
    volumes: ["pg_data:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine

volumes:
  pg_data:
  storage_data:
```

---

## 14. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [pull_request]
jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt --break-system-packages
      - run: ruff check backend/
      - run: pytest backend/tests/unit backend/tests/integration --cov=app
      - name: Build backend image
        run: docker build -t backend:ci ./backend
      - name: Build frontend
        run: |
          cd frontend && npm ci && npm run build
```

```yaml
# .github/workflows/cd.yml
name: CD
on:
  push:
    branches: [main]
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Log in to registry
        run: echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u "${{ secrets.REGISTRY_USER }}" --password-stdin
      - name: Build & push backend
        run: |
          docker build -t registry.example.com/ai-platform/backend:${{ github.sha }} ./backend
          docker push registry.example.com/ai-platform/backend:${{ github.sha }}
      - name: Deploy (kubectl apply / Terraform apply)
        run: echo "Deploy step - kubectl set image or terraform apply against target environment"
```

This pipeline demonstrates the standard cloud DevOps lifecycle: **lint → test → build → containerize → push → deploy**, entirely automated on every merge.

---

## 15. Future AWS Migration Plan

The system is designed so that migrating from the demo/on-prem deployment to AWS requires **configuration changes, not code rewrites**:

| Component (Current) | AWS Migration Target | Change Required |
|---|---|---|
| Docker Compose services | Amazon ECS (Fargate) or EKS | New Terraform module + task definitions; app code unchanged |
| Local disk storage | Amazon S3 | Set `STORAGE_BACKEND=s3` + IAM role; `S3StorageAdapter` already implemented |
| PostgreSQL container | Amazon RDS (PostgreSQL) | Update `DATABASE_URL`; no ORM changes |
| Redis container | Amazon ElastiCache (Redis) | Update `REDIS_URL` |
| NGINX reverse proxy | Application Load Balancer + AWS WAF | Terraform-managed ALB listener rules |
| Docker sandbox executor | AWS Fargate tasks (or Firecracker via AWS Lambda) for execution jobs | Executor adapter swapped for `FargateExecutorAdapter` implementing the same `ICodeExecutor` port |
| GitHub Actions CD | Same, deploying to ECS/EKS via `aws-actions/amazon-ecs-deploy-task-definition` | Add AWS credentials as GitHub secrets |
| Secrets (.env) | AWS Secrets Manager / Parameter Store | Inject via ECS task definition secrets block |
| Monitoring (Prometheus/Grafana) | Amazon CloudWatch / Managed Grafana | Add CloudWatch exporter; dashboards portable |

Because every external dependency (storage, executor, AI provider, database) sits behind a **port/interface**, this migration is a textbook demonstration of the **Ports & Adapters (Hexagonal) pattern** enabling multi-cloud portability — a key differentiator for a Cloud Computing specialization project.

---

## 16. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Code generation response < 3s (P95); execution result < 10s including sandbox cold start |
| Scalability | API tier scales horizontally to N replicas with no code change; execution workers scale on queue depth |
| Availability | Health/readiness probes enable zero-downtime rolling deployments |
| Security | All the controls in Section 10; no untrusted code ever runs outside a sandboxed container |
| Portability | Storage and AI provider are swappable via configuration, not code, per Sections 4 & 15 |
| Observability | Structured JSON logs, Prometheus metrics, distributed tracing hooks (OpenTelemetry-ready) |
| Maintainability | Clean Architecture layering enforces testable, decoupled modules |

---

## 17. Testing Strategy

| Test Type | Scope | Tooling |
|---|---|---|
| Unit tests | Domain entities, use cases (with mocked ports) | pytest, pytest-mock |
| Integration tests | Repository ↔ PostgreSQL, Redis cache, storage adapters | pytest + testcontainers |
| Contract tests | `IAIProvider`, `IStorageService`, `ICodeExecutor` adapter conformance | pytest fixtures per adapter |
| Security tests | Sandbox escape attempts, static-analysis bypass attempts, auth boundary tests | Custom pytest security suite |
| E2E tests | Full user flow: prompt → generate → execute → save | Playwright (frontend) + httpx (API) |
| Load tests | Concurrent execution job throughput | Locust / k6 |

---

## 18. Suggested MCA Project Timeline (14–16 Weeks)

| Phase | Weeks | Deliverable |
|---|---|---|
| 1. Requirements & Architecture Design | 1–2 | This design document, ERD, API contract |
| 2. Core Backend (Auth, Clean Architecture skeleton) | 3–4 | Auth module, DB migrations, base FastAPI app |
| 3. AI Integration (Gemini) | 5–6 | Codegen use case, adapter, prompt safety |
| 4. Secure Docker Execution Engine | 7–8 | Executor service, sandbox hardening, tests |
| 5. Storage Abstraction Layer | 9 | Local + S3 adapters, factory, tests |
| 6. Frontend Workspace UI | 10–11 | Editor, live preview, snippet library |
| 7. DevOps: Docker Compose, CI/CD, Monitoring | 12–13 | GitHub Actions, dashboards, logging |
| 8. Security Hardening & Load Testing | 14 | Pen-test checklist, Locust results |
| 9. Documentation & AWS Migration Plan | 15 | Final report, migration doc |
| 10. Final Demo & Viva Preparation | 16 | Presentation, live demo script |

---

## 19. Conclusion

This platform is engineered as a **Cloud-Native AI system**, not a conventional full-stack web app: every core decision — the storage abstraction, the stateless API tier, the ephemeral sandboxed execution model, the ports-and-adapters boundary around the AI provider, and the containerized/orchestrated deployment topology — exists specifically to demonstrate cloud computing principles: **elasticity, portability, isolation, and managed-service consumption**. The explicit AWS migration plan (Section 15) shows the system was designed cloud-first, with the current Docker/local deployment serving as a faithful, cost-free proxy for a production cloud environment, ready to be lifted onto AWS with configuration changes alone.
