from fastapi import APIRouter

from app.api.v1.endpoints import (
    appointments,
    audit,
    auth,
    billing,
    clinical,
    doctors,
    health,
    laboratory,
    patients,
    pharmacy,
    reports,
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
api_router.include_router(laboratory.test_type_router)
api_router.include_router(laboratory.lab_order_router)
api_router.include_router(billing.router)
api_router.include_router(audit.router)
api_router.include_router(reports.router)
