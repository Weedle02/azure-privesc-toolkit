from .engine import Rule, EdgeQuery

#Concept
CHAINS = [
    Rule(
      name="User Access Admin -> Self Assign",
      preconditions=[EdgeQuery("HAS_ROLE", role="User Access Administrator")],
      produce=["CAN_GRANT_ANY_ROLE"],
      impact="High",
      remediation="Remove UAA at high scopes or move to PIM eligible; restrict to least-privilege."
    ),
    # add PRA->GA, App Owner->AddCred, AA->MSI, KV->Secrets...
]
