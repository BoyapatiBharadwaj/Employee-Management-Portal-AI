AI-Powered Employee Management Portal

Project Overview

A web-based HR management system that centralizes employee information and HR operations while providing a role-aware AI assistant for employees, HR users, and administrators.

Objectives

Centralize employee and HR information.

Manage employees and departments.

Manage attendance, leave, payroll, and performance.

Support onboarding, offboarding, and employee documents.

Provide dashboards, reports, and analytics.

Provide an AI assistant for HR-related queries.

Enforce role-based access to employee information.

Deploy the system using Docker.

User Roles

Administrator

Organization-wide employee and HR management.

Broader database-aware AI queries.

Management of HR modules and reports.

HR

HR operations and employee-related management.

HR assistant functionality.

Employee

Personal employee portal.

Personal attendance, leave, payroll, performance, profile, and related information.

AI access restricted to the employee's own information.

Main Modules

Employee Management

Employees

Employee profiles

Departments

Employee documents

Onboarding

Offboarding

HR Operations

Attendance

Leave management

Payroll

Performance reviews

Reports

Dashboards and analytics

AI and Intelligent Features

AI Assistant

HR Assistant

Database-aware employee queries

Semantic Search

Resume Analyzer

Sentiment Analysis

Local LLM integration

System Architecture

                         Users
                  Admin / HR / Employee
                           |
                           v
                  React + Vite Frontend
                           |
                           | HTTP API
                           v
                    FastAPI Backend
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        HR Services     AI Service    Authentication
             |             |
             |             +------------------+
             |                                |
             v                                v
        PostgreSQL                         Ollama
             |                         TinyLlama Model
             |
             v
      Employee / HR Data

AI Request Flow

User
  |
  v
React AI Assistant
  |
  | POST /ai/chat
  v
FastAPI AI Router
  |
  +--> Authentication / Role Check
  |
  v
AIService
  |
  +--> Employee-specific database queries
  |
  +--> Domain-specific AI logic
  |
  +--> Local LLM when required
              |
              v
           Ollama
              |
              v
      TinyLlama:latest
              |
              v
        AI Response
              |
              v
          Frontend

The AI router authenticates the current user and applies employee access restrictions before passing requests to the AI service.

Employees can access only their own HR information through the AI interface. Administrative users can reach broader database-aware AI processing.

The LLM service uses Ollama with the tinyllama:latest model.

Technology Stack

Frontend

React 19

Vite

Bootstrap 5

React Bootstrap

Axios

Chart.js

React Router

Backend

Python

FastAPI

SQLAlchemy

Pydantic

Database

PostgreSQL 16

AI

Ollama

TinyLlama (tinyllama:latest)

Application-level AI/domain routing

Deployment

Docker

Docker Compose

Nginx

Database Models

The backend contains models for:

User

Employee

Department

Attendance

Leave

Payroll

Performance

Onboarding

Offboarding

Employee Document

Backend Structure

backend/
├── ai/
│   ├── ai_service.py
│   ├── llm_service.py
│   ├── attendance_ai.py
│   ├── leave_ai.py
│   ├── payroll_ai.py
│   ├── performance_ai.py
│   ├── profile_ai.py
│   ├── resume_ai.py
│   ├── semantic_search.py
│   └── sentiment_ai.py
│
├── models/
├── routers/
├── schemas/
└── services/

The backend follows a router/service/model structure, with separate AI components for domain-specific functionality.

Frontend Structure

frontend/src/
├── components/
├── pages/
└── services/

The frontend contains separate employee and administrative/HR pages and service modules for communicating with the backend.

Docker Deployment

The deployed application uses three primary containers:

employee-frontend
    React build served by Nginx
    Port: 5173 -> 80

employee-backend
    FastAPI / Uvicorn
    Port: 8000 -> 8000

employee-postgres
    PostgreSQL 16
    Port: 5432 -> 5432

Docker Compose manages the application services and PostgreSQL volume.

Security

Authentication is applied to AI requests.

User roles are checked before AI processing.

Employees are restricted from requesting other employees' confidential information.

Database-aware AI responses use application data rather than relying only on free-form LLM output.

The local LLM system prompt instructs the assistant not to invent company data.

Database credentials are kept in environment configuration rather than application code.

Current Project Status

Frontend: Working

FastAPI backend: Working

PostgreSQL: Working

Docker deployment: Working

AI Assistant: Working

Role-aware AI restrictions: Implemented

Employee-specific AI queries: Implemented

HR management modules: Implemented

Future Scope

Automated employee account provisioning when HR creates an employee.

Email-based onboarding and password setup.

Stronger authentication and session management.

Advanced RAG over HR policies and company documents.

More comprehensive analytics and dashboards.

Audit logging for sensitive HR and AI operations.

Production HTTPS and domain configuration.

Automated CI/CD deployment.

Architecture Summary

The system is designed as a modular HR platform rather than a standalone chatbot. The core application manages structured employee data through FastAPI and PostgreSQL, while the AI layer provides natural-language access to relevant HR information under role-based security controls.

The AI component combines application-level routing and database logic with a locally hosted Ollama/TinyLlama model, allowing the system to combine structured company data with natural-language assistance.

Handover and Setup Instructions

Prerequisites

The following software is required:

- Git
- Docker
- Docker Compose

For AI functionality, Ollama should be available on the host machine with the required model configured.

Clone the Repository

git clone https://github.com/chinthavishnupriya/Employee-Management-Portal-AI.git

cd Employee-Management-Portal-AI

Environment Configuration

Create a .env file in the project root.

Example:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your-password>
POSTGRES_DB=employee_management
OLLAMA_HOST=<your-ollama-host>

Do not commit the .env file to GitHub.

Run the Application with Docker

From the project root:

docker compose up -d --build

Check the running containers:

docker ps

The application consists of:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Backend API documentation: http://localhost:8000/docs
- PostgreSQL: port 5432

Stop the Application

docker compose down

Restart the Application

docker compose up -d

Project Handover

The project is structured into frontend, backend, database and AI components.

The frontend is built using React and communicates with the FastAPI backend through HTTP APIs.

The backend handles authentication, business logic, database operations and AI-related requests.

PostgreSQL stores employee and HR information.

The AI layer provides role-aware assistance using application data and the local Ollama/TinyLlama model.

A new team member should review the project architecture, README, backend routers and services, frontend pages and services, database models, and AI components before making changes.

Proposed Use Cases

1. AI Employee Performance Insights

The existing employee and performance modules can be extended with an AI feature that analyzes employee performance information and provides useful summaries and improvement suggestions.

This builds on the existing employee and performance functionality.

2. AI Leave and Attendance Analysis

The existing attendance and leave modules can be combined to provide AI-based analysis of attendance patterns, leave usage and related HR information.

This extends the existing attendance and leave functionality.

3. Payroll Insights

The existing employee and payroll modules can be extended to provide AI-assisted payroll summaries and insights using salary, bonus, allowances and deductions already stored in the system.

This builds directly on the existing payroll functionality.

4. Employee Retention and Risk Insights

Existing employee, attendance, leave and performance information can be combined to provide HR with insights about employees who may require additional attention or support.

This extends the existing HR data and analytics functionality rather than introducing an unrelated feature.


## Groq + Docker Deployment

The LLM integration now uses the Groq API rather than Ollama. The default model is `openai/gpt-oss-20b`, configurable through `GROQ_MODEL`. Groq's current documentation recommends GPT-OSS 20B as the replacement for the deprecated `llama-3.1-8b-instant` model; free-tier rate limits are account-specific.

1. Copy `.env.example` to `.env`.
2. Set `POSTGRES_PASSWORD`, `SECRET_KEY`, and `GROQ_API_KEY`.
3. Keep `GROQ_MODEL=openai/gpt-oss-20b` unless you need another currently supported model.
4. Run `docker compose up --build`.
5. Open the frontend at `http://localhost:5173` and the API at `http://localhost:8000`.

The backend Docker container runs the idempotent database upgrade before starting FastAPI. The monthly performance scheduler runs inside the backend process and checks the previous month hourly so completed evaluations are finalized, missing evaluations become `Pending Review`, and in-app reminders are generated for responsible Superiors.

## Employee Hierarchy & Monthly Performance

Implemented scope from the client requirements baseline:

- One active Superior per employee, controlled by Admin.
- Historical Superior assignments are retained.
- Current Superior appears on the employee dashboard and monthly performance view.
- Superior team view is restricted to direct reports.
- Monthly 1–100 evaluations are accepted from the 25th through month-end.
- Monthly performance combines Superior Rating 60%, Attendance 25%, and Leave 15%.
- Overall scores remain on a 1–100 scale and use competition ranking.
- Previous-month Performance Insights are available to Admin with department, Superior, employee, month, and rank filters through the API.
- Finalized records are read-only for Superiors/Employees; Admin corrections are audited.
- Audit records and in-app pending-review notifications are persisted in PostgreSQL.
