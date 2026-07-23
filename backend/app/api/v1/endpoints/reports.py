from fastapi import APIRouter

from app.api.dependencies import (
    DatabaseDependency,
    ReportReaderDependency,
)
from app.schemas.reports import (
    ClinicalReportResponse,
    DashboardReportResponse,
    FinancialReportResponse,
    SystemReportResponse,
)
from app.services.report_service import (
    read_clinical_report,
    read_dashboard_report,
    read_financial_report,
    read_system_report,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reportes"],
)


@router.get(
    "/dashboard",
    response_model=DashboardReportResponse,
)
def get_dashboard_report(
    database: DatabaseDependency,
    _: ReportReaderDependency,
) -> DashboardReportResponse:
    return read_dashboard_report(database)


@router.get(
    "/clinical",
    response_model=ClinicalReportResponse,
)
def get_clinical_report(
    database: DatabaseDependency,
    _: ReportReaderDependency,
) -> ClinicalReportResponse:
    return read_clinical_report(database)


@router.get(
    "/financial",
    response_model=FinancialReportResponse,
)
def get_financial_report(
    database: DatabaseDependency,
    _: ReportReaderDependency,
) -> FinancialReportResponse:
    return read_financial_report(database)


@router.get(
    "/system",
    response_model=SystemReportResponse,
)
def get_system_report(
    database: DatabaseDependency,
    _: ReportReaderDependency,
) -> SystemReportResponse:
    return read_system_report(database)
