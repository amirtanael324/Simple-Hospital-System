import random
from datetime import datetime, date
from typing import List, Optional, Tuple

# Domain classes

class HospitalRoom:
    def __init__(self, room_number: str, room_type: str):
        self.room_number = room_number
        self.room_type = room_type
        self.available = True
        self.assigned_patient: Optional['Patient'] = None

    def assign_patient(self, patient: 'Patient') -> None:
        if self.available:
            self.assigned_patient = patient
            self.available = False
            patient.room = self

    def vacate_room(self) -> None:
        if self.assigned_patient:
            self.assigned_patient.room = None
        self.assigned_patient = None
        self.available = True

    def is_available(self) -> bool:
        return self.available

    def set_unavailable(self) -> None:
        self.available = False


class MedicalRecord:
    def __init__(self, record_id: str):
        self.record_id = record_id
        self.history_summary: List[str] = []
        self.diagnosis: str = ""
        self.allergies: List[str] = []
        self.is_closed = False

    def add_entry(self, entry: str) -> None:
        if not self.is_closed:
            self.history_summary.append(entry)

    def get_summary(self) -> str:
        return "\n".join(self.history_summary)

    def close_record(self) -> None:
        self.is_closed = True


class Patient:
    def __init__(self, patient_id: str, patient_name: str, date_of_birth: date, gender: str, contact_information: str):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.contact_information = contact_information

        self.medical_record = MedicalRecord(f"REC-{patient_id}")
        self.appointments: List['Appointment'] = []
        self.treatments: List['Treatment'] = []
        self.bills: List['Bill'] = []

        # Added for the hospital flow
        self.condition: Optional[str] = None
        self.assigned_doctor: Optional['Doctor'] = None
        self.room: Optional[HospitalRoom] = None

    def register_patient(self) -> None:
        print(f"Patient registered: {self.patient_name}")

    def update_record(self, entry: str) -> None:
        if self.medical_record:
            self.medical_record.add_entry(entry)

    def get_medical_record(self) -> MedicalRecord:
        return self.medical_record


class Appointment:
    def __init__(self, appointment_id: str, date_time: datetime, reason: str, patient: Patient, doctor: 'Doctor'):
        self.appointment_id = appointment_id
        self.date = date_time
        self.reason = reason
        self.status = "Scheduled"
        self.patient = patient
        self.doctor = doctor

    def confirm_appointment(self) -> None:
        self.status = "Confirmed"

    def cancel_appointment(self) -> None:
        self.status = "Cancelled"

    def reschedule_appointment(self, new_date: datetime) -> None:
        self.date = new_date
        self.status = "Rescheduled"


class Doctor:
    def __init__(self, doctor_id: str, name: str, specialization: str, experience: int):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.experience = experience
        self.available = True
        self.room: Optional[HospitalRoom] = None

        self.patients: List[Patient] = []
        self.appointments: List[Appointment] = []
        self.treatments: List['Treatment'] = []
        self.prescriptions: List['Prescription'] = []
        self.lab_tests: List['LabTest'] = []

    def schedule_appointment(self, appointment: Appointment) -> None:
        self.appointments.append(appointment)

    def update_prescription(self, prescription: 'Prescription', new_instructions: str) -> None:
        prescription.set_instructions(new_instructions)

    def is_available(self) -> bool:
        return self.available

    def set_unavailable(self) -> None:
        self.available = False

    def set_available(self) -> None:
        self.available = True


class Prescription:
    def __init__(self, prescription_id: str, prescribed_date: date, instructions: str):
        self.prescription_id = prescription_id
        self.prescribed_date = prescribed_date
        self.instructions = instructions
        self.is_cancelled = False
        self.medicines: List['Medicine'] = []

    def add_medicine(self, medicine: 'Medicine') -> None:
        self.medicines.append(medicine)

    def cancel_prescription(self) -> None:
        self.is_cancelled = True

    def set_instructions(self, instructions: str) -> None:
        self.instructions = instructions


class Treatment:
    def __init__(self, treatment_id: str, name: str, description: str, cost: float):
        self.treatment_id = treatment_id
        self.name = name
        self.description = description
        self.cost = cost
        self.prescription: Optional[Prescription] = None

    def apply_treatment(self, prescription: Optional[Prescription] = None) -> None:
        self.prescription = prescription
        print(f"  Applying treatment: {self.name}")

    def calculate_cost(self) -> float:
        return self.cost


class Medicine:
    def __init__(self, medicine_id: str, name: str, dosage: str, stock_count: int, price_per_unit: float):
        self.medicine_id = medicine_id
        self.name = name
        self.dosage = dosage
        self.stock_count = stock_count
        self.price_per_unit = price_per_unit

    def check_stock(self) -> int:
        return self.stock_count

    def dispense_medicine(self, quantity: int) -> bool:
        if self.stock_count >= quantity:
            self.stock_count -= quantity
            return True
        return False

    def get_price_per_unit(self) -> float:
        return self.price_per_unit


class LabTest:
    def __init__(self, test_id: str, test_name: str, test_date: date, test_cost: float):
        self.test_id = test_id
        self.test_name = test_name
        self.results: Optional[str] = None
        self.status = "Pending"
        self.test_date = test_date
        self.test_cost = test_cost

    def record_results(self, results: str) -> None:
        self.results = results
        self.status = "Completed"

    def generate_report(self) -> str:
        return f"Test: {self.test_name} | Date: {self.test_date} | Results: {self.results}"

    def get_cost(self) -> float:
        return self.test_cost


class Bill:
    def __init__(self, bill_id: str, issue_date: date):
        self.bill_id = bill_id
        self.issue_date = issue_date
        self.total_amount = 0.0
        self.amount_paid = 0.0
        self.status = "Unpaid"

        self.treatments: List[Treatment] = []
        self.lab_tests: List[LabTest] = []
        self.medicines: List[Tuple[Medicine, int]] = []  # (medicine, quantity)

    @property
    def balance(self) -> float:
        return round(self.total_amount - self.amount_paid, 2)

    def add_charge(self, amount: float) -> None:
        self.total_amount += amount

    def add_treatment(self, treatment: Treatment) -> None:
        self.treatments.append(treatment)
        self.add_charge(treatment.calculate_cost())

    def add_lab_test(self, lab_test: LabTest) -> None:
        self.lab_tests.append(lab_test)
        self.add_charge(lab_test.get_cost())

    def add_medicine(self, medicine: Medicine, quantity: int) -> None:
        self.medicines.append((medicine, quantity))
        self.add_charge(medicine.get_price_per_unit() * quantity)

    def generate_bill(self) -> None:
        print("\n" + "=" * 52)
        print(f" BILL {self.bill_id}    Issued: {self.issue_date}")
        print("=" * 52)
        for t in self.treatments:
            print(f"  Treatment  {t.name:<24} ${t.calculate_cost():>9.2f}")
        for l in self.lab_tests:
            print(f"  Lab test   {l.test_name:<24} ${l.get_cost():>9.2f}")
        for m, qty in self.medicines:
            label = f"{m.name} x{qty}"
            print(f"  Medicine   {label:<24} ${m.get_price_per_unit() * qty:>9.2f}")
        print("-" * 52)
        print(f"  TOTAL                               ${self.total_amount:>9.2f}")
        print("=" * 52)

    def receive_payment(self, amount: float) -> None:
        self.amount_paid = min(self.amount_paid + amount, self.total_amount)
        if self.amount_paid >= self.total_amount:
            self.status = "Paid"
        elif self.amount_paid > 0:
            self.status = "Partially Paid"

# Input helpers

def ask(prompt: str) -> str:
    return input(prompt).strip()


def ask_nonempty(prompt: str) -> str:
    while True:
        value = ask(prompt)
        if value:
            return value
        print("  Please enter a value.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        value = ask(prompt).lower()
        if value in ("yes", "y"):
            return True
        if value in ("no", "n"):
            return False
        print("  Please answer yes or no.")


def ask_choice(prompt: str, options: List[str]) -> int:
    """Show a numbered menu and return the chosen 0-based index."""
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    while True:
        value = ask("Choose a number: ")
        if value.isdigit() and 1 <= int(value) <= len(options):
            return int(value) - 1
        print(f"  Enter a number between 1 and {len(options)}.")


def ask_date(prompt: str) -> date:
    while True:
        try:
            return datetime.strptime(ask(prompt), "%Y-%m-%d").date()
        except ValueError:
            print("  Use the format YYYY-MM-DD (e.g. 2001-04-23).")


def ask_int(prompt: str, default: int) -> int:
    while True:
        value = ask(prompt)
        if value == "":
            return default
        if value.isdigit() and int(value) > 0:
            return int(value)
        print("  Enter a positive whole number (or press Enter for the default).")

# Hospital data

# condition -> (category, medicines prescribed, treatments given, lab test)
CONDITIONS = {
    "Fever / headache":    ("minor",  ["Paracetamol"],                    [],                                  "Blood Test"),
    "Cough / cold":        ("minor",  ["Cough Syrup", "Cetirizine"],      [],                                  "Blood Test"),
    "Seasonal allergy":    ("minor",  ["Cetirizine"],                     [],                                  "Blood Test"),
    "Bacterial infection": ("minor",  ["Amoxicillin", "Paracetamol"],     [],                                  "Blood Test"),
    "Fractured bone":      ("injury", [],                                 ["Cast", "Physiotherapy Session"],   "X-Ray"),
    "Deep cut":            ("injury", [],                                 ["Stitches", "Wound Dressing"],      "Blood Test"),
    "Sprain":              ("injury", [],                                 ["Splint"],                          "X-Ray"),
}

# name, dosage, stock, price per unit, default course quantity
MEDICINE_CATALOG = [
    ("Paracetamol", "500mg", 100, 0.50, 10),
    ("Ibuprofen",   "400mg", 100, 0.75, 10),
    ("Amoxicillin", "500mg",  80, 1.20, 14),
    ("Cetirizine",  "10mg",   60, 0.60, 7),
    ("Cough Syrup", "100ml",  40, 6.00, 1),
]

# name, description, cost
TREATMENT_CATALOG = [
    ("Cast",                  "Plaster cast for a broken bone",   150.00),
    ("Splint",                "Support splint for a sprain",       60.00),
    ("Stitches",              "Wound closure with sutures",        90.00),
    ("Wound Dressing",        "Cleaning and dressing of a wound",  30.00),
    ("Physiotherapy Session", "Guided recovery session",           80.00),
]

# name, cost
LAB_TEST_CATALOG = [
    ("Blood Test", 40.00),
    ("X-Ray",      75.00),
]

LAB_RESULTS = {
    "Blood Test": ["Normal range, mild inflammation markers", "Slightly elevated white cell count", "All values normal"],
    "X-Ray":      ["Imaging complete, consistent with reported injury", "No additional damage detected"],
}

# Allergy name -> medicines it rules out (besides an exact name match)
ALLERGY_MAP = {
    "penicillin": ["amoxicillin"],
    "nsaids":     ["ibuprofen"],
    "nsaid":      ["ibuprofen"],
}

# Doctor certificate questions: (question, accepted answers)
CERTIFICATE_QUESTIONS = [
    ("How many bones are in the adult human body?", ["206", "two hundred and six", "two hundred six"]),
    ("How many chambers does the human heart have?", ["4", "four"]),
    ("What is the largest organ of the human body?", ["skin", "the skin"]),
    ("Which organ produces insulin?", ["pancreas", "the pancreas"]),
    ("Which vitamin does the skin produce in sunlight?", ["d", "vitamin d"]),
    ("Which blood type is the universal donor?", ["o negative", "o-", "o neg"]),
]

SPECIALIZATIONS = ["General Practitioner", "Orthopedics"]

RANDOM_NAMES = ["Layla Hassan", "Omar Saleh", "Maya Chen", "Daniel Brooks", "Noor Aziz",
                "Carlos Mendez", "Sara Ibrahim", "Tom Walker", "Yusuf Karim", "Emma Rossi"]

# Hospital controller

class Hospital:
    def __init__(self):
        self.rooms = [
            HospitalRoom("101", "General Ward"), HospitalRoom("102", "General Ward"),
            HospitalRoom("103", "General Ward"), HospitalRoom("201", "Treatment Room"),
            HospitalRoom("202", "Treatment Room"),
        ]
        self.doctors = [
            Doctor("D001", "Dr. Sarah Ahmed", "General Practitioner", 12),
            Doctor("D002", "Dr. Omar Khalid", "Orthopedics", 15),
            Doctor("D003", "Dr. Lina Haddad", "General Practitioner", 6),
            Doctor("D004", "Dr. James Carter", "Orthopedics", 9),
        ]
        self.medicines = {
            name: Medicine(f"MED-{i:02d}", name, dosage, stock, price)
            for i, (name, dosage, stock, price, _) in enumerate(MEDICINE_CATALOG, 1)
        }
        self.course_qty = {name: qty for name, _, _, _, qty in MEDICINE_CATALOG}
        self.patients: List[Patient] = []

        self.patient_count = 0
        self.doctor_count = len(self.doctors)
        self.appointment_count = 0
        self.prescription_count = 0
        self.treatment_count = 0
        self.lab_count = 0
        self.bill_count = 0

    # factories

    def new_patient(self, name: str, dob: date, gender: str, contact: str) -> Patient:
        self.patient_count += 1
        patient = Patient(f"P{self.patient_count:03d}", name, dob, gender, contact)
        self.patients.append(patient)
        return patient

    def new_treatment(self, name: str) -> Treatment:
        for t_name, description, cost in TREATMENT_CATALOG:
            if t_name == name:
                self.treatment_count += 1
                return Treatment(f"TRT-{self.treatment_count:03d}", t_name, description, cost)
        raise KeyError(name)

    def new_lab_test(self, name: str) -> LabTest:
        for t_name, cost in LAB_TEST_CATALOG:
            if t_name == name:
                self.lab_count += 1
                return LabTest(f"LAB-{self.lab_count:03d}", t_name, date.today(), cost)
        raise KeyError(name)

    def new_prescription(self, instructions: str = "Take as directed by your doctor.") -> Prescription:
        self.prescription_count += 1
        return Prescription(f"RX-{self.prescription_count:03d}", date.today(), instructions)

    def new_bill(self) -> Bill:
        self.bill_count += 1
        return Bill(f"BILL-{self.bill_count:03d}", date.today())

    def new_appointment(self, patient: Patient, doctor: Doctor) -> Appointment:
        self.appointment_count += 1
        appt = Appointment(f"APT-{self.appointment_count:03d}", datetime.now(), patient.condition or "", patient, doctor)
        doctor.schedule_appointment(appt)
        patient.appointments.append(appt)
        return appt

    # lookups

    def find_doctor(self, category: str) -> Optional[Doctor]:
        wanted = "Orthopedics" if category == "injury" else "General Practitioner"
        free = [d for d in self.doctors if d.is_available()]
        matching = [d for d in free if d.specialization == wanted]
        pool = matching or free
        return pool[0] if pool else None

    def find_room(self, category: str) -> Optional[HospitalRoom]:
        wanted = "Treatment Room" if category == "injury" else "General Ward"
        free = [r for r in self.rooms if r.is_available()]
        matching = [r for r in free if r.room_type == wanted]
        pool = matching or free
        return pool[0] if pool else None

    @staticmethod
    def is_allergic(patient: Patient, medicine: Medicine) -> bool:
        med = medicine.name.lower()
        for allergy in patient.medical_record.allergies:
            a = allergy.strip().lower()
            if a and (a == med or med in ALLERGY_MAP.get(a, [])):
                return True
        return False

    # shared clinical steps 

    def run_lab_test(self, doctor: Doctor, patient: Patient, bill: Bill, test_name: str) -> None:
        lab = self.new_lab_test(test_name)
        print(f"  Running lab test: {lab.test_name} ...")
        lab.record_results(random.choice(LAB_RESULTS[test_name]))
        doctor.lab_tests.append(lab)
        bill.add_lab_test(lab)
        patient.update_record(f"Lab test - {lab.generate_report()}")
        print(f"  {lab.generate_report()}")

    def dispense(self, doctor: Doctor, patient: Patient, bill: Bill,
                 prescription: Prescription, medicine: Medicine, quantity: int) -> bool:
        if self.is_allergic(patient, medicine):
            print(f"  WARNING: patient is allergic to {medicine.name}. Not prescribed.")
            return False
        if not medicine.dispense_medicine(quantity):
            print(f"  {medicine.name} is out of stock (only {medicine.check_stock()} left).")
            return False
        prescription.add_medicine(medicine)
        bill.add_medicine(medicine, quantity)
        patient.update_record(f"Medicine administered: {medicine.name} {medicine.dosage} x{quantity}")
        print(f"  Administered {medicine.name} {medicine.dosage} x{quantity}")
        return True

    def give_treatment(self, doctor: Doctor, patient: Patient, bill: Bill,
                       treatment_name: str, prescription: Optional[Prescription] = None) -> None:
        treatment = self.new_treatment(treatment_name)
        treatment.apply_treatment(prescription)
        patient.treatments.append(treatment)
        doctor.treatments.append(treatment)
        bill.add_treatment(treatment)
        patient.update_record(f"Treatment given: {treatment.name}")

    def assign_doctor_and_appointment(self, patient: Patient, doctor: Doctor) -> Appointment:
        patient.assigned_doctor = doctor
        doctor.patients.append(patient)
        doctor.set_unavailable()
        appt = self.new_appointment(patient, doctor)
        appt.confirm_appointment()
        return appt

    def release_form(self, doctor: Doctor, patient: Patient, bill: Bill) -> None:
        print("                 HOSPITAL RELEASE FORM")
        print(f" Patient:    {patient.patient_name} ({patient.patient_id})")
        print(f" Diagnosis:  {patient.medical_record.diagnosis}")
        print(f" Doctor:     {doctor.name} ({doctor.specialization})")
        print(f" Discharged: {datetime.now():%Y-%m-%d %H:%M}")
        print(f" Bill:       {bill.bill_id} - total ${bill.total_amount:.2f} ({bill.status})")
        print(" The above patient is cleared for release from hospital care.")
        print(f" Doctor signature: {doctor.name}")

    @staticmethod
    def pay_bill(bill: Bill) -> None:
        if bill.total_amount <= 0:
            bill.status = "Paid"
            return
        while True:
            value = ask(f"Enter payment amount (press Enter to pay the full ${bill.balance:.2f}): ")
            if value == "":
                amount = bill.balance
            else:
                try:
                    amount = float(value)
                except ValueError:
                    print("  Enter a number.")
                    continue
                if amount <= 0:
                    print("  Amount must be positive.")
                    continue
            bill.receive_payment(amount)
            print(f"  Payment received. Status: {bill.status}")
            if bill.balance > 0:
                print(f"  Remaining balance of ${bill.balance:.2f} is due at reception.")
            break

    # ---- patient flow -----------------------------------------------------

    def run_patient(self) -> None:
        print("\n--- Patient Registration ---")
        name = ask_nonempty("Please enter your name: ")
        dob = ask_date("Date of birth (YYYY-MM-DD): ")
        gender = ask_nonempty("Gender: ")
        contact = ask_nonempty("Contact information (phone/email): ")

        patient = self.new_patient(name, dob, gender, contact)
        patient.register_patient()
        print(f"Your patient ID is {patient.patient_id}")

        # Medical record
        print("\n--- Medical Record ---")
        conditions = list(CONDITIONS)
        patient.condition = conditions[ask_choice("What brings you in today?", conditions)]
        category = CONDITIONS[patient.condition][0]
        allergies = ask("Any allergies? (comma separated, or press Enter for none): ")
        patient.medical_record.allergies = [a.strip() for a in allergies.split(",") if a.strip()]
        history = ask("Relevant medical history (press Enter to skip): ")
        patient.update_record(f"Presenting complaint: {patient.condition}")
        if history:
            patient.update_record(f"Patient history: {history}")
        print("Medical record saved.")

        # Doctor and room assignment
        doctor = self.find_doctor(category)
        if doctor is None:
            print("\nNo doctor is available right now. Please come back shortly.")
            return
        appointment = self.assign_doctor_and_appointment(patient, doctor)

        room = self.find_room(category)
        if room is None:
            print("\nNo room is available right now. Please come back shortly.")
            appointment.cancel_appointment()
            doctor.set_available()
            return
        room.assign_patient(patient)

        print(f"\nYou have been assigned to {doctor.name} ({doctor.specialization}).")
        print(f"Your room: {room.room_number} ({room.room_type}).")

        # The only point where the patient may still leave
        if not ask_yes_no("Do you want to proceed to your room? Answering 'no' lets you leave (yes/no): "):
            room.vacate_room()
            doctor.set_available()
            appointment.cancel_appointment()
            print("You have left the hospital. Take care!")
            return

        print(f"\nYou are now in room {room.room_number}. Treatment will begin.")
        bill = self.new_bill()
        patient.bills.append(bill)
        _, medicine_names, treatment_names, lab_name = CONDITIONS[patient.condition]

        # Lab test
        self.run_lab_test(doctor, patient, bill, lab_name)
        patient.medical_record.diagnosis = patient.condition

        # Prescription (minor sickness) or treatment (injury)
        if category == "minor":
            prescription = self.new_prescription()
            doctor.prescriptions.append(prescription)
            print(f"\n{doctor.name} is writing your prescription ({prescription.prescription_id}):")
            given = [
                self.dispense(doctor, patient, bill, prescription,
                              self.medicines[m], self.course_qty[m])
                for m in medicine_names
            ]
            if not any(given):
                print("  No suitable medicine could be given. Please see the doctor for alternatives.")
        else:
            print(f"\n{doctor.name} is treating your injury:")
            for t in treatment_names:
                self.give_treatment(doctor, patient, bill, t)

        # Billing
        bill.generate_bill()
        self.pay_bill(bill)

        # Discharge
        patient.medical_record.close_record()
        self.release_form(doctor, patient, bill)
        room.vacate_room()
        doctor.set_available()
        print("\nThank you for visiting. Get well soon!")

    # ---- doctor flow ------------------------------------------------------

    def doctor_certificate(self) -> bool:
        question, answers = random.choice(CERTIFICATE_QUESTIONS)
        print("\nTo verify your certificate, answer this question (3 attempts):")
        print(f"  {question}")
        for attempt in range(1, 4):
            if ask(f"Answer ({attempt}/3): ").lower() in answers:
                print("Certificate verified.")
                return True
            print("  Incorrect.")
        print("Certificate verification failed. Access denied.")
        return False

    def random_patient(self) -> Patient:
        name = random.choice(RANDOM_NAMES)
        dob = date(random.randint(1950, 2015), random.randint(1, 12), random.randint(1, 28))
        patient = self.new_patient(name, dob, random.choice(["Male", "Female"]), "N/A (walk-in)")
        patient.condition = random.choice(list(CONDITIONS))
        patient.medical_record.allergies = random.choice([[], [], [], ["Penicillin"], ["NSAIDs"]])
        patient.update_record(f"Presenting complaint: {patient.condition}")
        patient.update_record(random.choice([
            "No significant history", "Previous similar episode last year",
            "Hypertension (controlled)", "No known chronic conditions"]))
        return patient

    def doctor_menu(self, doctor: Doctor, patient: Patient, bill: Bill) -> None:
        prescription: Optional[Prescription] = None
        while True:
            choice = ask_choice(
                "\nWhat would you like to do for this patient?",
                ["Prescribe medicine", "Give treatment", "Order lab test", "Finish and calculate bill"])

            if choice == 0:
                names = list(self.medicines)
                labels = [
                    f"{n} {self.medicines[n].dosage} - ${self.medicines[n].price_per_unit:.2f}/unit "
                    f"(stock {self.medicines[n].stock_count})" for n in names]
                medicine = self.medicines[names[ask_choice("Select medicine:", labels)]]
                quantity = ask_int(f"Quantity (Enter for {self.course_qty[medicine.name]}): ",
                                   self.course_qty[medicine.name])
                if prescription is None:
                    prescription = self.new_prescription()
                    doctor.prescriptions.append(prescription)
                self.dispense(doctor, patient, bill, prescription, medicine, quantity)

            elif choice == 1:
                labels = [f"{n} - {d} (${c:.2f})" for n, d, c in TREATMENT_CATALOG]
                name = TREATMENT_CATALOG[ask_choice("Select treatment:", labels)][0]
                self.give_treatment(doctor, patient, bill, name, prescription)

            elif choice == 2:
                labels = [f"{n} (${c:.2f})" for n, c in LAB_TEST_CATALOG]
                name = LAB_TEST_CATALOG[ask_choice("Select lab test:", labels)][0]
                self.run_lab_test(doctor, patient, bill, name)

            else:
                return

    def run_doctor(self) -> None:
        print("\n Doctor Sign-in ")
        name = ask_nonempty("Please enter your name: ")
        if not self.doctor_certificate():
            return

        spec = SPECIALIZATIONS[ask_choice("Select your specialization:", SPECIALIZATIONS)]
        self.doctor_count += 1
        doctor = Doctor(f"D{self.doctor_count:03d}", name, spec, 0)
        doctor.set_unavailable()
        print(f"Welcome, {doctor.name}. Your doctor ID is {doctor.doctor_id}.")

        room = self.find_room("injury" if spec == "Orthopedics" else "minor")
        if room is None:
            print("No room is available right now. Please come back shortly.")
            return
        doctor.room = room
        room.set_unavailable()
        print(f"You have been assigned to room {room.room_number} ({room.room_type}).")

        while True:
            patient = self.random_patient()
            room.available = True  # room was only reserved for the doctor; free it for the patient
            room.assign_patient(patient)
            appointment = self.assign_doctor_and_appointment(patient, doctor)
            doctor.set_unavailable()
            appointment.confirm_appointment()

            print("\n" + "-" * 52)
            print(f" New patient: {patient.patient_name} ({patient.patient_id})")
            print(f" Born: {patient.date_of_birth}   Gender: {patient.gender}")
            allergies = ", ".join(patient.medical_record.allergies) or "None"
            print(f" Allergies: {allergies}")
            print(" Medical record:")
            for line in patient.medical_record.get_summary().splitlines():
                print(f"   - {line}")
            print("-" * 52)

            bill = self.new_bill()
            patient.bills.append(bill)
            self.doctor_menu(doctor, patient, bill)

            patient.medical_record.diagnosis = patient.condition or ""
            bill.generate_bill()
            bill.status = "Billed to patient"
            self.release_form(doctor, patient, bill)

            patient.medical_record.close_record()
            room.vacate_room()
            room.set_unavailable()  # still reserved for this doctor

            if not ask_yes_no("\nTreat another patient? (yes/no): "):
                break

        room.available = True
        doctor.room = None
        print(f"\nSession ended. Thank you, {doctor.name}!")

# Entry point

def main() -> None:
    hospital = Hospital()
    print("Welcome to the Hospital System")
    try:
        while True:
            if not ask_yes_no("\nEnter hospital? (yes/no): "):
                print("Goodbye!")
                break
            role = ask_choice("Are you a patient or a doctor?", ["Patient", "Doctor"])
            if role == 0:
                hospital.run_patient()
            else:
                hospital.run_doctor()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")


if __name__ == "__main__":
    main()