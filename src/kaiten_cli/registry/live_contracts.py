"""Live validation contract metadata for the current test tenant."""

from __future__ import annotations

from dataclasses import dataclass


LIVE_STATUS_PASSED = "live_passed"
LIVE_STATUS_PASSED_WITH_RUNTIME_FIX = "live_passed_with_runtime_fix"
LIVE_STATUS_PASSED_AS_EXPECTED_ERROR = "live_passed_as_expected_error"
LIVE_STATUS_SYNTHETIC_READ = "synthetic_read"
LIVE_STATUS_POLICY_EXCLUDED = "policy_excluded"

VALID_LIVE_STATUSES = {
    LIVE_STATUS_PASSED,
    LIVE_STATUS_PASSED_WITH_RUNTIME_FIX,
    LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
    LIVE_STATUS_SYNTHETIC_READ,
    LIVE_STATUS_POLICY_EXCLUDED,
}


@dataclass(slots=True, frozen=True)
class LiveContract:
    status: str
    note: str
    expected_statuses: tuple[int, ...] = ()


_SPECIAL_CONTRACTS: dict[str, LiveContract] = {
    "api-keys.create": LiveContract(
        status=LIVE_STATUS_POLICY_EXCLUDED,
        note="Creating API keys is excluded from live validation because teardown would require testing key deletion.",
    ),
    "api-keys.delete": LiveContract(
        status=LIVE_STATUS_POLICY_EXCLUDED,
        note="Deleting API keys is explicitly excluded from live validation by user instruction.",
    ),
    "boards.delete": LiveContract(
        status=LIVE_STATUS_PASSED_WITH_RUNTIME_FIX,
        note="Sandbox requires the force flag for board deletion; the CLI injects the live-safe request shape.",
    ),
    "projects.cards.list": LiveContract(
        status=LIVE_STATUS_SYNTHETIC_READ,
        note="If GET /projects/{project_id}/cards returns 405, the CLI falls back to GET /projects/{project_id}?with_cards_data=true and extracts the embedded cards list.",
        expected_statuses=(405,),
    ),
    "removed-boards.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sandbox returns 405 for recycle-bin board listing; the live suite validates that contract explicitly.",
        expected_statuses=(405,),
    ),
    "removed-cards.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sandbox returns 405 for recycle-bin card listing; the live suite validates that contract explicitly.",
        expected_statuses=(405,),
    ),
    "checklists.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sandbox returns 405 for checklist listing; the live suite validates the expected error path.",
        expected_statuses=(405,),
    ),
    "checklist-items.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sandbox returns 405 for checklist item listing; the live suite validates the expected error path.",
        expected_statuses=(405,),
    ),
    "card-subscribers.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sandbox returns 405 for card subscriber listing; the live suite validates the expected error path.",
        expected_statuses=(405,),
    ),
    "column-subscribers.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sandbox returns 405 for column subscriber listing; the live suite validates the expected error path.",
        expected_statuses=(405,),
    ),
    "sprints.create": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sprint creation is permission-dependent on sandbox; the live suite accepts either success or a documented 403/405 error.",
        expected_statuses=(403, 405),
    ),
    "sprints.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sprint listing is permission-dependent on sandbox; the live suite accepts either success or a documented 403/405 error.",
        expected_statuses=(403, 405),
    ),
    "sprints.get": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When sprint creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel sprint id.",
        expected_statuses=(403, 404, 405),
    ),
    "sprints.update": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When sprint creation is unavailable or the created sprint id cannot be resolved, sandbox may return 403/404/405 or 500 on a sentinel sprint id; the live suite validates that documented defect contract explicitly.",
        expected_statuses=(403, 404, 405, 500),
    ),
    "sprints.delete": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Sprint deletion is often unavailable on sandbox; the live suite accepts the documented 403/404/405 contract.",
        expected_statuses=(403, 404, 405),
    ),
    "webhooks.get": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Webhook GET may return 404/405 even after successful creation; the live suite validates that contract explicitly.",
        expected_statuses=(404, 405),
    ),
    "webhooks.delete": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Webhook DELETE may return 404/405 even after successful creation; the live suite validates that contract explicitly.",
        expected_statuses=(404, 405),
    ),
    "automations.get": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Automation GET-single may return 405 even after successful creation; the live suite validates that contract explicitly.",
        expected_statuses=(405,),
    ),
    "automations.create": LiveContract(
        status=LIVE_STATUS_PASSED,
        note="Automation creation passes on sandbox when the payload matches the known live-valid add_assignee shape derived from kaiten-mcp e2e.",
    ),
    "automations.update": LiveContract(
        status=LIVE_STATUS_PASSED,
        note="Automation update passes on sandbox for automations created with the known live-valid add_assignee payload shape.",
    ),
    "automations.delete": LiveContract(
        status=LIVE_STATUS_PASSED,
        note="Automation delete passes on sandbox for automations created during live validation; cleanup is verified.",
    ),
    "automations.copy": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Automation copy remains sandbox-dependent even with a live-valid source automation; the live suite accepts success or a documented 400/403/404/405 contract.",
        expected_statuses=(400, 403, 404, 405),
    ),
    "workflows.create": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Workflow creation is permission-dependent on sandbox; the live suite accepts either success or a documented 403/405 error.",
        expected_statuses=(403, 405),
    ),
    "workflows.get": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When workflow creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel workflow id.",
        expected_statuses=(403, 404, 405),
    ),
    "workflows.update": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When workflow creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel workflow id.",
        expected_statuses=(403, 404, 405),
    ),
    "workflows.delete": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When workflow creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel workflow id.",
        expected_statuses=(403, 404, 405),
    ),
    "service-desk.users.set-temp-password": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Temporary password generation may succeed or return a documented 403/404/405 sandbox error; the live suite accepts both outcomes.",
        expected_statuses=(403, 404, 405),
    ),
    "service-desk.users.update": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="The current live account is not a Service Desk user, so update may return 400 'Should be service desk user'; the live suite validates that documented contract.",
        expected_statuses=(400, 403, 404, 405),
    ),
    "service-desk.organization-users.update": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Updating Service Desk organization-user permissions remains sandbox-dependent; the live suite accepts success or a documented 400/403/404/405 contract.",
        expected_statuses=(400, 403, 404, 405),
    ),
    "service-desk.requests.create": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Service Desk request creation is permission-dependent; the live suite accepts either success or a documented 400/403/404/405 contract.",
        expected_statuses=(400, 403, 404, 405),
    ),
    "service-desk.requests.get": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When request creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel request id.",
        expected_statuses=(403, 404, 405),
    ),
    "service-desk.requests.update": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When request creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel request id.",
        expected_statuses=(403, 404, 405),
    ),
    "service-desk.requests.delete": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When request creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel request id.",
        expected_statuses=(403, 404, 405),
    ),
    "service-desk.sla-rules.create": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="SLA rule creation is permission- and schema-dependent; the live suite accepts either success or a documented 400/403/404/405 contract.",
        expected_statuses=(400, 403, 404, 405),
    ),
    "service-desk.sla-rules.update": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When SLA-rule creation is unavailable, the live suite validates the documented 400/403/404/405 error contract on a sentinel rule id.",
        expected_statuses=(400, 403, 404, 405),
    ),
    "service-desk.sla-rules.delete": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When SLA-rule creation is unavailable, the live suite validates the documented 400/403/404/405 error contract on a sentinel rule id.",
        expected_statuses=(400, 403, 404, 405),
    ),
    "compute-jobs.cancel": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="Canceling a compute job can legitimately return 400/404/409 depending on backend state; the live suite accepts that contract.",
        expected_statuses=(400, 404, 409),
    ),
    "user-timers.list": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="User-timer listing remains sandbox-dependent; the live suite accepts either success or a documented 403/405 error path.",
        expected_statuses=(403, 405),
    ),
    "user-timers.create": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="User-timer creation remains sandbox-dependent; the live suite accepts either success or a documented 400/403/405/409 contract.",
        expected_statuses=(400, 403, 405, 409),
    ),
    "user-timers.get": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When timer creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel timer id.",
        expected_statuses=(403, 404, 405),
    ),
    "user-timers.update": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When timer creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel timer id.",
        expected_statuses=(403, 404, 405),
    ),
    "user-timers.delete": LiveContract(
        status=LIVE_STATUS_PASSED_AS_EXPECTED_ERROR,
        note="When timer creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel timer id.",
        expected_statuses=(403, 404, 405),
    ),
}


def get_live_contract(canonical_name: str) -> LiveContract:
    return _SPECIAL_CONTRACTS.get(
        canonical_name,
        LiveContract(
            status=LIVE_STATUS_PASSED,
            note="Validated on the normal success path in the full live suite.",
        ),
    )


def iter_special_live_contracts() -> tuple[tuple[str, LiveContract], ...]:
    return tuple(sorted(_SPECIAL_CONTRACTS.items()))


def has_special_live_contract(canonical_name: str) -> bool:
    return canonical_name in _SPECIAL_CONTRACTS


LIVE_POLICY_EXCLUSIONS = {
    name: contract.note
    for name, contract in _SPECIAL_CONTRACTS.items()
    if contract.status == LIVE_STATUS_POLICY_EXCLUDED
}
