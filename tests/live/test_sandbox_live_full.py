from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest


def _iso_date(days_delta: int) -> str:
    return (datetime.now(UTC) + timedelta(days=days_delta)).date().isoformat()


def _iso_datetime(days_delta: int) -> str:
    return (datetime.now(UTC) + timedelta(days=days_delta)).replace(microsecond=0).isoformat()


def _pick_other_user_id(users: list[dict], current_user_id: int) -> int | None:
    for item in users:
        if isinstance(item, dict) and item.get("id") != current_user_id:
            return item["id"]
    return None


def _pick_first_id(items: list[dict], *, key: str = "id"):
    for item in items:
        if isinstance(item, dict) and key in item:
            return item[key]
    raise AssertionError(f"Expected at least one item with key {key!r}")


def _find_id_by_title(items: list[dict], title: str) -> int | None:
    for item in items:
        if isinstance(item, dict) and item.get("title") == title and "id" in item:
            return item["id"]
    return None


def _automation_actions(current_user_id: int) -> list[dict]:
    return [
        {
            "type": "add_assignee",
            "created": _iso_datetime(0),
            "data": {"variant": "specific", "userId": current_user_id},
        }
    ]


def _exercise_foundation(h) -> None:
    company = h.run_tool("company.current")
    h.state["company_name"] = company["name"]
    h.run_tool("company.update", name=company["name"])

    current_user = h.run_tool("users.current")
    h.state["current_user_id"] = current_user["id"]
    h.state["current_user_full_name"] = current_user.get("full_name") or current_user.get("username") or "Codex Live User"
    h.state["current_user_lng"] = current_user.get("lng")

    users = h.run_tool("users.list", limit=10, compact=True)
    h.state["users"] = users
    h.state["other_user_id"] = _pick_other_user_id(users, current_user["id"])

    calendars = h.run_tool("calendars.list", limit=5)
    h.state["calendar_id"] = _pick_first_id(calendars)
    h.run_tool("calendars.get", calendar_id=h.state["calendar_id"])

    h.run_non_tool("search-tools", "service desk sla")
    h.run_non_tool("describe", "cards.create")
    h.run_non_tool("examples", "cards.create")

    primary_space = h.run_tool(
        "spaces.create",
        title=h.name("space"),
        description="Full live validation space",
        access="for_everyone",
    )
    h.state["space_id"] = primary_space["id"]
    h.push_cleanup("delete primary space", "spaces.delete", space_id=h.state["space_id"])
    h.run_tool("spaces.list", compact=True, fields="id,title")
    h.run_tool("spaces.get", space_id=h.state["space_id"])
    h.run_tool("spaces.update", space_id=h.state["space_id"], title=h.name("space-updated"))

    secondary_space = h.run_tool(
        "spaces.create",
        title=h.name("space-secondary"),
        description="Secondary full live validation space",
        access="for_everyone",
    )
    h.state["secondary_space_id"] = secondary_space["id"]
    h.push_cleanup("delete secondary space", "spaces.delete", space_id=h.state["secondary_space_id"])

    primary_board = h.run_tool("boards.create", space_id=h.state["space_id"], title=h.name("board"))
    h.state["board_id"] = primary_board["id"]
    h.push_cleanup("delete primary board", "boards.delete", space_id=h.state["space_id"], board_id=h.state["board_id"], force=True)
    h.run_tool("boards.list", space_id=h.state["space_id"], compact=True)
    h.run_tool("boards.get", board_id=h.state["board_id"])
    h.run_tool("boards.update", space_id=h.state["space_id"], board_id=h.state["board_id"], title=h.name("board-updated"))

    secondary_board = h.run_tool("boards.create", space_id=h.state["secondary_space_id"], title=h.name("board-secondary"))
    h.state["secondary_board_id"] = secondary_board["id"]
    h.push_cleanup(
        "delete secondary board",
        "boards.delete",
        space_id=h.state["secondary_space_id"],
        board_id=h.state["secondary_board_id"],
        force=True,
    )

    disposable_board = h.run_tool("boards.create", space_id=h.state["space_id"], title=h.name("board-disposable"))
    h.run_tool("boards.delete", space_id=h.state["space_id"], board_id=disposable_board["id"], force=True)
    h.run_tool_expect_api_error("removed-boards.list", {405}, limit=5)

    queue_column = h.run_tool("columns.create", board_id=h.state["board_id"], title=h.name("queue"), type=1)
    h.state["queue_column_id"] = queue_column["id"]
    h.push_cleanup("delete queue column", "columns.delete", board_id=h.state["board_id"], column_id=h.state["queue_column_id"])
    progress_column = h.run_tool("columns.create", board_id=h.state["board_id"], title=h.name("progress"), type=2)
    h.state["progress_column_id"] = progress_column["id"]
    h.push_cleanup("delete progress column", "columns.delete", board_id=h.state["board_id"], column_id=h.state["progress_column_id"])
    done_column = h.run_tool("columns.create", board_id=h.state["board_id"], title=h.name("done"), type=3)
    h.state["done_column_id"] = done_column["id"]
    h.push_cleanup("delete done column", "columns.delete", board_id=h.state["board_id"], column_id=h.state["done_column_id"])
    h.run_tool("columns.list", board_id=h.state["board_id"])
    h.run_tool("columns.update", board_id=h.state["board_id"], column_id=h.state["queue_column_id"], title=h.name("queue-updated"))

    disposable_column = h.run_tool("columns.create", board_id=h.state["board_id"], title=h.name("column-disposable"), type=1)
    h.run_tool("columns.delete", board_id=h.state["board_id"], column_id=disposable_column["id"])

    lane = h.run_tool("lanes.create", board_id=h.state["board_id"], title=h.name("lane"))
    h.state["lane_id"] = lane["id"]
    h.push_cleanup("delete lane", "lanes.delete", board_id=h.state["board_id"], lane_id=h.state["lane_id"])
    h.run_tool("lanes.list", board_id=h.state["board_id"])
    h.run_tool("lanes.update", board_id=h.state["board_id"], lane_id=h.state["lane_id"], title=h.name("lane-updated"))

    disposable_lane = h.run_tool("lanes.create", board_id=h.state["board_id"], title=h.name("lane-disposable"))
    h.run_tool("lanes.delete", board_id=h.state["board_id"], lane_id=disposable_lane["id"])

    subcolumn = h.run_tool("subcolumns.create", column_id=h.state["queue_column_id"], title=h.name("subcolumn"))
    h.state["subcolumn_id"] = subcolumn["id"]
    h.push_cleanup("delete subcolumn", "subcolumns.delete", column_id=h.state["queue_column_id"], subcolumn_id=h.state["subcolumn_id"])
    h.run_tool("subcolumns.list", column_id=h.state["queue_column_id"])
    h.run_tool("subcolumns.update", column_id=h.state["queue_column_id"], subcolumn_id=h.state["subcolumn_id"], title=h.name("subcolumn-updated"))

    parent_card = h.run_tool(
        "cards.create",
        title=h.name("card-parent"),
        board_id=h.state["board_id"],
        column_id=h.state["queue_column_id"],
        lane_id=h.state["lane_id"],
    )
    h.state["parent_card_id"] = parent_card["id"]
    h.push_cleanup("delete parent card", "cards.delete", card_id=h.state["parent_card_id"])

    child_card = h.run_tool(
        "cards.create",
        title=h.name("card-child"),
        board_id=h.state["board_id"],
        column_id=h.state["queue_column_id"],
        lane_id=h.state["lane_id"],
    )
    h.state["child_card_id"] = child_card["id"]
    h.push_cleanup("delete child card", "cards.delete", card_id=h.state["child_card_id"])

    extra_card = h.run_tool(
        "cards.create",
        title=h.name("card-extra"),
        board_id=h.state["board_id"],
        column_id=h.state["queue_column_id"],
        lane_id=h.state["lane_id"],
    )
    h.state["extra_card_id"] = extra_card["id"]
    h.push_cleanup("delete extra card", "cards.delete", card_id=h.state["extra_card_id"])

    archive_card = h.run_tool(
        "cards.create",
        title=h.name("card-archive"),
        board_id=h.state["board_id"],
        column_id=h.state["queue_column_id"],
    )
    h.run_tool("cards.archive", card_id=archive_card["id"])
    h.push_cleanup("delete archived card", "cards.delete", card_id=archive_card["id"])

    removed_card = h.run_tool(
        "cards.create",
        title=h.name("card-removed"),
        board_id=h.state["board_id"],
        column_id=h.state["queue_column_id"],
    )
    h.run_tool("cards.delete", card_id=removed_card["id"])
    h.run_tool_expect_api_error("removed-cards.list", {405}, limit=5)

    h.run_tool("cards.list", board_id=h.state["board_id"], limit=10, compact=True)
    h.run_tool("cards.get", card_id=h.state["parent_card_id"], compact=True, fields="id,title,state,board_id")
    h.run_tool("cards.update", card_id=h.state["parent_card_id"], title=h.name("card-parent-updated"))
    h.run_tool(
        "cards.move",
        card_id=h.state["parent_card_id"],
        board_id=h.state["board_id"],
        column_id=h.state["progress_column_id"],
        lane_id=h.state["lane_id"],
    )
    h.run_tool(
        "cards.move",
        card_id=h.state["parent_card_id"],
        board_id=h.state["board_id"],
        column_id=h.state["queue_column_id"],
        lane_id=h.state["lane_id"],
    )
    h.run_tool("cards.list-all", board_id=h.state["board_id"], page_size=5, max_pages=1, compact=True)

    time_log = h.run_tool("time-logs.create", card_id=h.state["parent_card_id"], time_spent=15, comment="live")
    h.state["time_log_id"] = time_log["id"]
    h.push_cleanup("delete time log", "time-logs.delete", card_id=h.state["parent_card_id"], time_log_id=h.state["time_log_id"])
    h.run_tool("time-logs.list", card_id=h.state["parent_card_id"])
    h.run_tool(
        "time-logs.update",
        card_id=h.state["parent_card_id"],
        time_log_id=h.state["time_log_id"],
        time_spent=20,
        comment="live-updated",
    )


def _exercise_card_adjacent(h) -> None:
    comment = h.run_tool("comments.create", card_id=h.state["parent_card_id"], text="Live comment", format="markdown")
    h.state["comment_id"] = comment["id"]
    h.push_cleanup("delete comment", "comments.delete", card_id=h.state["parent_card_id"], comment_id=h.state["comment_id"])
    h.run_tool("comments.list", card_id=h.state["parent_card_id"], compact=True)
    h.run_tool("comments.update", card_id=h.state["parent_card_id"], comment_id=h.state["comment_id"], text="Live comment updated")

    checklist = h.run_tool("checklists.create", card_id=h.state["parent_card_id"], name=h.name("checklist"))
    h.state["checklist_id"] = checklist["id"]
    h.push_cleanup("delete checklist", "checklists.delete", card_id=h.state["parent_card_id"], checklist_id=h.state["checklist_id"])
    h.run_tool_expect_api_error("checklists.list", {405}, card_id=h.state["parent_card_id"])
    h.run_tool("checklists.update", card_id=h.state["parent_card_id"], checklist_id=h.state["checklist_id"], name=h.name("checklist-updated"))

    checklist_item = h.run_tool(
        "checklist-items.create",
        card_id=h.state["parent_card_id"],
        checklist_id=h.state["checklist_id"],
        text="Live checklist item",
    )
    h.state["checklist_item_id"] = checklist_item["id"]
    h.push_cleanup(
        "delete checklist item",
        "checklist-items.delete",
        card_id=h.state["parent_card_id"],
        checklist_id=h.state["checklist_id"],
        item_id=h.state["checklist_item_id"],
    )
    h.run_tool_expect_api_error(
        "checklist-items.list",
        {405},
        card_id=h.state["parent_card_id"],
        checklist_id=h.state["checklist_id"],
    )
    h.run_tool(
        "checklist-items.update",
        card_id=h.state["parent_card_id"],
        checklist_id=h.state["checklist_id"],
        item_id=h.state["checklist_item_id"],
        text="Live checklist item updated",
        checked=True,
    )

    external_link = h.run_tool(
        "external-links.create",
        card_id=h.state["parent_card_id"],
        url="https://example.com/live-link",
        description="live external link",
    )
    h.state["external_link_id"] = external_link["id"]
    h.push_cleanup(
        "delete external link",
        "external-links.delete",
        card_id=h.state["parent_card_id"],
        link_id=h.state["external_link_id"],
    )
    h.run_tool("external-links.list", card_id=h.state["parent_card_id"])
    h.run_tool(
        "external-links.update",
        card_id=h.state["parent_card_id"],
        link_id=h.state["external_link_id"],
        description="live external link updated",
    )

    file_link = h.run_tool(
        "files.create",
        card_id=h.state["parent_card_id"],
        name="live-asset.txt",
        url="https://example.com/live-asset.txt",
        type=1,
    )
    h.state["file_id"] = file_link["id"]
    h.push_cleanup("delete file", "files.delete", card_id=h.state["parent_card_id"], file_id=h.state["file_id"])
    h.run_tool("files.list", card_id=h.state["parent_card_id"])
    h.run_tool("files.update", card_id=h.state["parent_card_id"], file_id=h.state["file_id"], name="live-asset-updated.txt")

    blocker = h.run_tool("blockers.create", card_id=h.state["parent_card_id"], reason="live blocker")
    h.state["blocker_id"] = blocker["id"]
    h.push_cleanup("delete blocker", "blockers.delete", card_id=h.state["parent_card_id"], blocker_id=h.state["blocker_id"])
    h.run_tool("blockers.list", card_id=h.state["parent_card_id"])
    h.run_tool("blockers.get", card_id=h.state["parent_card_id"], blocker_id=h.state["blocker_id"])
    h.run_tool("blockers.update", card_id=h.state["parent_card_id"], blocker_id=h.state["blocker_id"], reason="live blocker updated")

    tag = h.run_tool("tags.create", name=h.name("tag"))
    h.state["tag_id"] = tag["id"]
    h.push_cleanup("delete tag", "tags.delete", tag_id=h.state["tag_id"])
    h.run_tool("tags.list", limit=10)
    h.run_tool("tags.update", tag_id=h.state["tag_id"], name=h.name("tag-updated"))
    h.run_tool("card-tags.add", card_id=h.state["parent_card_id"], name=h.name("tag-on-card"))
    h.push_cleanup("remove explicit tag", "card-tags.remove", card_id=h.state["parent_card_id"], tag_id=h.state["tag_id"])

    h.run_tool("card-members.list", card_id=h.state["parent_card_id"], compact=True)
    member_user_id = h.state["other_user_id"] or h.state["current_user_id"]
    member_added, _ = h.run_tool_maybe(
        "card-members.add",
        expected_error_statuses={400, 404, 409},
        card_id=h.state["parent_card_id"],
        user_id=member_user_id,
    )
    if member_added:
        h.push_cleanup("remove card member", "card-members.remove", card_id=h.state["parent_card_id"], user_id=member_user_id)
    else:
        h.run_tool_maybe(
            "card-members.remove",
            expected_error_statuses={404},
            card_id=h.state["parent_card_id"],
            user_id=0,
        )

    h.run_tool_expect_api_error("card-subscribers.list", {405}, card_id=h.state["parent_card_id"], compact=True)
    subscriber_user_id = h.state["other_user_id"] or h.state["current_user_id"]
    subscriber_added, _ = h.run_tool_maybe(
        "card-subscribers.add",
        expected_error_statuses={400, 404, 409},
        card_id=h.state["parent_card_id"],
        user_id=subscriber_user_id,
    )
    if subscriber_added:
        h.push_cleanup("remove card subscriber", "card-subscribers.remove", card_id=h.state["parent_card_id"], user_id=subscriber_user_id)
    else:
        h.run_tool_maybe(
            "card-subscribers.remove",
            expected_error_statuses={404},
            card_id=h.state["parent_card_id"],
            user_id=0,
        )

    h.run_tool_expect_api_error("column-subscribers.list", {405}, column_id=h.state["queue_column_id"], compact=True)
    column_subscriber_added, _ = h.run_tool_maybe(
        "column-subscribers.add",
        expected_error_statuses={400, 404, 409},
        column_id=h.state["queue_column_id"],
        user_id=subscriber_user_id,
    )
    if column_subscriber_added:
        h.push_cleanup("remove column subscriber", "column-subscribers.remove", column_id=h.state["queue_column_id"], user_id=subscriber_user_id)
    else:
        h.run_tool_maybe(
            "column-subscribers.remove",
            expected_error_statuses={404},
            column_id=h.state["queue_column_id"],
            user_id=0,
        )

    h.run_tool("card-children.add", card_id=h.state["parent_card_id"], child_card_id=h.state["child_card_id"])
    h.push_cleanup("remove child relation", "card-children.remove", card_id=h.state["parent_card_id"], child_id=h.state["child_card_id"])
    h.run_tool("card-children.list", card_id=h.state["parent_card_id"])
    h.run_tool("card-parents.list", card_id=h.state["child_card_id"])

    h.run_tool("card-parents.add", card_id=h.state["extra_card_id"], parent_card_id=h.state["parent_card_id"])
    h.push_cleanup("remove parent relation", "card-parents.remove", card_id=h.state["extra_card_id"], parent_id=h.state["parent_card_id"])
    h.run_tool("card-parents.list", card_id=h.state["extra_card_id"])


def _exercise_projects_documents_and_tree(h) -> None:
    projects = h.run_tool("projects.list")
    assert isinstance(projects, list)

    project = h.run_tool("projects.create", title=h.name("project"), description="live project")
    h.state["project_id"] = project["id"]
    h.push_cleanup("delete project", "projects.delete", project_id=h.state["project_id"])
    h.run_tool("projects.get", project_id=h.state["project_id"], with_cards_data=True)
    h.run_tool("projects.update", project_id=h.state["project_id"], title=h.name("project-updated"))
    h.run_tool("projects.cards.add", project_id=h.state["project_id"], card_id=h.state["parent_card_id"])
    h.push_cleanup("remove project card", "projects.cards.remove", project_id=h.state["project_id"], card_id=h.state["parent_card_id"])
    h.run_tool("projects.cards.list", project_id=h.state["project_id"], compact=True)

    sprint_title = h.name("sprint")
    sprint_created, sprint_data = h.run_tool_maybe(
        "sprints.create",
        expected_error_statuses={403, 405},
        title=sprint_title,
        board_id=h.state["board_id"],
        goal="live sprint",
        start_date=_iso_datetime(-1),
        finish_date=_iso_datetime(7),
    )
    sprints_list_ok, sprints_list_payload = h.run_tool_maybe("sprints.list", expected_error_statuses={403, 405}, limit=10)
    if sprint_created:
        sprint_id = sprint_data.get("id")
        if sprint_id is None and sprints_list_ok:
            sprint_id = _find_id_by_title(sprints_list_payload, sprint_title)
        if sprint_id is not None:
            h.state["sprint_id"] = sprint_id
            h.run_tool("sprints.get", sprint_id=h.state["sprint_id"])
            h.run_tool("sprints.update", sprint_id=h.state["sprint_id"], goal="live sprint updated", active=False, archive_done_cards=False)
            h.run_tool_maybe("sprints.delete", expected_error_statuses={405}, sprint_id=h.state["sprint_id"])
        else:
            h.run_tool_expect_api_error("sprints.get", {403, 404, 405}, sprint_id=0)
            h.run_tool_expect_api_error("sprints.update", {403, 404, 405, 500}, sprint_id=0, goal="noop")
            h.run_tool_expect_api_error("sprints.delete", {403, 404, 405}, sprint_id=0)
    else:
        h.run_tool_expect_api_error("sprints.get", {403, 404, 405}, sprint_id=0)
        h.run_tool_expect_api_error("sprints.update", {403, 404, 405, 500}, sprint_id=0, goal="noop")
        h.run_tool_expect_api_error("sprints.delete", {403, 404, 405}, sprint_id=0)

    doc_group = h.run_tool("document-groups.create", title=h.name("doc-group"), sort_order=1)
    h.state["doc_group_uid"] = doc_group["uid"]
    h.push_cleanup("delete document group", "document-groups.delete", group_uid=h.state["doc_group_uid"])
    h.run_tool("document-groups.list", limit=10)
    h.run_tool("document-groups.get", group_uid=h.state["doc_group_uid"])
    h.run_tool("document-groups.update", group_uid=h.state["doc_group_uid"], title=h.name("doc-group-updated"))

    document = h.run_tool(
        "documents.create",
        title=h.name("document"),
        text="# Live document\n\nBody",
        sort_order=1,
        parent_entity_uid=h.state["doc_group_uid"],
    )
    h.state["document_uid"] = document["uid"]
    h.push_cleanup("delete document", "documents.delete", document_uid=h.state["document_uid"])
    h.run_tool("documents.list", limit=10)
    h.run_tool("documents.get", document_uid=h.state["document_uid"])
    h.run_tool("documents.update", document_uid=h.state["document_uid"], title=h.name("document-updated"), text="# Updated")

    h.run_tool("tree.children.list", parent_entity_uid=h.state["doc_group_uid"])
    h.run_tool("tree.get", root_uid=h.state["doc_group_uid"], depth=2)


def _exercise_company_metadata(h) -> None:
    roles = h.run_tool("roles.list", limit=10)
    role_id = _pick_first_id(roles)
    h.run_tool("roles.get", role_id=role_id)
    h.state["role_id"] = role_id

    h.run_tool("space-users.list", space_id=h.state["space_id"], compact=True)
    space_user_target = h.state["other_user_id"] or h.state["current_user_id"]
    space_user_added, _ = h.run_tool_maybe(
        "space-users.add",
        expected_error_statuses={400, 404, 409},
        space_id=h.state["space_id"],
        user_id=space_user_target,
        role_id=role_id,
    )
    if space_user_added:
        h.push_cleanup("remove space user", "space-users.remove", space_id=h.state["space_id"], user_id=space_user_target)
        h.run_tool("space-users.update", space_id=h.state["space_id"], user_id=space_user_target, role_id=role_id)
    else:
        h.run_tool_maybe(
            "space-users.update",
            expected_error_statuses={400, 403, 404, 409},
            space_id=h.state["space_id"],
            user_id=space_user_target,
            role_id=role_id,
        )
        h.run_tool_maybe("space-users.remove", expected_error_statuses={404}, space_id=h.state["space_id"], user_id=0)

    company_group = h.run_tool("company-groups.create", name=h.name("group"))
    h.state["company_group_uid"] = company_group["uid"]
    h.push_cleanup("delete company group", "company-groups.delete", group_uid=h.state["company_group_uid"])
    h.run_tool("company-groups.list", limit=10)
    h.run_tool("company-groups.get", group_uid=h.state["company_group_uid"])
    h.run_tool("company-groups.update", group_uid=h.state["company_group_uid"], name=h.name("group-updated"))
    h.run_tool("group-users.add", group_uid=h.state["company_group_uid"], user_id=h.state["current_user_id"])
    h.push_cleanup("remove group user", "group-users.remove", group_uid=h.state["company_group_uid"], user_id=h.state["current_user_id"])
    h.run_tool("group-users.list", group_uid=h.state["company_group_uid"], compact=True)

    card_types = h.run_tool("card-types.list", limit=10)
    replacement_type_id = next(item["id"] for item in card_types if item["id"])
    h.state["replacement_card_type_id"] = replacement_type_id
    h.run_tool("card-types.get", type_id=replacement_type_id)
    card_type = h.run_tool("card-types.create", name=h.name("type"), letter="L", color=2)
    h.state["card_type_id"] = card_type["id"]
    h.push_cleanup(
        "delete card type",
        "card-types.delete",
        type_id=h.state["card_type_id"],
        replace_type_id=replacement_type_id,
    )
    h.run_tool("card-types.get", type_id=h.state["card_type_id"])
    h.run_tool("card-types.update", type_id=h.state["card_type_id"], name=h.name("type-updated"))

    select_property = h.run_tool("custom-properties.create", name=h.name("prop-select"), type="select", colorful=True)
    h.state["select_property_id"] = select_property["id"]
    h.push_cleanup("delete select property", "custom-properties.delete", property_id=h.state["select_property_id"])
    h.run_tool("custom-properties.list", limit=10)
    h.run_tool("custom-properties.get", property_id=h.state["select_property_id"])
    h.run_tool("custom-properties.update", property_id=h.state["select_property_id"], name=h.name("prop-select-updated"))

    select_value = h.run_tool(
        "custom-properties.select-values.create",
        property_id=h.state["select_property_id"],
        value=h.name("value"),
        color=2,
    )
    h.state["select_value_id"] = select_value["id"]
    h.push_cleanup(
        "delete select value",
        "custom-properties.select-values.delete",
        property_id=h.state["select_property_id"],
        value_id=h.state["select_value_id"],
    )
    h.run_tool("custom-properties.select-values.list", property_id=h.state["select_property_id"], v2_select_search=True)
    h.run_tool("custom-properties.select-values.get", property_id=h.state["select_property_id"], value_id=h.state["select_value_id"])
    h.run_tool(
        "custom-properties.select-values.update",
        property_id=h.state["select_property_id"],
        value_id=h.state["select_value_id"],
        value=h.name("value-updated"),
    )


def _exercise_integrations(h) -> None:
    webhook = h.run_tool("webhooks.create", space_id=h.state["space_id"], url="https://example.com/live-webhook")
    webhook_id = webhook["id"]
    h.run_tool("webhooks.list", space_id=h.state["space_id"])
    h.run_tool("webhooks.update", space_id=h.state["space_id"], webhook_id=webhook_id, enabled=False)
    h.run_tool_maybe("webhooks.get", expected_error_statuses={404, 405}, space_id=h.state["space_id"], webhook_id=webhook_id)
    h.run_tool_maybe("webhooks.delete", expected_error_statuses={404, 405}, space_id=h.state["space_id"], webhook_id=webhook_id)

    incoming_webhook = h.run_tool(
        "incoming-webhooks.create",
        space_id=h.state["space_id"],
        board_id=h.state["board_id"],
        column_id=h.state["queue_column_id"],
        lane_id=h.state["lane_id"],
        owner_id=h.state["current_user_id"],
        format=1,
    )
    incoming_webhook_id = incoming_webhook["id"]
    h.run_tool("incoming-webhooks.list", space_id=h.state["space_id"])
    h.run_tool(
        "incoming-webhooks.update",
        space_id=h.state["space_id"],
        webhook_id=incoming_webhook_id,
        position=1,
        format=2,
    )
    h.run_tool("incoming-webhooks.delete", space_id=h.state["space_id"], webhook_id=incoming_webhook_id)

    automation_created, automation_payload = h.run_tool_maybe(
        "automations.create",
        expected_error_statuses={400, 403, 405},
        space_id=h.state["space_id"],
        name=h.name("automation"),
        type="on_action",
        trigger={"type": "card_created"},
        actions=_automation_actions(h.state["current_user_id"]),
    )
    h.run_tool("automations.list", space_id=h.state["space_id"])
    if automation_created:
        automation_id = automation_payload["id"]
        h.push_cleanup("delete automation", "automations.delete", space_id=h.state["space_id"], automation_id=automation_id)
        h.run_tool_maybe("automations.get", expected_error_statuses={405}, space_id=h.state["space_id"], automation_id=automation_id)
        h.run_tool(
            "automations.update",
            space_id=h.state["space_id"],
            automation_id=automation_id,
            name=h.name("automation-updated"),
        )
        copied, copied_payload = h.run_tool_maybe(
            "automations.copy",
            expected_error_statuses={400, 403, 404, 405},
            space_id=h.state["space_id"],
            automation_id=automation_id,
            target_space_id=h.state["secondary_space_id"],
        )
        if copied and isinstance(copied_payload, dict) and "id" in copied_payload:
            h.push_cleanup(
                "delete copied automation",
                "automations.delete",
                space_id=h.state["secondary_space_id"],
                automation_id=copied_payload["id"],
            )
    else:
        sentinel_automation_id = "00000000-0000-0000-0000-000000000000"
        h.run_tool_expect_api_error("automations.get", {404, 405}, space_id=h.state["space_id"], automation_id=sentinel_automation_id)
        h.run_tool_expect_api_error(
            "automations.update",
            {400, 404, 405},
            space_id=h.state["space_id"],
            automation_id=sentinel_automation_id,
            status="disabled",
        )
        h.run_tool_expect_api_error(
            "automations.delete",
            {404, 405},
            space_id=h.state["space_id"],
            automation_id=sentinel_automation_id,
        )
        h.run_tool_expect_api_error(
            "automations.copy",
            {400, 404, 405},
            space_id=h.state["space_id"],
            automation_id=sentinel_automation_id,
            target_space_id=h.state["secondary_space_id"],
        )

    workflow_created, workflow_data = h.run_tool_maybe(
        "workflows.create",
        expected_error_statuses={403, 405},
        name=h.name("workflow"),
        stages=[
            {
                "id": f"{h.run_id}-stage-1",
                "name": "Queue",
                "type": "queue",
                "position_data": {"x": 0, "y": 0},
            },
            {
                "id": f"{h.run_id}-stage-2",
                "name": "Done",
                "type": "done",
                "position_data": {"x": 240, "y": 0},
            },
        ],
        transitions=[
            {
                "id": f"{h.run_id}-transition-1",
                "prev_stage_id": f"{h.run_id}-stage-1",
                "next_stage_id": f"{h.run_id}-stage-2",
                "position_data": {"sourceHandle": "r", "targetHandle": "l"},
            }
        ],
    )
    h.run_tool("workflows.list", limit=10)
    if workflow_created:
        workflow_id = workflow_data["id"]
        h.push_cleanup("delete workflow", "workflows.delete", workflow_id=workflow_id)
        h.run_tool("workflows.get", workflow_id=workflow_id)
        h.run_tool("workflows.update", workflow_id=workflow_id, name=h.name("workflow-updated"))
    else:
        h.run_tool_expect_api_error("workflows.get", {403, 404, 405}, workflow_id="00000000-0000-0000-0000-000000000000")
        h.run_tool_expect_api_error(
            "workflows.update",
            {403, 404, 405},
            workflow_id="00000000-0000-0000-0000-000000000000",
            name="noop",
        )
        h.run_tool_expect_api_error("workflows.delete", {403, 404, 405}, workflow_id="00000000-0000-0000-0000-000000000000")


def _exercise_service_desk(h) -> None:
    h.run_tool("service-desk.settings.get")
    current_settings = h.run_tool("service-desk.settings.get")
    h.run_tool("service-desk.settings.update", service_desk_settings=current_settings)

    h.run_tool("service-desk.users.list", limit=10, include_paid_users=True, include_all_sd_users=True)

    sd_user_updated, sd_user_payload = h.run_tool_maybe(
        "service-desk.users.update",
        expected_error_statuses={400, 403, 404, 405},
        user_id=h.state["current_user_id"],
        full_name=h.state["current_user_full_name"],
    )
    h.run_tool_maybe(
        "service-desk.users.set-temp-password",
        expected_error_statuses={403, 404, 405},
        user_id=h.state["current_user_id"],
    )

    organization = h.run_tool("service-desk.organizations.create", name=h.name("sd-org"), description="live sd org")
    organization_id = organization["id"]
    h.push_cleanup("delete service-desk organization", "service-desk.organizations.delete", organization_id=organization_id)
    h.run_tool("service-desk.organizations.list", limit=10)
    h.run_tool("service-desk.organizations.get", organization_id=organization_id)
    h.run_tool("service-desk.organizations.update", organization_id=organization_id, name=h.name("sd-org-updated"))

    org_user_target = h.state["other_user_id"] or h.state["current_user_id"]
    org_user_added, _ = h.run_tool_maybe(
        "service-desk.organization-users.add",
        expected_error_statuses={400, 404, 409},
        organization_id=organization_id,
        user_id=org_user_target,
        permissions=1,
    )
    if org_user_added:
        h.run_tool_maybe(
            "service-desk.organization-users.update",
            expected_error_statuses={400, 403, 404, 405},
            organization_id=organization_id,
            user_id=org_user_target,
            permissions=7,
        )
        h.run_tool("service-desk.organization-users.remove", organization_id=organization_id, user_id=org_user_target)
        h.run_tool("service-desk.organization-users.batch-add", organization_id=organization_id, user_ids=[org_user_target])
        h.push_cleanup("batch-remove org users", "service-desk.organization-users.batch-remove", organization_id=organization_id, user_ids=[org_user_target])
    else:
        h.run_tool_expect_api_error("service-desk.organization-users.update", {403, 404, 405}, organization_id=organization_id, user_id=0, permissions=1)
        h.run_tool_expect_api_error("service-desk.organization-users.remove", {403, 404, 405}, organization_id=organization_id, user_id=0)
        h.run_tool_expect_api_error("service-desk.organization-users.batch-add", {403, 404, 405}, organization_id=organization_id, user_ids=[0])
        h.run_tool_expect_api_error("service-desk.organization-users.batch-remove", {403, 404, 405}, organization_id=organization_id, user_ids=[0])

    service = h.run_tool(
        "service-desk.services.create",
        name=h.name("sd-service"),
        board_id=h.state["board_id"],
        position=1,
        lng="en",
        column_id=h.state["queue_column_id"],
        lane_id=h.state["lane_id"],
    )
    service_id = service["id"]
    h.push_cleanup("archive service-desk service", "service-desk.services.delete", service_id=service_id)
    h.run_tool("service-desk.services.list", limit=10, include_archived=True)
    h.run_tool("service-desk.services.get", service_id=service_id)
    h.run_tool("service-desk.services.update", service_id=service_id, description="live sd service updated")

    sla = h.run_tool("service-desk.sla.create", name=h.name("sd-sla"), rules=[{"time": 3600}])
    sla_id = sla["id"]
    h.push_cleanup("delete service-desk sla", "service-desk.sla.delete", sla_id=sla_id)
    h.run_tool("service-desk.sla.list", limit=10)
    h.run_tool("service-desk.sla.get", sla_id=sla_id)
    h.run_tool("service-desk.sla.update", sla_id=sla_id, name=h.name("sd-sla-updated"))

    sla_rule_created, sla_rule_data = h.run_tool_maybe(
        "service-desk.sla-rules.create",
        expected_error_statuses={400, 403, 404, 405},
        sla_id=sla_id,
        type="response",
        estimated_time=120,
    )
    if sla_rule_created:
        rule_id = sla_rule_data["id"]
        h.push_cleanup("delete sla rule", "service-desk.sla-rules.delete", sla_id=sla_id, rule_id=rule_id)
        h.run_tool("service-desk.sla-rules.update", sla_id=sla_id, rule_id=rule_id, estimated_time=240)
    else:
        h.run_tool_expect_api_error("service-desk.sla-rules.update", {400, 403, 404, 405}, sla_id=sla_id, rule_id="missing", estimated_time=1)
        h.run_tool_expect_api_error("service-desk.sla-rules.delete", {400, 403, 404, 405}, sla_id=sla_id, rule_id="missing")

    h.run_tool("service-desk.sla.recalculate", sla_id=sla_id)

    template_answer = h.run_tool("service-desk.template-answers.create", name=h.name("sd-template"), text="Hello from live suite")
    template_answer_id = template_answer["id"]
    h.push_cleanup("delete template answer", "service-desk.template-answers.delete", template_answer_id=template_answer_id)
    h.run_tool("service-desk.template-answers.list")
    h.run_tool("service-desk.template-answers.get", template_answer_id=template_answer_id)
    h.run_tool("service-desk.template-answers.update", template_answer_id=template_answer_id, text="Updated")

    h.run_tool("service-desk.stats.get", date_from=_iso_date(-30), date_to=_iso_date(1), service_id=service_id)
    h.run_tool("service-desk.sla.stats", date_from=_iso_date(-30), date_to=_iso_date(1), service_id=service_id, sla_id=sla_id)

    h.run_tool("card-slas.attach", card_id=h.state["parent_card_id"], sla_id=sla_id)
    h.push_cleanup("detach card sla", "card-slas.detach", card_id=h.state["parent_card_id"], sla_id=sla_id)
    h.run_tool("card-sla-measurements.get", card_id=h.state["parent_card_id"])
    h.run_tool("space-sla-measurements.get", space_id=h.state["space_id"])

    h.run_tool("service-desk.vote-properties.add", service_id=service_id, id=h.state["select_property_id"])
    h.push_cleanup("remove vote property", "service-desk.vote-properties.remove", service_id=service_id, property_id=h.state["select_property_id"])

    h.run_tool("service-desk.requests.list", limit=10)
    request_created, request_data = h.run_tool_maybe(
        "service-desk.requests.create",
        expected_error_statuses={400, 403, 404, 405},
        title=h.name("sd-request"),
        service_id=service_id,
        description="live request",
    )
    if request_created:
        request_id = request_data["id"]
        h.push_cleanup("delete service request", "service-desk.requests.delete", request_id=request_id)
        h.run_tool("service-desk.requests.get", request_id=request_id)
        h.run_tool("service-desk.requests.update", request_id=request_id, priority="high")
    else:
        h.run_tool_expect_api_error("service-desk.requests.get", {403, 404, 405}, request_id=0)
        h.run_tool_expect_api_error("service-desk.requests.update", {403, 404, 405}, request_id=0, priority="low")
        h.run_tool_expect_api_error("service-desk.requests.delete", {403, 404, 405}, request_id=0)


def _exercise_analytics_and_jobs(h) -> None:
    h.run_tool("audit-logs.list", limit=5)
    h.run_tool("company-activity.get", limit=5, compact=True)
    h.run_tool("space-activity.get", space_id=h.state["space_id"], limit=5, compact=True)
    h.run_tool("space-activity-all.get", space_id=h.state["space_id"], page_size=5, max_pages=1, compact=True)
    h.run_tool("card-activity.get", card_id=h.state["parent_card_id"], limit=5)
    h.run_tool("card-location-history.get", card_id=h.state["parent_card_id"])

    saved_filter = h.run_tool(
        "saved-filters.create",
        name=h.name("filter"),
        filter={"board_id": h.state["board_id"]},
        shared=False,
    )
    saved_filter_id = saved_filter["id"]
    h.push_cleanup("delete saved filter", "saved-filters.delete", filter_id=saved_filter_id)
    h.run_tool("saved-filters.list", limit=10)
    h.run_tool("saved-filters.get", filter_id=saved_filter_id)
    h.run_tool("saved-filters.update", filter_id=saved_filter_id, name=h.name("filter-updated"))

    h.run_tool("charts.boards.get", space_id=h.state["space_id"])
    h.run_tool(
        "charts.summary.get",
        space_id=h.state["space_id"],
        date_from=_iso_date(-30),
        date_to=_iso_date(1),
        done_columns=[h.state["done_column_id"]],
    )
    h.run_tool("charts.block-resolution.get", space_id=h.state["space_id"])
    h.run_tool(
        "charts.due-dates.get",
        space_id=h.state["space_id"],
        card_date_from=_iso_date(-30),
        card_date_to=_iso_date(1),
        checklist_item_date_from=_iso_date(-30),
        checklist_item_date_to=_iso_date(1),
    )

    cfd_job = h.run_tool(
        "charts.cfd.create",
        space_id=h.state["space_id"],
        date_from=_iso_date(-30),
        date_to=_iso_date(1),
        selectedLanes=[h.state["lane_id"]],
    )
    compute_job_id = cfd_job["compute_job_id"]
    h.run_tool("compute-jobs.get", job_id=compute_job_id)
    h.run_tool_maybe("compute-jobs.cancel", expected_error_statuses={400, 404, 409}, job_id=compute_job_id)

    shared_control_kwargs = {
        "space_id": h.state["space_id"],
        "date_from": _iso_date(-30),
        "date_to": _iso_date(1),
        "start_columns": [h.state["queue_column_id"]],
        "end_columns": [h.state["done_column_id"]],
        "start_column_lanes": {str(h.state["queue_column_id"]): [h.state["lane_id"]]},
        "end_column_lanes": {str(h.state["done_column_id"]): [h.state["lane_id"]]},
    }
    h.run_tool("charts.control.create", **shared_control_kwargs)
    h.run_tool("charts.spectral.create", **shared_control_kwargs)
    h.run_tool("charts.lead-time.create", **shared_control_kwargs)
    h.run_tool(
        "charts.throughput-capacity.create",
        space_id=h.state["space_id"],
        date_from=_iso_date(-30),
        date_to=_iso_date(1),
        end_column=h.state["done_column_id"],
    )
    h.run_tool(
        "charts.throughput-demand.create",
        space_id=h.state["space_id"],
        date_from=_iso_date(-30),
        date_to=_iso_date(1),
        start_column=h.state["queue_column_id"],
    )
    h.run_tool(
        "charts.task-distribution.create",
        space_id=h.state["space_id"],
        includeArchivedCards=False,
        timezone="Europe/Moscow",
    )
    h.run_tool(
        "charts.cycle-time.create",
        space_id=h.state["space_id"],
        date_from=_iso_date(-30),
        date_to=_iso_date(1),
        start_column=h.state["queue_column_id"],
        end_column=h.state["done_column_id"],
    )
    h.run_tool(
        "charts.sales-funnel.create",
        space_id=h.state["space_id"],
        date_from=_iso_date(-30),
        date_to=_iso_date(1),
        board_configs=[
            {
                "board_id": h.state["board_id"],
                "enabled": True,
                "columns": [
                    {"column_id": h.state["queue_column_id"], "enabled": True, "funnel_type": "stage"},
                    {"column_id": h.state["done_column_id"], "enabled": True, "funnel_type": "won"},
                ],
            }
        ],
    )


def _exercise_utilities_tail(h) -> None:
    h.run_tool("api-keys.list")

    timer_list_ok, timer_list_payload = h.run_tool_maybe("user-timers.list", expected_error_statuses={403, 405})
    if timer_list_ok:
        timer_created, timer_payload = h.run_tool_maybe(
            "user-timers.create",
            expected_error_statuses={400, 403, 405, 409},
            card_id=h.state["parent_card_id"],
        )
        if timer_created:
            timer_id = timer_payload["id"]
            h.push_cleanup("delete user timer", "user-timers.delete", timer_id=timer_id)
            h.run_tool("user-timers.get", timer_id=timer_id)
            h.run_tool("user-timers.update", timer_id=timer_id, paused=True)
        else:
            h.run_tool_expect_api_error("user-timers.get", {403, 404, 405}, timer_id=0)
            h.run_tool_expect_api_error("user-timers.update", {403, 404, 405}, timer_id=0, paused=True)
            h.run_tool_expect_api_error("user-timers.delete", {403, 404, 405}, timer_id=0)
    else:
        h.run_tool_expect_api_error("user-timers.create", {403, 405}, card_id=h.state["parent_card_id"])
        h.run_tool_expect_api_error("user-timers.get", {403, 404, 405}, timer_id=0)
        h.run_tool_expect_api_error("user-timers.update", {403, 404, 405}, timer_id=0, paused=True)
        h.run_tool_expect_api_error("user-timers.delete", {403, 404, 405}, timer_id=0)


@pytest.mark.live
@pytest.mark.full_live_coverage
@pytest.mark.timeout(1800)
def test_sandbox_full_live_sequential(live_harness):
    h = live_harness

    _exercise_foundation(h)
    _exercise_card_adjacent(h)
    _exercise_projects_documents_and_tree(h)
    _exercise_company_metadata(h)
    _exercise_integrations(h)
    _exercise_service_desk(h)
    _exercise_analytics_and_jobs(h)
    _exercise_utilities_tail(h)
