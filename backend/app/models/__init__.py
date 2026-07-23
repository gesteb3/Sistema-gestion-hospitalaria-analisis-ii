from app.models.association import usuario_roles
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.models.doctor_specialty import medico_especialidades
from app.models.legal_guardian import LegalGuardian
from app.models.patient import Patient
from app.models.role import Role
from app.models.specialty import Specialty
from app.models.user import User

__all__ = [
    "Doctor",
    "DoctorSchedule",
    "LegalGuardian",
    "Patient",
    "Role",
    "Specialty",
    "User",
    "medico_especialidades",
    "usuario_roles",
]
