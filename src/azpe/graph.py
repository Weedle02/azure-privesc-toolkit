# (same GraphBuilder code as above)
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

import networkx as nx

try:
    import pydot  # noqa: F401
except Exception:
    pydot = None

NODE_TYPES = {"TENANT","SUBSCRIPTION","RESOURCE_GROUP","PRINCIPAL","APP","KEYVAULT","AUTOMATION_ACCOUNT","FUNCTION_APP","ROLE_DEFINITION"}
EDGE_TYPES = {"HAS_ROLE","OWNS_APP","CAN_ADD_CREDENTIAL","CAN_SET_POLICY","CAN_WRITE_RUNBOOK","CAN_DEPLOY_FUNCTION","MEMBER_OF","GRANTS_ROLE"}

from dataclasses import dataclass

@dataclass(frozen=True)
class Node:
    id: str
    type: str
    props: Dict[str, object]

@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    type: str
    props: Dict[str, object]

class GraphBuilder:
    def __init__(self, credential: object, tenant_id: str, subs: Iterable[str] | str = "all") -> None:
        self.credential = credential
        self.tenant_id = tenant_id
        self.subs = subs
        self.g = nx.DiGraph()
        self._nodes_by_id: Dict[str, str] = {}
        self._type_index: Dict[str, set[str]] = {t: set() for t in NODE_TYPES}

    def build(self) -> None:
        self._add_tenant()
        self._enumerate_subscriptions()
        self._enumerate_principals()
        self._enumerate_resources()
        self._enumerate_role_assignments()

    def save(self, path: str | Path) -> None:
        data = nx.node_link_data(self.g)
        Path(path).write_text(json.dumps(data, indent=2))

    def export_dot(self, path: str | Path) -> None:
        if pydot is None:
            raise RuntimeError("pydot/graphviz not available. Install 'pydot' and Graphviz.")
        nx.drawing.nx_pydot.write_dot(self.g, str(path))

    def add_node(self, node: Node) -> None:
        if node.type not in NODE_TYPES:
            raise ValueError(f"Unknown node type: {node.type}")
        if node.id in self._nodes_by_id:
            self.g.nodes[node.id].update(node.props)
            return
        self.g.add_node(node.id, type=node.type, **node.props)
        self._nodes_by_id[node.id] = node.id
        self._type_index[node.type].add(node.id)

    def add_edge(self, edge: Edge) -> None:
        if edge.type not in EDGE_TYPES:
            raise ValueError(f"Unknown edge type: {edge.type}")
        if edge.src not in self._nodes_by_id or edge.dst not in self._nodes_by_id:
            raise ValueError("Both src and dst nodes must exist before adding an edge.")
        self.g.add_edge(edge.src, edge.dst, type=edge.type, **edge.props)

    def _add_tenant(self) -> None:
        self.add_node(Node(id=f"tenant:{self.tenant_id}", type="TENANT", props={"name": self.tenant_id}))

    def _enumerate_subscriptions(self) -> None:
        sub_ids = ["00000000-0000-0000-0000-000000000000"] if self.subs == "all" else list(self.subs)  # type: ignore[arg-type]
        for sid in sub_ids:
            self.add_node(Node(id=f"sub:{sid}", type="SUBSCRIPTION", props={"name": sid}))
            self.add_edge(Edge(src=f"tenant:{self.tenant_id}", dst=f"sub:{sid}", type="MEMBER_OF", props={}))

    def _enumerate_principals(self) -> None:
        self.add_node(Node(id="user:alice@contoso.com", type="PRINCIPAL", props={"displayName": "Alice"}))
        self.add_node(Node(id="sp://apps/ContosoApp", type="PRINCIPAL", props={"displayName": "ContosoAppSP", "kind": "ServicePrincipal"}))

    def _enumerate_resources(self) -> None:
        kv_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.KeyVault/vaults/kv1"
        aa_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.Automation/automationAccounts/aa1"
        fn_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.Web/sites/fn1"
        self.add_node(Node(id=f"kv:{kv_id}", type="KEYVAULT", props={"name": "kv1"}))
        self.add_node(Node(id=f"aa:{aa_id}", type="AUTOMATION_ACCOUNT", props={"name": "aa1"}))
        self.add_node(Node(id=f"fn:{fn_id}", type="FUNCTION_APP", props={"name": "fn1"}))

    def _enumerate_role_assignments(self) -> None:
        self.add_edge(Edge(
            src="user:alice@contoso.com",
            dst="sub:00000000-0000-0000-0000-000000000000",
            type="HAS_ROLE",
            props={"roleName": "User Access Administrator", "scope": "subscription"}
        ))
        self.add_edge(Edge(
            src="sp://apps/ContosoApp",
            dst="kv:/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.KeyVault/vaults/kv1",
            type="CAN_SET_POLICY",
            props={}
        ))

    def stats(self) -> Dict[str, object]:
        return {
            "nodes": self.g.number_of_nodes(),
            "edges": self.g.number_of_edges(),
            "by_type": {t: len(ids) for t, ids in self._type_index.items()},
        }
