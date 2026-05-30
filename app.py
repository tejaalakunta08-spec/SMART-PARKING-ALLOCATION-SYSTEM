"""Tkinter UI for the Smart Parking Allocation project.

Run:
    python app.py
"""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List, Optional

from csp_solver import SolveResult, solve
from models import ParkingLot, Priority, Size, Vehicle, VehicleType, build_sample_lot


SLOT_FILL = {
    Size.SMALL: "#eaf2ff",
    Size.MEDIUM: "#eaf7ea",
    Size.LARGE: "#fff2dc",
}
SLOT_STRIPE = {
    Size.SMALL: "#4d7ee8",
    Size.MEDIUM: "#3ca55c",
    Size.LARGE: "#d69125",
}
PRIORITY_COLOR = {
    Priority.HIGH: "#c0392b",
    Priority.MEDIUM: "#d68910",
    Priority.NORMAL: "#2874a6",
}
VEHICLE_COLOR = {
    VehicleType.BIKE: "#34495e",
    VehicleType.CAR: "#3498db",
    VehicleType.AMBULANCE: "#ffffff",
    VehicleType.TRUCK: "#7f8c8d",
}


def draw_vehicle(canvas: tk.Canvas, vehicle_type: VehicleType, x: float, y: float, w: float, h: float) -> None:
    color = VEHICLE_COLOR[vehicle_type]
    if vehicle_type == VehicleType.BIKE:
        wheel_y = y + h * 0.76
        radius = h * 0.13
        canvas.create_oval(x + w * 0.2 - radius, wheel_y - radius, x + w * 0.2 + radius, wheel_y + radius, fill="#222")
        canvas.create_oval(x + w * 0.8 - radius, wheel_y - radius, x + w * 0.8 + radius, wheel_y + radius, fill="#222")
        canvas.create_line(x + w * 0.2, wheel_y, x + w * 0.5, y + h * 0.45, x + w * 0.8, wheel_y, fill=color, width=3)
        canvas.create_line(x + w * 0.5, y + h * 0.45, x + w * 0.68, y + h * 0.32, fill=color, width=3)
        return

    if vehicle_type == VehicleType.CAR:
        canvas.create_polygon(
            x + w * 0.08,
            y + h * 0.7,
            x + w * 0.2,
            y + h * 0.48,
            x + w * 0.35,
            y + h * 0.34,
            x + w * 0.68,
            y + h * 0.34,
            x + w * 0.84,
            y + h * 0.5,
            x + w * 0.94,
            y + h * 0.7,
            fill=color,
            outline="#1f2d3d",
            width=2,
        )
    elif vehicle_type == VehicleType.AMBULANCE:
        canvas.create_rectangle(x + w * 0.08, y + h * 0.3, x + w * 0.62, y + h * 0.72, fill=color, outline="#1f2d3d", width=2)
        canvas.create_rectangle(x + w * 0.62, y + h * 0.42, x + w * 0.92, y + h * 0.72, fill=color, outline="#1f2d3d", width=2)
        cx, cy = x + w * 0.35, y + h * 0.51
        canvas.create_rectangle(cx - 4, cy - 15, cx + 4, cy + 15, fill="#d23a2a", outline="")
        canvas.create_rectangle(cx - 15, cy - 4, cx + 15, cy + 4, fill="#d23a2a", outline="")
    else:
        canvas.create_rectangle(x + w * 0.05, y + h * 0.3, x + w * 0.62, y + h * 0.72, fill="#8b6f47", outline="#1f2d3d", width=2)
        canvas.create_polygon(
            x + w * 0.62,
            y + h * 0.45,
            x + w * 0.72,
            y + h * 0.36,
            x + w * 0.92,
            y + h * 0.36,
            x + w * 0.96,
            y + h * 0.72,
            x + w * 0.62,
            y + h * 0.72,
            fill=color,
            outline="#1f2d3d",
            width=2,
        )

    wheel_y = y + h * 0.78
    radius = h * 0.1
    for frac in (0.25, 0.75):
        canvas.create_oval(x + w * frac - radius, wheel_y - radius, x + w * frac + radius, wheel_y + radius, fill="#222")


class ParkingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Smart Parking Allocation - CSP")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.lot: ParkingLot = build_sample_lot()
        self.vehicles: List[Vehicle] = []
        self.next_vehicle_id = 1
        self.assignment: Dict[int, int] = {}
        self.last_result: Optional[SolveResult] = None
        self.selected_vehicle_id: Optional[int] = None

        self._build_ui()
        self._load_sample()
        self._redraw()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self, padding=10)
        sidebar.grid(row=0, column=0, sticky="ns")
        main = ttk.Frame(self, padding=(0, 10, 10, 10))
        main.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        form = ttk.LabelFrame(sidebar, text="Add vehicle", padding=10)
        form.pack(fill="x")

        self.plate_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Car")
        self.priority_var = tk.StringVar(value="Normal")

        ttk.Label(form, text="Plate").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.plate_var, width=20).grid(row=0, column=1, pady=3)
        ttk.Label(form, text="Type").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Combobox(form, textvariable=self.type_var, values=[item.label_text for item in VehicleType], state="readonly", width=17).grid(row=1, column=1, pady=3)
        ttk.Label(form, text="Priority").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Combobox(form, textvariable=self.priority_var, values=["High", "Medium", "Normal"], state="readonly", width=17).grid(row=2, column=1, pady=3)
        ttk.Button(form, text="Add vehicle", command=self._add_vehicle).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        vehicle_box = ttk.LabelFrame(sidebar, text="Vehicles", padding=6)
        vehicle_box.pack(fill="both", expand=True, pady=8)
        self.vehicle_list = tk.Listbox(vehicle_box, height=16, width=34)
        self.vehicle_list.pack(fill="both", expand=True)
        self.vehicle_list.bind("<<ListboxSelect>>", self._select_vehicle)

        ttk.Button(sidebar, text="Remove selected", command=self._remove_selected).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Load sample", command=self._load_sample).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Random fill", command=self._random_fill).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Clear all", command=self._clear_all).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Solve parking", command=self._solve).pack(fill="x", pady=(10, 2))
        ttk.Button(sidebar, text="Reset assignment", command=self._reset_assignment).pack(fill="x", pady=2)

        self.canvas = tk.Canvas(main, bg="#fafbfc", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _event: self._redraw())

        bottom = ttk.Frame(main)
        bottom.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.status_var = tk.StringVar(value="Add vehicles and solve.")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left")

        self.stats_var = tk.StringVar(value="")
        ttk.Label(bottom, textvariable=self.stats_var, font=("Segoe UI", 10, "bold")).pack(side="right")

        trace_box = ttk.LabelFrame(main, text="Solver trace", padding=4)
        trace_box.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.trace = tk.Text(trace_box, height=7, wrap="word", font=("Consolas", 9))
        self.trace.pack(fill="both", expand=True)

    def _add_vehicle(self) -> None:
        plate = self.plate_var.get().strip().upper()
        if not plate:
            messagebox.showwarning("Missing plate", "Enter a vehicle plate number.")
            return

        self.vehicles.append(
            Vehicle(
                id=self.next_vehicle_id,
                plate=plate,
                vtype=VehicleType.from_label(self.type_var.get()),
                priority=Priority.from_label(self.priority_var.get()),
            )
        )
        self.next_vehicle_id += 1
        self.plate_var.set("")
        self._reset_assignment()
        self._refresh_vehicle_list()

    def _select_vehicle(self, _event: object) -> None:
        selected = self.vehicle_list.curselection()
        self.selected_vehicle_id = self.vehicles[selected[0]].id if selected else None

    def _remove_selected(self) -> None:
        if self.selected_vehicle_id is None:
            return
        self.vehicles = [item for item in self.vehicles if item.id != self.selected_vehicle_id]
        self.selected_vehicle_id = None
        self._reset_assignment()
        self._refresh_vehicle_list()

    def _clear_all(self) -> None:
        self.vehicles.clear()
        self.selected_vehicle_id = None
        self.next_vehicle_id = 1
        self._reset_assignment()
        self._refresh_vehicle_list()

    def _load_sample(self) -> None:
        sample = [
            ("AMB-101", VehicleType.AMBULANCE, Priority.HIGH),
            ("VIP-002", VehicleType.CAR, Priority.HIGH),
            ("STF-221", VehicleType.CAR, Priority.MEDIUM),
            ("STF-222", VehicleType.BIKE, Priority.MEDIUM),
            ("DLV-440", VehicleType.TRUCK, Priority.MEDIUM),
            ("CAR-501", VehicleType.CAR, Priority.NORMAL),
            ("CAR-502", VehicleType.CAR, Priority.NORMAL),
            ("BIK-601", VehicleType.BIKE, Priority.NORMAL),
            ("BIK-602", VehicleType.BIKE, Priority.NORMAL),
            ("TRK-701", VehicleType.TRUCK, Priority.NORMAL),
        ]
        self.vehicles = [Vehicle(index + 1, plate, vtype, priority) for index, (plate, vtype, priority) in enumerate(sample)]
        self.next_vehicle_id = len(self.vehicles) + 1
        self.selected_vehicle_id = None
        self._reset_assignment()
        self._refresh_vehicle_list()

    def _random_fill(self) -> None:
        prefixes = {
            VehicleType.BIKE: "BIK",
            VehicleType.CAR: "CAR",
            VehicleType.AMBULANCE: "AMB",
            VehicleType.TRUCK: "TRK",
        }
        self.vehicles.clear()
        for index in range(18):
            vtype = random.choices(list(VehicleType), weights=[3, 5, 1, 2], k=1)[0]
            priority = Priority.HIGH if vtype == VehicleType.AMBULANCE else random.choices(list(Priority), weights=[1, 2, 5], k=1)[0]
            plate = f"{prefixes[vtype]}-{random.randint(100, 999)}"
            self.vehicles.append(Vehicle(index + 1, plate, vtype, priority))
        self.next_vehicle_id = len(self.vehicles) + 1
        self._reset_assignment()
        self._refresh_vehicle_list()

    def _solve(self) -> None:
        if not self.vehicles:
            messagebox.showinfo("No vehicles", "Add vehicles before solving.")
            return

        result = solve(self.vehicles, self.lot)
        self.last_result = result
        self.assignment = dict(result.assignment)
        self.status_var.set(
            f"Assigned {len(result.assignment)} of {len(self.vehicles)} vehicles. "
            f"Unassigned: {len(result.unassigned)}."
        )
        self.stats_var.set(f"Total distance: {result.total_distance} | Backtracks: {result.backtracks}")
        self._set_trace(result.steps)
        self._redraw()

    def _reset_assignment(self) -> None:
        self.assignment.clear()
        self.last_result = None
        self.status_var.set("Add vehicles and solve.")
        self.stats_var.set("")
        self._set_trace([])
        self._redraw()

    def _refresh_vehicle_list(self) -> None:
        self.vehicle_list.delete(0, tk.END)
        for vehicle in self.vehicles:
            self.vehicle_list.insert(
                tk.END,
                f"{vehicle.plate:<8} {vehicle.vtype.label_text:<9} {vehicle.priority.label()}",
            )

    def _set_trace(self, steps: List[str]) -> None:
        self.trace.delete("1.0", tk.END)
        self.trace.insert(tk.END, "\n".join(steps[-80:]))

    def _redraw(self) -> None:
        if not hasattr(self, "canvas"):
            return

        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 760)
        height = max(canvas.winfo_height(), 460)

        margin_left = 90
        margin_top = 40
        cell = min((width - margin_left - 30) / self.lot.cols, (height - margin_top - 30) / self.lot.rows)
        cell = max(70, min(cell, 130))

        lot_width = cell * self.lot.cols
        lot_height = cell * self.lot.rows
        entrance_x = margin_left - 45
        entrance_y = margin_top + lot_height / 2

        canvas.create_rectangle(margin_left - 12, margin_top - 12, margin_left + lot_width + 12, margin_top + lot_height + 12, fill="#edf0f3", outline="")
        canvas.create_oval(entrance_x - 17, entrance_y - 17, entrance_x + 17, entrance_y + 17, fill="#20242a", outline="")
        canvas.create_text(entrance_x, entrance_y, text="<", fill="white", font=("Segoe UI", 16, "bold"))
        canvas.create_text(entrance_x, entrance_y + 30, text="Entrance", fill="#333", font=("Segoe UI", 9, "bold"))

        vehicles_by_id = {vehicle.id: vehicle for vehicle in self.vehicles}

        for vehicle_id, slot_id in self.assignment.items():
            slot = self.lot.slot_by_id(slot_id)
            vehicle = vehicles_by_id.get(vehicle_id)
            if not vehicle:
                continue
            x = margin_left + slot.col * cell + cell / 2
            y = margin_top + slot.row * cell + cell / 2
            canvas.create_line(entrance_x + 14, entrance_y, x, y, fill=PRIORITY_COLOR[vehicle.priority], width=2)

        for slot in self.lot.slots:
            x0 = margin_left + slot.col * cell
            y0 = margin_top + slot.row * cell
            x1 = x0 + cell - 6
            y1 = y0 + cell - 6
            assigned_vehicle_id = next((vehicle_id for vehicle_id, assigned_slot_id in self.assignment.items() if assigned_slot_id == slot.id), None)
            vehicle = vehicles_by_id.get(assigned_vehicle_id) if assigned_vehicle_id else None

            fill = "#ffffff" if vehicle else SLOT_FILL[slot.size]
            outline = PRIORITY_COLOR[vehicle.priority] if vehicle else "#b8c0c8"
            width_outline = 3 if vehicle else 1
            canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=width_outline)
            canvas.create_rectangle(x0, y0, x0 + 8, y1, fill=SLOT_STRIPE[slot.size], outline="")
            canvas.create_text(x0 + 14, y0 + 8, anchor="nw", text=f"#{slot.id}  d={slot.distance}", fill="#4b5560", font=("Segoe UI", 8))
            canvas.create_text(x1 - 8, y0 + 8, anchor="ne", text=slot.label(), fill="#68717b", font=("Segoe UI", 8, "italic"))

            if vehicle:
                draw_vehicle(canvas, vehicle.vtype, x0 + 12, y0 + 26, cell - 30, cell - 52)
                canvas.create_text((x0 + x1) / 2, y1 - 11, text=f"{vehicle.plate} | {vehicle.priority.label()}", fill=PRIORITY_COLOR[vehicle.priority], font=("Segoe UI", 9, "bold"))
            else:
                canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="empty", fill="#98a1aa", font=("Segoe UI", 10, "italic"))


if __name__ == "__main__":
    ParkingApp().mainloop()
