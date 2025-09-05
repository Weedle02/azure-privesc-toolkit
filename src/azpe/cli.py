from __future__ import annotations
import typer
from rich import print
from pathlib import Path
from .graph import GraphBuilder

app = typer.Typer(no_args_is_help=True)

@app.command()
def enum(
    tenant: str = typer.Option(..., help="Tenant ID"),
    subs: str = typer.Option("all", help="'all' or comma-separated list of subscription IDs"),
    out: str = typer.Option("graph.json"),
    dot: str = typer.Option(None),
):
    gb = GraphBuilder(credential=None, tenant_id=tenant, subs=subs.split(",") if subs != "all" else "all")
    gb.build()
    gb.save(out)
    if dot:
        gb.export_dot(dot)
    print(f"[bold green]+[/bold green] Graph saved to {out}{' and ' + dot if dot else ''}")
    print(gb.stats())

if __name__ == "__main__":
    app()
