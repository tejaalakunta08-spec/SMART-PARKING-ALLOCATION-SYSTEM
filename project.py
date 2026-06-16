

# CO1:
# Python Essentials, Classes, Dataclasses, State Representation,
# Lists, Functions, Complexity-Aware Coding

from dataclasses import dataclass
import heapq

# ==========================================================
# CO1: STATE REPRESENTATION USING DATACLASSES
# ==========================================================

@dataclass
class ParkingSlot:
    slot_id: str
    distance: int
    slot_type: str
    occupied: bool = False
    availability_prob: float = 1.0


@dataclass
class Vehicle:
    vehicle_no: str
    vehicle_type: str


# ==========================================================
# MAIN SYSTEM
# ==========================================================

class SmartParkingSystem:

    def __init__(self):

        # CO1:
        # Knowledge Representation using Objects and Lists

        self.slots = [
            ParkingSlot("A1", 2, "Car", False, 0.95),
            ParkingSlot("A2", 5, "Car", False, 0.80),
            ParkingSlot("A3", 8, "Car", False, 0.70),
            ParkingSlot("B1", 1, "Bike", False, 0.90),
            ParkingSlot("B2", 4, "Bike", False, 0.85),
            ParkingSlot("B3", 7, "Bike", False, 0.75)
        ]

    # ======================================================
    # CO3: CSP (Constraint Satisfaction Problem)
    # ======================================================

    def is_valid_slot(self, vehicle, slot):

        if slot.occupied:
            print(f"{slot.slot_id} Rejected -> Slot Occupied")
            return False

        if vehicle.vehicle_type.lower() != slot.slot_type.lower():
            print(f"{slot.slot_id} Rejected -> Vehicle Type Mismatch")
            return False

        return True

    # ======================================================
    # CO2: A* SEARCH ALGORITHM
    # ======================================================

    def find_best_slot(self, vehicle):

        open_list = []

        print("\nSearching Available Slots...\n")

        for slot in self.slots:

            if self.is_valid_slot(vehicle, slot):

                # CO5:
                # Probability Reasoning
                # Availability probability used in heuristic

                heuristic = 1 - slot.availability_prob

                # CO2:
                # f(n) = g(n) + h(n)

                cost = slot.distance + heuristic

                print(
                    f"Slot={slot.slot_id} | "
                    f"Distance={slot.distance} | "
                    f"Probability={slot.availability_prob} | "
                    f"Cost={cost:.2f}"
                )

                heapq.heappush(
                    open_list,
                    (cost, slot.slot_id, slot)
                )

        if not open_list:
            return None

        return heapq.heappop(open_list)[2]

    # ======================================================
    # CO4: UTILITY-BASED DECISION MAKING
    # ======================================================

    def calculate_utility(self, slot):

        utility = (10 - slot.distance) * slot.availability_prob

        return utility

    # ======================================================
    # CO6: HYBRID AI SYSTEM
    # ======================================================

    def allocate_slot(self, vehicle):

        slot = self.find_best_slot(vehicle)

        if slot is None:
            print("\nNo Suitable Slot Found")
            return

        utility = self.calculate_utility(slot)

        print("\n========== REASONING TRACE ==========")
        print(f"Vehicle Number       : {vehicle.vehicle_no}")
        print(f"Vehicle Type         : {vehicle.vehicle_type}")
        print(f"Selected Slot        : {slot.slot_id}")
        print(f"Distance             : {slot.distance}")
        print(f"Availability Prob.   : {slot.availability_prob}")
        print(f"Utility Score        : {utility:.2f}")
        print("=====================================")

        slot.occupied = True

        print("\nParking Allocated Successfully!")

    # ======================================================
    # CO1:
    # State Update
    # ======================================================

    def release_slot(self, slot_id):

        for slot in self.slots:

            if slot.slot_id.upper() == slot_id.upper():

                if slot.occupied:

                    slot.occupied = False

                    print("\nSlot Released Successfully")

                else:

                    print("\nSlot Already Free")

                return

        print("\nInvalid Slot ID")

    # ======================================================
    # CO1:
    # Display Current Environment State
    # ======================================================

    def display_slots(self):

        print("\n========== PARKING STATUS ==========")
        print("Slot\tType\tDistance\tStatus")

        for slot in self.slots:

            status = "Occupied" if slot.occupied else "Free"

            print(
                f"{slot.slot_id}\t"
                f"{slot.slot_type}\t"
                f"{slot.distance}\t\t"
                f"{status}"
            )

        print("====================================")


# ==========================================================
# CO1: PEAS MODEL
# ==========================================================


def main():

    parking_system = SmartParkingSystem()

    while True:

        print("\n====================================")
        print(" SMART PARKING ALLOCATION SYSTEM ")
        print("====================================")
        print("1. View Parking Slots")
        print("2. Allocate Parking")
        print("3. Release Slot")
        print("4. Exit")

        choice = input("\nEnter Choice: ")

        if choice == "1":

            parking_system.display_slots()

        elif choice == "2":

            vehicle_no = input("Enter Vehicle Number: ")
            vehicle_type = input("Enter Vehicle Type (Car/Bike): ")

            vehicle = Vehicle(vehicle_no, vehicle_type)

            parking_system.allocate_slot(vehicle)

        elif choice == "3":

            slot_id = input("Enter Slot ID to Release: ")

            parking_system.release_slot(slot_id)

        elif choice == "4":

            print("\nThank You")
            break

        else:

            print("\nInvalid Choice")


# ==========================================================
# PROGRAM START
# ==========================================================

if __name__ == "__main__":
    main()


# ==========================================================
# CO MAPPING SUMMARY
# ==========================================================
#
# CO1:
# - PEAS Model
# - State Representation
# - Dataclasses
# - Lists and Objects
# - Environment Modeling
#
# CO2:
# - A* Search Concept
# - Cost Function
# - Heuristic Function
# - Priority Queue (heapq)
#
# CO3:
# - CSP Modeling
# - Constraint Checking
# - Constraint Failure Explanation
#
# CO4:
# - Utility Function
# - Rational Decision Making
#
# CO5:
# - Probability-Based Availability
# - Uncertainty Reasoning
#
# CO6:
# - Hybrid AI System
# - Search + CSP + Probability + Utility
# - Explainable AI Trace
#
# ==========================================================