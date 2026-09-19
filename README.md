# Synapse ERP | AI-Powered Enterprise Resource Planning

Synapse ERP is an end-to-end, multi-tenant Enterprise Resource Planning platform engineered to automate complex business workflows. By embedding autonomous LLM agents directly into the business logic, Synapse bridges the gap between unstructured data and strict relational database constraints, enabling seamless operations from raw customer inquiries to finalized PDF invoices.

## System Architecture & Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React, Vite, Tailwind CSS |
| **Backend** | Python, FastAPI, SQLAlchemy, Alembic |
| **Database** | PostgreSQL |
| **AI Integration** | Google Gemini API (`gemini-3.6-flash`), Custom ReAct Agent Architecture |
| **Document Pipeline** | WeasyPrint, Jinja2 (HTML to PDF) |

## Core Capabilities

### 1. Multi-Tenant Role Isolation (RBAC)
The platform features strict role-based access control across five distinct operational dashboards:
*   **Sales:** Manages customer relationships and handles unstructured order ingestion.
*   **Manager:** Approves/rejects orders and monitors team KPI metrics.
*   **Warehouse:** Manages inventory allocation and order fulfillment.
*   **Accountant:** Handles invoice generation, payment processing, and receipt documentation.
*   **Owner:** Accesses high-level business intelligence and revenue analytics.

### 2. Agentic AI Workflows
Rather than treating AI as a conversational bolt-on, Synapse integrates LLMs as functional system actors:
*   **Order Extraction Agent:** Parses unstructured emails or text messages into strictly validated Pydantic schemas, mapping requested items to database SKUs.
*   **Inventory & Financial Analysts:** ReAct-based agents that execute explicit, parameterized tool calls to PostgreSQL to retrieve real-time stock levels and revenue forecasts.
*   **Automated Rejection Drafter:** Autonomously generates context-aware, polite email drafts when managers reject orders due to business rule violations.

### 3. Deterministic AI Security (`ToolGuard`)
To mitigate LLM hallucination and prevent unauthorized data access, all agentic tool calls are routed through a custom `ToolGuard` middleware. This layer intercepts database requests, ensuring the AI operates strictly within safe, read-only analytical bounds.

### 4. Automated Document Pipeline
Generates pixel-perfect, dynamic PDF invoices and payment receipts. The system utilizes Jinja2 to inject live database models into HTML templates, which are subsequently rendered into PDFs on the fly via WeasyPrint.

---

## Local Environment Setup

### Prerequisites
*   Python 3.12+
*   Node.js 18+
*   PostgreSQL running locally or via Docker

### Backend Installation

1. Navigate to the backend directory and set up the virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
