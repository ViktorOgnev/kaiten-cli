"""Explicit-profile access lifecycle with a private recovery journal.

KAITEN_LIVE=1 KAITEN_ACCESS_LIVE_PROFILE=<profile>
KAITEN_ACCESS_LIVE_DOMAIN=<expected-domain> pytest -m live ...
No pre-existing user's company permissions or pre-existing entities are changed.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
import uuid
from pathlib import Path

import pytest
from click.testing import CliRunner

from kaiten_cli.app import cli
from kaiten_cli.profiles import resolve_profile
from kaiten_cli.registry import resolve_tool
from kaiten_cli.registry.access_management import TOOLS
from kaiten_cli.runtime.client import KaitenClient


class AccessCampaign:
    def __init__(self, root: Path, profile: str):
        self.root = root
        self.profile = profile
        self.prefix = f"codex-access-live-{uuid.uuid4().hex[:10]}"
        self.runner = CliRunner()
        self.cleanup = []
        self.covered = set()
        self.results = []
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if (root / "cleanup.json").exists():
            assert json.loads((root / "cleanup.json").read_text()) == [], (
                "Resolve pending cleanup before another run"
            )
        for name in ("manifest.jsonl", "cleanup.json", "report.json"):
            (root / name).touch(mode=0o600)
        self.save_cleanup()

    def probe(self):
        result = self.runner.invoke(
            cli,
            [
                "--locale",
                "ru",
                "--json",
                "--profile",
                self.profile,
                "--read-only",
                "--trace-file",
                str(self.root / "trace.jsonl"),
                "profile",
                "probe",
            ],
        )
        assert json.loads(result.output)["success"], "Read-only profile probe failed"

    def save_cleanup(self):
        (self.root / "cleanup.json").write_text(json.dumps(self.cleanup, ensure_ascii=False))

    def journal(self, name, inputs, status):
        record = {"canonical_name": name, "input": inputs, "status": status}
        record["operation_id"] = hashlib.sha256(
            json.dumps([name, inputs], sort_keys=True).encode()
        ).hexdigest()
        with (self.root / "manifest.jsonl").open("a") as output:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")

    def invoke(self, name, inputs=None, *, allow_error=False):
        inputs = inputs or {}
        tool = resolve_tool(name)
        if tool.is_mutation:
            self.journal(name, inputs, "pending")
        args = [
            "--locale",
            "ru",
            "--json",
            "--profile",
            self.profile,
            "--trace-file",
            str(self.root / "trace.jsonl"),
            "--stdin-json",
        ]
        if not tool.is_mutation:
            args.append("--read-only")
        result = self.runner.invoke(cli, [*args, *tool.command_segments], input=json.dumps(inputs))
        payload = json.loads(result.output)
        success = payload.get("success") is True
        self.results.append(
            {
                "command": name,
                "success": success,
                "status": payload.get("error", {}).get("status_code"),
                "error": payload.get("error"),
                "http_requests": payload.get("stats", {}).get("http_request_count"),
            }
        )
        if success:
            self.covered.add(name)
        if tool.is_mutation:
            self.journal(name, inputs, "applied" if success else "failed")
        self.save_report()
        print(
            f"{name}: {'ok' if success else payload.get('error', {}).get('status_code', 'error')}",
            flush=True,
        )
        time.sleep(0.5)
        if not success and not allow_error:
            raise AssertionError(f"{name}: {payload.get('error')}")
        return payload.get("data") if success else payload

    def verify(self, condition, label):
        self.journal("postcondition", {"check": label}, "verified" if condition else "failed")
        assert condition, label

    def register(
        self, delete_name, delete_input, verify_name, verify_input, *, restore=None, kind=None
    ):
        self.cleanup.append(
            {
                "delete": delete_name,
                "input": delete_input,
                "verify": verify_name,
                "verify_input": verify_input,
                "restore": restore,
                "kind": kind,
            }
        )
        self.save_cleanup()

    def save_report(self, cleanup_errors=None):
        (self.root / "report.json").write_text(
            json.dumps(
                {
                    "prefix": self.prefix,
                    "covered": sorted(self.covered),
                    "calls": self.results,
                    "cleanup_pending": len(self.cleanup),
                    "cleanup_errors": cleanup_errors or [],
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    def teardown(self):
        errors = []
        for item in reversed(list(self.cleanup)):
            try:
                if item["restore"]:
                    self.invoke(item["restore"][0], item["restore"][1])
                response = self.invoke(item["delete"], item["input"], allow_error=True)
                if isinstance(response, dict) and response.get("success") is False:
                    assert response.get("error", {}).get("status_code") == 404
                if item["kind"] == "virtual":
                    for _ in range(20):
                        rows = self.invoke(
                            "company-users.list",
                            {"query": self.prefix, "limit": 100, "only_virtual": True},
                        )
                        rows = (
                            rows
                            if isinstance(rows, list)
                            else rows.get("records", rows.get("users", []))
                        )
                        if not any(
                            row.get("id", row.get("user_id")) == item["input"]["user_id"]
                            for row in rows
                        ):
                            break
                        time.sleep(1)
                    else:
                        raise AssertionError("Virtual user deletion did not complete")
                elif item["kind"] == "role":
                    rows = self.invoke("roles.list")
                    self.verify(
                        not any(row["id"] == item["input"]["role_id"] for row in rows),
                        "temporary role absent from role list",
                    )
                elif item["kind"] in ("space", "story"):
                    rows = self.invoke(
                        "admin-tree-entities.list",
                        {
                            "query": str(
                                item["input"].get("space_id", item["input"].get("map_id"))
                            ),
                            "entity_types": "space" if item["kind"] == "space" else "story_map",
                            "limit": 100,
                        },
                    )
                    self.verify(
                        not any(
                            row.get("id")
                            == item["input"].get("space_id", item["input"].get("map_id"))
                            for row in rows
                        ),
                        "temporary space absent from administrative tree",
                    )
                else:
                    absent = self.invoke(item["verify"], item["verify_input"], allow_error=True)
                    self.verify(
                        isinstance(absent, dict)
                        and absent.get("error", {}).get("status_code") == 404,
                        f"{item['delete']} removed its temporary object",
                    )
                self.cleanup.remove(item)
                self.save_cleanup()
            except Exception as exc:
                errors.append(f"{item['delete']}: {exc}")
        self.save_report(errors)
        assert not errors, "Cleanup failed: " + "; ".join(errors)


def _user(rows, user_id):
    return next((row for row in rows if row.get("user_id", row.get("id")) == user_id), None)


@pytest.mark.live
@pytest.mark.timeout(900)
def test_access_management_live(tmp_path, socket_enabled):
    if os.environ.get("KAITEN_LIVE", "").lower() not in ("1", "true"):
        pytest.skip("Set KAITEN_LIVE=1|true")
    profile_name = os.environ.get("KAITEN_ACCESS_LIVE_PROFILE")
    expected_domain = os.environ.get("KAITEN_ACCESS_LIVE_DOMAIN")
    if not profile_name or not expected_domain:
        pytest.skip("Select an explicit access-test profile and expected domain")
    profile = resolve_profile(profile_name)
    assert profile.domain == expected_domain, "Profile domain does not match the authorized target"
    root = Path(os.environ.get("KAITEN_ACCESS_LIVE_DIR", str(tmp_path / "access-live")))
    assert (
        not (root / "cleanup.json").exists()
        or json.loads((root / "cleanup.json").read_text()) == []
    ), "Resolve pending cleanup before another run"
    h = AccessCampaign(root, profile_name)
    print(f"Access campaign journal: {root}", flush=True)
    h.probe()
    try:
        actor = h.invoke("users.current")
        actor_id = actor["id"]
        members = h.invoke(
            "company-users.list", {"access_type_permissions": "member", "limit": 100}
        )
        members = (
            members
            if isinstance(members, list)
            else members.get("records", members.get("users", []))
        )
        target = next(
            (
                row
                for row in members
                if row.get("id", row.get("user_id")) != actor_id
                and not row.get("virtual")
                and not row.get("temporarily_inactive")
                and row.get("apps_permissions", 0) & 1
            ),
            None,
        )
        assert target is not None, (
            "A second existing paid test-company member is needed; no external invitations are sent"
        )
        target_id = target.get("id", target.get("user_id"))
        roles = h.invoke("roles.list")
        reader = next(row for row in roles if row["id"] == "06ccb31f-426b-4fa3-b7e5-861daee95696")
        admin_id = "07ea3efc-a004-4d31-8683-4bb2084e209b"
        template = h.invoke("roles.get", {"role_id": reader["id"]})
        role = h.invoke(
            "roles.create",
            {
                "name": h.prefix + "-role",
                "permissions": template["permissions"],
                "new_permissions_default_value": False,
            },
        )
        h.register(
            "roles.delete",
            {"role_id": role["id"], "replacing_role_id": reader["id"]},
            "roles.get",
            {"role_id": role["id"]},
            kind="role",
        )
        h.invoke(
            "roles.update",
            {
                "role_id": role["id"],
                "name": h.prefix + "-role-updated",
                "permissions": {"document": {"update": False}},
            },
        )
        updated = h.invoke("roles.get", {"role_id": role["id"]})
        h.verify(
            updated["name"].endswith("-updated")
            and updated["permissions"]["document"]["update"] is False,
            "partial role update",
        )

        group = h.invoke(
            "company-groups.create",
            {"name": h.prefix + "-group", "named_permissions": {"entitiesTree": False}},
        )
        group_uid = group["uid"]
        h.register(
            "company-groups.delete",
            {"group_uid": group_uid},
            "company-groups.get",
            {"group_uid": group_uid},
        )
        for enabled in (True, False):
            h.invoke(
                "company-groups.update",
                {"group_uid": group_uid, "named_permissions": {"entitiesTree": enabled}},
            )
            readback = h.invoke("company-groups.get", {"group_uid": group_uid})
            h.verify(
                readback.get("named_permissions", {}).get("entitiesTree") is enabled,
                f"group entitiesTree={enabled}",
            )

        folder = h.invoke(
            "document-groups.create", {"title": h.prefix + "-folder", "sort_order": 1}
        )
        folder_uid = folder["uid"]
        h.register(
            "document-groups.delete",
            {"group_uid": folder_uid},
            "document-groups.get",
            {"group_uid": folder_uid},
        )
        destination = h.invoke(
            "document-groups.create", {"title": h.prefix + "-destination", "sort_order": 1}
        )
        destination_uid = destination["uid"]
        h.register(
            "document-groups.delete",
            {"group_uid": destination_uid},
            "document-groups.get",
            {"group_uid": destination_uid},
        )
        space = h.invoke(
            "spaces.create",
            {"title": h.prefix + "-space", "access": "by_invite", "parent_entity_uid": folder_uid},
        )
        h.register(
            "spaces.delete",
            {"space_id": space["id"]},
            "spaces.get",
            {"space_id": space["id"]},
            kind="space",
        )
        doc = h.invoke(
            "documents.create",
            {
                "title": h.prefix + "-document",
                "parent_entity_uid": folder_uid,
                "text": "Temporary API access validation.",
            },
        )
        doc_uid = doc["uid"]
        h.register(
            "documents.delete",
            {"document_uid": doc_uid},
            "documents.get",
            {"document_uid": doc_uid},
            restore=[
                "document-users.add",
                {"document_uid": doc_uid, "user_id": actor_id, "role_id": admin_id},
            ],
        )
        story = h.invoke(
            "story-maps.create",
            {
                "title": h.prefix + "-story",
                "access": "by_invite",
                "parent_entity_uid": folder_uid,
            },
        )
        map_id = story["id"]
        h.register(
            "story-maps.delete",
            {"map_id": map_id},
            "story-maps.get",
            {"map_id": map_id},
            kind="story",
            restore=[
                "story-map-users.add",
                {"map_id": map_id, "user_id": actor_id, "role_id": admin_id},
            ],
        )

        h.invoke("story-maps.list", {"limit": 100, "offset": 0, "query": h.prefix})
        h.invoke(
            "story-maps.update",
            {
                "map_id": map_id,
                "title": h.prefix + "-story-updated",
                "parent_entity_uid": destination_uid,
            },
        )
        moved = h.invoke("story-maps.get", {"map_id": map_id})
        h.verify(moved["parent_entity_uid"] == destination_uid, "story map moved")
        h.invoke(
            "story-map-users.update", {"map_id": map_id, "user_id": actor_id, "role_id": admin_id}
        )
        h.invoke("story-maps.update", {"map_id": map_id, "parent_entity_uid": None})
        moved = h.invoke("story-maps.get", {"map_id": map_id})
        h.verify(moved["parent_entity_uid"] is None, "story map moved to root")
        h.invoke("story-maps.update", {"map_id": map_id, "parent_entity_uid": folder_uid})

        page = h.invoke("admin-tree-entities.list", {"parent_uid": folder_uid, "limit": 100})
        h.verify(
            {doc_uid, story["uid"], space["uid"]} <= {row["uid"] for row in page},
            "admin listing contains temporary children",
        )
        inventory = h.invoke(
            "admin-tree-entities.list-all",
            {
                "page_size": 100,
                "max_pages": 100,
                "fields": "uid,title,parent_entity_uid,entity_type",
            },
        )
        h.verify(
            folder_uid in {row["uid"] for row in inventory},
            "bounded inventory contains temporary folder",
        )

        h.invoke(
            "document-users.update",
            {"document_uid": doc_uid, "user_id": actor_id, "role_id": admin_id},
        )
        h.invoke(
            "documents.update",
            {"document_uid": doc_uid, "parent_entity_uid": None, "access": "by_invite"},
        )
        h.invoke("document-groups.update", {"group_uid": folder_uid, "access": "by_invite"})
        h.invoke("story-maps.update", {"map_id": map_id, "parent_entity_uid": None})

        # Only temporary-object ACLs change; the actor retains access-control rights.
        for namespace, target in (
            ("document-users", {"document_uid": doc_uid}),
            ("story-map-users", {"map_id": map_id}),
            ("document-group-users", {"group_uid": folder_uid}),
        ):
            h.invoke(
                f"{namespace}.add",
                {**target, "user_id": target_id, "role_id": reader["id"], "send_email": False},
            )
            rows = h.invoke(f"{namespace}.list", {**target, "include_inherited_access": True})
            row = _user(rows, target_id)
            h.verify(
                row is not None and reader["id"] in row.get("own_role_ids", []),
                namespace + " direct grant",
            )
            h.invoke(f"{namespace}.update", {**target, "user_id": target_id, "role_id": admin_id})
            rows = h.invoke(f"{namespace}.list", {**target, "include_inherited_access": False})
            h.verify(
                admin_id in _user(rows, target_id).get("own_role_ids", []),
                namespace + " role changed",
            )
            h.invoke(f"{namespace}.remove", {**target, "user_id": target_id})
            rows = h.invoke(f"{namespace}.list", {**target, "include_inherited_access": False})
            row = _user(rows, target_id)
            h.verify(row is None or not row.get("own_role_ids"), namespace + " direct revoke")
        h.invoke("group-users.add", {"group_uid": group_uid, "user_id": target_id})
        for namespace, entity_uid in (
            ("space-access-groups", space["uid"]),
            ("document-access-groups", doc_uid),
            ("document-group-access-groups", folder_uid),
            ("story-map-access-groups", story["uid"]),
        ):
            h.invoke(
                "group-entities.add",
                {"group_uid": group_uid, "entity_uid": entity_uid, "role_ids": [role["id"]]},
            )
            rows = h.invoke(
                f"{namespace}.list", {"entity_uid": entity_uid, "include_inherited_access": True}
            )
            h.verify(
                any(row.get("uid", row.get("group_uid")) == group_uid for row in rows),
                namespace + " group grant",
            )
            h.invoke("group-entities.remove", {"group_uid": group_uid, "entity_uid": entity_uid})
            rows = h.invoke(
                f"{namespace}.list", {"entity_uid": entity_uid, "include_inherited_access": False}
            )
            h.verify(
                not any(
                    row.get("uid", row.get("group_uid")) == group_uid and row.get("own_role_ids")
                    for row in rows
                ),
                namespace + " group revoke",
            )
        h.invoke("group-users.remove", {"group_uid": group_uid, "user_id": target_id})

    finally:
        h.teardown()
    expected = {tool.canonical_name for tool in TOOLS}
    assert expected <= h.covered, f"Uncovered commands: {sorted(expected - h.covered)}"


@pytest.mark.live
@pytest.mark.timeout(180)
def test_virtual_company_permissions_live(tmp_path, socket_enabled):
    if os.environ.get("KAITEN_LIVE", "").lower() not in ("1", "true"):
        pytest.skip("Set KAITEN_LIVE=1|true")
    profile_name = os.environ.get("KAITEN_ACCESS_LIVE_PROFILE")
    expected_domain = os.environ.get("KAITEN_ACCESS_LIVE_DOMAIN")
    if not profile_name or not expected_domain:
        pytest.skip("Select an explicit access-test profile and expected domain")
    profile = resolve_profile(profile_name)
    assert profile.domain == expected_domain
    root = Path(os.environ.get("KAITEN_ACCESS_LIVE_DIR", str(tmp_path / "access-live"))) / "virtual"
    h = AccessCampaign(root, profile_name)
    h.probe()
    try:
        # Setup-only API fixture: CLI has no company-user create command.
        async def create_virtual():
            client = KaitenClient(domain=profile.domain, token=profile.token)
            try:
                return await client.post(
                    "/company/users", json={"virtual": True, "full_name": h.prefix + "-virtual"}
                )
            finally:
                await client.close()

        h.journal("fixture.virtual-user.create", {"full_name": h.prefix + "-virtual"}, "pending")
        virtual = asyncio.run(create_virtual())
        virtual_id = virtual["id"]
        h.journal("fixture.virtual-user.create", {"user_id": virtual_id}, "applied")
        h.register(
            "company-users.remove-virtual",
            {"user_id": virtual_id},
            "company-users.list",
            {"query": h.prefix},
            kind="virtual",
        )
        for enabled in (True, False):
            result = h.invoke(
                "company-users.update",
                {"user_id": virtual_id, "named_permissions": {"entitiesTree": enabled}},
                allow_error=True,
            )
            if isinstance(result, dict) and result.get("success") is False:
                error = result.get("error", {})
                if error.get("type") == "transport_error" and "500" in error.get("message", ""):
                    # Read before any other write; no retry or account activation.
                    rows = h.invoke(
                        "company-users.list",
                        {"only_virtual": True, "limit": 100, "query": h.prefix},
                    )
                    h.verify(
                        _user(rows, virtual_id) is not None,
                        "failed mutation recipient still identifiable for cleanup",
                    )
                    pytest.xfail(
                        "Test tenant returns HTTP 500 for a virtual user's company permissions; result is uncertain, no retry is made, and the temporary user is deleted"
                    )
                raise AssertionError(f"Unexpected company-user permission response: {error}")
            users = h.invoke("company-users.list", {"query": h.prefix, "limit": 100})
            users = (
                users if isinstance(users, list) else users.get("records", users.get("users", []))
            )
            row = _user(users, virtual_id)
            h.verify(
                row is not None
                and row.get("own_named_permissions", {}).get("entitiesTree") is enabled,
                f"virtual direct entitiesTree={enabled}",
            )

    finally:
        h.teardown()


@pytest.mark.live
@pytest.mark.timeout(240)
def test_access_inheritance_live(tmp_path, socket_enabled):
    if os.environ.get("KAITEN_LIVE", "").lower() not in ("1", "true"):
        pytest.skip("Set KAITEN_LIVE=1|true")
    profile_name = os.environ.get("KAITEN_ACCESS_LIVE_PROFILE")
    domain = os.environ.get("KAITEN_ACCESS_LIVE_DOMAIN")
    if not profile_name or not domain:
        pytest.skip("Select an explicit access-test profile and expected domain")
    assert resolve_profile(profile_name).domain == domain
    root = (
        Path(os.environ.get("KAITEN_ACCESS_LIVE_DIR", str(tmp_path / "access-live")))
        / "inheritance"
    )
    h = AccessCampaign(root, profile_name)
    h.probe()
    try:
        actor = h.invoke("users.current")
        members = h.invoke(
            "company-users.list", {"access_type_permissions": "member", "limit": 100}
        )
        members = (
            members
            if isinstance(members, list)
            else members.get("records", members.get("users", []))
        )
        target = next(
            row
            for row in members
            if row.get("id", row.get("user_id")) != actor["id"]
            and not row.get("virtual")
            and not row.get("temporarily_inactive")
            and row.get("apps_permissions", 0) & 1
        )
        user_id = target.get("id", target.get("user_id"))
        group = h.invoke("company-groups.create", {"name": h.prefix + "-group"})
        group_uid = group["uid"]
        h.register(
            "company-groups.delete",
            {"group_uid": group_uid},
            "company-groups.get",
            {"group_uid": group_uid},
        )
        h.invoke("group-users.add", {"group_uid": group_uid, "user_id": user_id})
        folder = h.invoke("document-groups.create", {"title": h.prefix + "-folder"})
        uid = folder["uid"]
        h.register(
            "document-groups.delete", {"group_uid": uid}, "document-groups.get", {"group_uid": uid}
        )
        h.invoke("document-groups.update", {"group_uid": uid, "access": "by_invite"})
        doc = h.invoke(
            "documents.create",
            {
                "title": h.prefix + "-document",
                "parent_entity_uid": uid,
                "text": "Temporary inherited-access test.",
            },
        )
        doc_uid = doc["uid"]
        h.register(
            "documents.delete",
            {"document_uid": doc_uid},
            "documents.get",
            {"document_uid": doc_uid},
        )
        reader_id = "06ccb31f-426b-4fa3-b7e5-861daee95696"
        h.invoke(
            "group-entities.add",
            {"group_uid": group_uid, "entity_uid": uid, "role_ids": [reader_id]},
        )
        inherited = h.invoke(
            "document-users.list", {"document_uid": doc_uid, "include_inherited_access": True}
        )
        row = _user(inherited, user_id)
        h.verify(
            row is not None
            and reader_id in (row.get("groups_role_ids") or [])
            and not row.get("own_role_ids"),
            "group role inherited from parent folder",
        )
        direct = h.invoke(
            "document-users.list", {"document_uid": doc_uid, "include_inherited_access": False}
        )
        h.verify(_user(direct, user_id) is None, "inherited user absent from direct-only listing")
        groups = h.invoke(
            "document-access-groups.list", {"entity_uid": doc_uid, "include_inherited_access": True}
        )
        h.verify(
            any(row.get("uid", row.get("group_uid")) == group_uid for row in groups),
            "inherited group exposed by entity group listing",
        )
        h.invoke("group-entities.remove", {"group_uid": group_uid, "entity_uid": uid})
        inherited = h.invoke(
            "document-users.list", {"document_uid": doc_uid, "include_inherited_access": True}
        )
        h.verify(
            _user(inherited, user_id) is None,
            "removing parent group grant removes inherited access",
        )
        h.invoke("group-users.remove", {"group_uid": group_uid, "user_id": user_id})
    finally:
        h.teardown()


@pytest.mark.live
@pytest.mark.timeout(240)
def test_group_entities_pagination_live(tmp_path, socket_enabled):
    if os.environ.get("KAITEN_LIVE", "").lower() not in ("1", "true"):
        pytest.skip("Set KAITEN_LIVE=1|true")
    profile_name = os.environ.get("KAITEN_ACCESS_LIVE_PROFILE")
    domain = os.environ.get("KAITEN_ACCESS_LIVE_DOMAIN")
    if not profile_name or not domain:
        pytest.skip("Select an explicit access-test profile and expected domain")
    assert resolve_profile(profile_name).domain == domain
    root = (
        Path(os.environ.get("KAITEN_ACCESS_LIVE_DIR", str(tmp_path / "access-live")))
        / "group-pagination"
    )
    h = AccessCampaign(root, profile_name)
    h.probe()
    try:
        group = h.invoke("company-groups.create", {"name": h.prefix + "-group"})
        group_uid = group["uid"]
        h.register(
            "company-groups.delete",
            {"group_uid": group_uid},
            "company-groups.get",
            {"group_uid": group_uid},
        )
        reader_id = "06ccb31f-426b-4fa3-b7e5-861daee95696"
        folders = []
        for index in range(3):
            folder = h.invoke("document-groups.create", {"title": f"{h.prefix}-folder-{index}"})
            uid = folder["uid"]
            folders.append(uid)
            h.register(
                "document-groups.delete",
                {"group_uid": uid},
                "document-groups.get",
                {"group_uid": uid},
            )
            h.invoke("document-groups.update", {"group_uid": uid, "access": "by_invite"})
            h.invoke(
                "group-entities.add",
                {
                    "group_uid": group_uid,
                    "entity_uid": uid,
                    "role_ids": [reader_id],
                },
            )
            groups = h.invoke(
                "document-group-access-groups.list",
                {
                    "entity_uid": uid,
                    "include_inherited_access": False,
                },
            )
            h.verify(
                any(
                    row.get("uid", row.get("group_uid")) == group_uid
                    and reader_id in (row.get("own_role_ids") or [])
                    for row in groups
                ),
                "temporary group has direct reader role",
            )

        pages = [
            h.invoke(
                "group-entities.list",
                {
                    "group_uid": group_uid,
                    "limit": 2,
                    "offset": offset,
                    "fields": "uid,title",
                    "compact": True,
                },
            )
            for offset in (0, 2)
        ]
        h.verify([len(page) for page in pages] == [2, 1], "server honors group pagination")
        paged_uids = [row["uid"] for page in pages for row in page]
        h.verify(
            len(set(paged_uids)) == 3 and set(paged_uids) == set(folders),
            "pages cover all three entities",
        )
        all_rows = h.invoke(
            "group-entities.list-all",
            {
                "group_uid": group_uid,
                "page_size": 2,
                "max_pages": 2,
                "fields": "uid,title",
                "compact": True,
            },
        )
        h.verify(all_rows == pages[0] + pages[1], "list-all agrees with explicit pages")
        for uid in folders:
            h.invoke("group-entities.remove", {"group_uid": group_uid, "entity_uid": uid})
            groups = h.invoke(
                "document-group-access-groups.list",
                {
                    "entity_uid": uid,
                    "include_inherited_access": False,
                },
            )
            h.verify(
                not any(row.get("uid", row.get("group_uid")) == group_uid for row in groups),
                "temporary group reader role revoked",
            )
        h.verify(
            h.invoke(
                "group-entities.list-all",
                {
                    "group_uid": group_uid,
                    "page_size": 2,
                    "max_pages": 2,
                },
            )
            == [],
            "group has no remaining entity assignments",
        )
    finally:
        h.teardown()
