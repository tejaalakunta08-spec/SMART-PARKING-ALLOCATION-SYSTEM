"""Constraint-satisfaction solver for smart parking allocation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from models import ParkingLot, Vehicle


@dataclass(frozen=True)
class Event:
    kind: str
    vehicle_id: int
    slot_id: int
    note: str


@dataclass
class SolveResult:
    assignment: Dict[int, int]
    unassigned: List[int]
    total_distance: int
    backtracks: int
    steps: List[str]
    events: List[Event] = field(default_factory=list)


def _initial_domains(vehicles: List[Vehicle], lot: ParkingLot) -> Dict[int, List[int]]:
    domains: Dict[int, List[int]] = {}
    for vehicle in vehicles:
        compatible = [slot for slot in lot.slots if slot.size >= vehicle.size]
        compatible.sort(key=lambda slot: (slot.distance, slot.id))
        domains[vehicle.id] = [slot.id for slot in compatible]
    return domains


def _order_vehicles(vehicles: List[Vehicle]) -> List[Vehicle]:
    return sorted(vehicles, key=lambda item: (item.priority, -item.size, item.id))


def _pick_next(remaining: List[Vehicle], domains: Dict[int, List[int]]) -> Vehicle:
    highest_priority = remaining[0].priority
    candidates = [item for item in remaining if item.priority == highest_priority]
    return min(candidates, key=lambda item: (len(domains[item.id]), -item.size, item.id))


def solve(vehicles: List[Vehicle], lot: ParkingLot) -> SolveResult:
    """Assign vehicles to slots using size, exclusivity, and priority rules."""

    steps: List[str] = []
    events: List[Event] = []
    assignment: Dict[int, int] = {}
    backtracks = 0

    ordered = _order_vehicles(vehicles)
    domains = _initial_domains(ordered, lot)
    queue = [vehicle for vehicle in ordered if domains[vehicle.id]]

    for vehicle in ordered:
        if not domains[vehicle.id]:
            steps.append(f"{vehicle.plate}: no compatible slot exists.")

    def backtrack(remaining: List[Vehicle], current_domains: Dict[int, List[int]]) -> bool:
        nonlocal backtracks
        if not remaining:
            return True

        vehicle = _pick_next(remaining, current_domains)
        rest = [item for item in remaining if item.id != vehicle.id]

        for slot_id in list(current_domains[vehicle.id]):
            slot = lot.slot_by_id(slot_id)
            note = (
                f"{vehicle.plate} ({vehicle.vtype.label_text}, {vehicle.priority.label()}) "
                f"to slot #{slot.id} ({slot.label()}, distance {slot.distance})"
            )
            steps.append(f"Try {note}")
            events.append(Event("try", vehicle.id, slot_id, note))
            assignment[vehicle.id] = slot_id

            pruned: List[Tuple[int, int]] = []
            dead_end = False
            for other in rest:
                if slot_id in current_domains[other.id]:
                    current_domains[other.id].remove(slot_id)
                    pruned.append((other.id, slot_id))
                    if not current_domains[other.id]:
                        dead_end = True

            if not dead_end and backtrack(rest, current_domains):
                return True

            for vehicle_id, removed_slot_id in pruned:
                current_domains[vehicle_id].append(removed_slot_id)
                current_domains[vehicle_id].sort(
                    key=lambda sid: (lot.slot_by_id(sid).distance, sid)
                )
            assignment.pop(vehicle.id, None)
            backtracks += 1
            steps.append(f"Backtrack {vehicle.plate} from slot #{slot_id}")
            events.append(Event("backtrack", vehicle.id, slot_id, f"Undo {vehicle.plate}"))

        return False

    backtrack(queue, domains)

    total_distance = sum(lot.slot_by_id(slot_id).distance for slot_id in assignment.values())
    unassigned = [vehicle.id for vehicle in vehicles if vehicle.id not in assignment]

    return SolveResult(
        assignment=assignment,
        unassigned=unassigned,
        total_distance=total_distance,
        backtracks=backtracks,
        steps=steps,
        events=events,
    )
