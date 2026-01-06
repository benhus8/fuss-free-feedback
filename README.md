
# Fuss-Free Feedback API
A privacy-focused, stateless anonymous feedback platform built with Python & FastAPI.

Fuss-Free Feedback is a modern take on anonymous messaging systems (like NGL or Tellonym), designed with privacy and simplicity in mind. Unlike traditional platforms, it requires no registration, no email, and no persistent user accounts.

Instead of a database of users, the system relies on Tripcodes—a cryptographic hash mechanism popularized by imageboards. This allows users to establish a consistent identity and manage their inboxes using only a username and a secret phrase, without ever storing sensitive personal data on the server.

### Key Features
- Zero Registration: Users can create an inbox instantly. No "Sign Up" flow, no email verification.

- Tripcode Identity: Authentication is stateless. Your Username + Secret generates a unique Signature (Tripcode) that proves ownership.

- Privacy First: Messages can be anonymous or signed. The server stores only what is necessary.


### How It Works
1. Create: You choose a Topic (e.g., "AMA about Python"), a Username, and a Secret.

2. Share: You get a public link (e.g., /inboxes/uuid) to share with others.

3. Receive: People visit the link and send anonymous (or signed) messages.

4. Read: You use your Secret to authenticate and read the replies. Only the holder of the Secret can decrypt the permission to view the inbox.

## 🏗 Project Architecture

This project follows Clean Architecture principles. The primary goal was to decouple the core business logic from the delivery mechanism (FastAPI) and the persistence layer (SQLModel/PostgreSQL).

By enforcing strict separation of concerns, the application becomes:

- Framework Agnostic: The core logic doesn't know it's running inside FastAPI.

- Database Independent: The domain models are pure Python objects, separate from database tables.

- Highly Testable: Business rules can be tested in isolation without spinning up a database or HTTP server.

```text
src/
├── domain/                  # Core (Pure Python)
│   ├── models/              # Entities/Aggregates (Inbox, Message)
│   ├── repositories/        # Repository interfaces (ports)
│   └── exceptions.py        # Domain exceptions
│
├── application/             # Application Layer (Use Cases orchestration)
│   ├── services/            # Application Services (e.g., InboxService)
│   └── utils/               # Utility functions (e.g., generate_tripcode)
│
├── infrastructure/          # Adapters & implementations
│   ├── database/            # DB setup & SQLModel/SQLAlchemy models
│   │   └── models/          # InboxDB, MessageDB
│   ├── repositories/        # SQLAlchemy repository implementations
│   └── mappers/             # DB <-> Domain mappers (InboxMapper, MessageMapper)
│
├── interface/               # Entry points (Driving adapters)
│   ├── api/                 # FastAPI endpoints (controllers)
│   ├── schemas/             # Pydantic DTOs
│   └── dependencies/        # DI definitions (e.g., get_service)
│
└── main.py                  # Application entry point & configuration
```

## Key Architectural Decisions
Domain Isolation: The domain layer has zero dependencies on external frameworks. It defines what the application is, not how it stores data.

Dependency Inversion: The application layer depends on repository interfaces (abstract classes), not concrete implementations. The infrastructure layer injects the real database logic at runtime.

Data Mapping: We use explicit Mappers to convert between Domain Entities (used for logic) and SQLModel classes (used for the database). This prevents database constraints from leaking into business rules.


## 🔐 API Authorization Strategy

This project implements a pragmatic, hybrid authorization model tailored for a "stateless" tripcode system. We distinguish between creating/signing content (where credentials are part of the payload) and accessing/managing resources (where credentials act as session keys via headers).

| Method  | Endpoint                            | Auth Source | Role    | Description |
| :------ | :---------------------------------- | :---------- | :------ | :---------- |
| `POST`  | `/inboxes`                          | **Body**    | Creator | Credentials in payload generate the owner signature and create the resource. |
| `GET`   | `/inboxes/{inbox_id}`               | **None**    | Guest   | Shows public inbox metadata so anyone can reply. No messages included. |
| `POST`  | `/inboxes/{inbox_id}/messages`      | **Body**    | Author  | Credentials optional; when provided they sign the message (tripcode). |
| `GET`   | `/inboxes`                          | **Headers** | Owner   | Lists inboxes for the authenticated owner (pagination: `page`, `page_size`). |
| `GET`   | `/inboxes/{inbox_id}/messages`      | **Headers** | Owner   | Reads messages for the inbox (pagination: `page`, `page_size`). |
| `PATCH` | `/inboxes/{inbox_id}/topic`         | **Headers** | Owner   | Changes the inbox topic (owner-only). |

### Headers Specification
For endpoints requiring Headers auth (Owner role), use:
- `X-username`: Your username
- `X-secret`: Your secret password


## Run tests
uv run pytest -q tests/integration