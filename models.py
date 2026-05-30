"""Domain models for the Smart Parking Allocation project."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List


class Size(IntEnum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

    def label(self) -> str:
        return {
            Size.SMALL: "Bike bay",
            Size.MEDIUM: "Car bay",
            Size.LARGE: "Large bay",
        }[self]


class VehicleType(Enum):
    BIKE = ("Bike", Size.SMALL)
    CAR = ("Car", Size.MEDIUM)
    AMBULANCE = ("Ambulance", Size.LARGE)
    TRUCK = ("Truck", Size.LARGE)

    def __init__(self, label: str, size: Size) -> None:
        self.label_text = label
        self.size = size

    @classmethod
    def from_label(cls, label: str) -> "VehicleType":
        for item in cls:
            if item.label_text.lower() == label.lower():
                return item
        raise ValueError(f"Unknown vehicle type: {label}")


class Priority(IntEnum):
    HIGH = 1
    MEDIUM = 2
    NORMAL = 3

    @classmethod
    def from_label(cls, label: str) -> "Priority":
        normalized = label.strip().lower()
        return {
            "high": cls.HIGH,
            "medium": cls.MEDIUM,
            "normal": cls.NORMAL,
        }[normalized]

    def label(self) -> str:
        return self.name.capitalize()


@dataclass(frozen=True)
class Slot:
    id: int
    row: int
    col: int
    size: Size
    distance: int

    def label(self) -> str:
        return self.size.label()


@dataclass(frozen=True)
class Vehicle:
    id: int
    plate: str
    vtype: VehicleType
    priority: Priority

    @property
    def size(self) -> Size:
        return self.vtype.size


@dataclass
class ParkingLot:
    rows: int
    cols: int
    slots: List[Slot] = field(default_factory=list)

    def slot_by_id(self, slot_id: int) -> Slot:
        for slot in self.slots:
            if slot.id == slot_id:
                return slot
        raise KeyError(f"Unknown slot id: {slot_id}")


def build_sample_lot(rows: int = 4, cols: int = 6) -> ParkingLot:
    """Build a sample lot with bike, car, and large bays.

    The entrance is considered to be on the left side of the grid, so slots
    in earlier columns have shorter walking distances.
    """

    slots: List[Slot] = []
    slot_id = 1
    for row in range(rows):
        for col in range(cols):
            if col == 0:
                size = Size.SMALL
            elif col <= 2:
                size = Size.MEDIUM
            else:
                size = Size.LARGE

            distance = (col + 1) * 10 + row * 2
            slots.append(Slot(slot_id, row, col, size, distance))
            slot_id += 1

    return ParkingLot(rows=rows, cols=cols, slots=slots)
