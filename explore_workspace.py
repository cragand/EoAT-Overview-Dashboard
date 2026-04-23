"""Explore Asana workspace structure: portfolios, projects, custom fields."""
import json
from asana_client import api_get


def main():
    # Get current user and workspace
    me = api_get("users/me")
    print(f"Authenticated as: {me['name']} ({me['email']})")
    workspaces = me.get("workspaces", [])
    print(f"\nWorkspaces ({len(workspaces)}):")
    for ws in workspaces:
        print(f"  - {ws['name']} (gid: {ws['gid']})")

    if not workspaces:
        return

    # Use first workspace (or the only one)
    ws_gid = workspaces[0]["gid"]
    print(f"\nExploring workspace: {workspaces[0]['name']}")

    # List portfolios
    print("\n--- PORTFOLIOS ---")
    portfolios = api_get("portfolios", {
        "workspace": ws_gid, "owner": me["gid"],
        "opt_fields": "name"
    })
    if not portfolios:
        # Try without owner filter
        print("(No portfolios owned by you; listing all accessible...)")
        portfolios = api_get("portfolios", {
            "workspace": ws_gid,
            "opt_fields": "name"
        })
    for p in portfolios:
        print(f"\n  Portfolio: {p['name']} (gid: {p['gid']})")
        # List items (projects) in portfolio
        items = api_get(f"portfolios/{p['gid']}/items", {
            "opt_fields": "name,custom_fields.name,custom_fields.display_value"
        })
        for item in items[:5]:  # Show first 5
            print(f"    Project: {item['name']} (gid: {item['gid']})")
            for cf in item.get("custom_fields", []):
                print(f"      {cf['name']}: {cf.get('display_value', 'N/A')}")
        if len(items) > 5:
            print(f"    ... and {len(items) - 5} more projects")

    # List standalone projects
    print("\n--- PROJECTS (first 10) ---")
    projects = api_get("projects", {
        "workspace": ws_gid,
        "opt_fields": "name,num_tasks",
        "limit": 10,
    })
    for proj in projects:
        print(f"  {proj['name']} (gid: {proj['gid']}, tasks: {proj.get('num_tasks', '?')})")

    # For each project, show custom fields
    print("\n--- PROJECT CUSTOM FIELDS (first 3 projects) ---")
    for proj in projects[:3]:
        print(f"\n  {proj['name']}:")
        try:
            detail = api_get(f"projects/{proj['gid']}", {
                "opt_fields": "custom_field_settings.custom_field.name,custom_field_settings.custom_field.type"
            })
            for cfs in detail.get("custom_field_settings", []):
                cf = cfs.get("custom_field", {})
                print(f"    {cf.get('name')} ({cf.get('type')})")
        except Exception as e:
            print(f"    Error: {e}")


if __name__ == "__main__":
    main()
