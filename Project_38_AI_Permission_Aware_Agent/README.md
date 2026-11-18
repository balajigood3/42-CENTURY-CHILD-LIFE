# Project 38 — AI Permission-Aware Agent

A small agent orchestration demo that enforces role-based access control (RBAC), permission scopes, and explicit approval before high-impact tools.

## Features
- Four roles: viewer, analyst, operator, admin
- Scope-based authorization checked before each tool call
- Human approval gate for draft creation and user administration
- Audit record for allow/approval-required decisions
- Tool permission visibility in Streamlit
- Safe local mock tools; no external services or paid API keys

## Architecture
`User + Role → Principal/Scopes → Policy Engine → Approval Gate → Mock Tool → Audit Record`

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

## Add a tool safely
1. Add a fixed tool name and required scope in `TOOL_POLICIES`.
2. Implement a bounded function in `_execute_demo_tool`.
3. Enforce authorization through `run_agent` before execution.
4. Add tests for permitted, denied, and approval-required cases.

## Security limitations
- This is an educational in-memory demo, not production identity management.
- Role assignments are selected in the UI and are not authenticated; production systems must derive principals from a trusted identity provider.
- Approval is a demo checkbox, not a cryptographically verified approval workflow.
- Mock tools do not access files, networks, shells, or real accounts.
- Production deployments need server-side authorization at every tool boundary, durable tamper-resistant audit logs, tenant isolation, and revocable credentials.
