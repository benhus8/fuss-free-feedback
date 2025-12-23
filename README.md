# fuss-free-feedback

## 🏗 Project Architecture

The project follows **Clean Architecture** (also known as Hexagonal Architecture) principles to ensure separation of concerns, scalability, and testability. The code is organized into concentric layers, with the **Domain** being the core dependency.

```text
├── domain/                  # The Core (Pure Python, No Frameworks)
│   ├── models/              # Aggregate Roots & Entities (e.g., Inbox, Message)
│   ├── repositories/        # Abstract Interfaces (Ports) for repositories
│   ├── services/            # Domain Services (Business logic spanning multiple entities)
│   └── vo/                  # Value Objects (Immutable domain objects)
│
├── application/             # Application Layer (Use Cases)
│   ├── commands/            # Write operations (e.g., CreateInbox, ReplyToInbox)
│   ├── queries/             # Read operations (e.g., GetInbox)
│   └── services/            # Application Services (Orchestrators)
│
├── infrastructure/          # Adapters & Implementation Details
│   ├── database/            # SQLModel/SQLAlchemy models & DB setup
│   ├── repositories/        # Implementation of Domain Repositories (Adapters)
│   └── extern/              # External services (e.g., Email, 3rd party APIs)
│
├── interface/               # Entry Points (The "Driving" Adapters)
│   ├── api/                 # FastAPI Endpoints (Controllers)
│   ├── schemas/             # Pydantic Models (DTOs - Input/Output validation)
│   └── dependencies/        # Dependency Injection definitions
│
├── exceptions.py            # Global exception handling & definitions
└── main.py                  # Application entry point & configuration