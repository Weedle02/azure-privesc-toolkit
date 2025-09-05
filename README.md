# Azure Privilege Escalation Toolkit (azpe)

**azpe** is a red-team / blue-team tool for mapping and simulating privilege escalation paths in Azure AD and Azure resources.  
It builds an attack graph from identities, role assignments, and resources, then finds concrete escalation chains with remediation and detection guidance.

(Please) Use only on tenants and subscriptions you own or are authorized to test.  
This project is for research and defense improvement.

---

## Features (MVP)

- Enumerates tenants, subscriptions, principals, and selected resources.
- Builds an attack graph (`graph.json`, `.dot` export for Graphviz).
- Detects common Azure privilege escalation chains:
  - User Access Administrator → self-assign role
  - Privileged Role Administrator → Global Administrator
  - App Owner → add credential → impersonate SP
  - Automation Account / Runbook write → escalate via Managed Identity
  - Key Vault policy → steal app creds
- Outputs explainers + JSON + KQL queries for detections.

---

## Install

Clone and install in a virtual environment:

```bash
git clone https://github.com/<your-username>/azure-privesc-toolkit.git
cd azure-privesc-toolkit
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

