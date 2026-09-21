"""Small compatibility validators for alternate documented request forms."""

from kaiten_cli.errors import ValidationError


def validate_public_request(tool, payload):
    name = tool.canonical_name
    alternatives = {
        "space-users.add": [("email",), ("user_id",)],
        "blocker-categories.add": [("name",), ("category_uuid",)],
        "custom-properties.create": [("name", "type"), ("formula", "formula_source_card")],
        "custom-properties.collective-vote-values.create": [
            ("value",),
            ("emoji_vote",),
            ("number_vote",),
            ("payload",),
        ],
    }
    if name in alternatives:
        if not any(all(field in payload for field in fields) for fields in alternatives[name]):
            choices = " or ".join(" + ".join(fields) for fields in alternatives[name])
            raise ValidationError(f"Missing required input: {choices}.")
    if name.startswith("private-") and payload.get("redirect") is True:
        raise ValidationError(
            "Field redirect=true returns binary/redirect content instead of JSON metadata. Use files.download to download restricted files safely."
        )
