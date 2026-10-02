from dataclasses import dataclass

IDENTITY_WEIGHTS = {
    "AGENT_ID": 100,
    "VM_UUID": 100,
    "AD_SID": 100,
    "BIOS_UUID": 95,
    "SERIAL_NUMBER": 90,
    "MACHINE_UUID": 90,
    "MAC_ADDRESS": 75,
    "HOSTNAME_DOMAIN": 70,
    "HOSTNAME": 50,
}


@dataclass(frozen=True)
class IdentityCandidate:
    identifier_type: str
    identifier_value: str
    asset_id: int
    weight: int


def normalize(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().lower()
    return value or None


def score_identifiers(observation: dict[str, str | None], existing: list[dict]) -> list[IdentityCandidate]:
    candidates: dict[int, IdentityCandidate] = {}
    for row in existing:
        value = normalize(row.get("identifier_value"))
        obs_value = normalize(observation.get(row.get("identifier_type", "")))
        if not value or value != obs_value:
            continue
        kind = row["identifier_type"]
        weight = IDENTITY_WEIGHTS.get(kind, 0)
        asset_id = int(row["asset_id"])
        current = candidates.get(asset_id)
        if current is None or weight > current.weight:
            candidates[asset_id] = IdentityCandidate(kind, value, asset_id, weight)
    return sorted(candidates.values(), key=lambda x: (-x.weight, x.asset_id))


def resolve_identity(observation: dict[str, str | None], existing: list[dict]) -> tuple[str, int | None, int]:
    candidates = score_identifiers(observation, existing)
    if not candidates:
        return "NEW", None, 0
    top = candidates[0]
    if len(candidates) > 1 and candidates[1].weight == top.weight and candidates[1].asset_id != top.asset_id:
        return "AMBIGUOUS", None, top.weight
    return "MATCHED", top.asset_id, top.weight
