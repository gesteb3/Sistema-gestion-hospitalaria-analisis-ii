from fastapi import APIRouter

from app.api.v1.endpoints import (
    appointments,
    auth,
    clinical,
    doctors,
    health,
    patients,
    pharmacy,
    specialties,
    users,
)


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(patients.router)
api_router.include_router(specialties.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(clinical.history_router)
api_router.include_router(clinical.consultation_router)
api_router.include_router(pharmacy.medication_router)
api_router.include_router(pharmacy.prescription_router)
