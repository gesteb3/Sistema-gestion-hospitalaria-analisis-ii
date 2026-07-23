from app.utils.audit import (
    action_from_method,
    module_from_path,
    should_audit_path,
)


def test_action_from_method() -> None:
    assert action_from_method("POST") == "CREAR"
    assert action_from_method("GET") == "CONSULTAR"
    assert action_from_method("DELETE") == "ELIMINAR"


def test_module_from_path() -> None:
    assert module_from_path(
        "/api/v1/billing/invoices"
    ) == "BILLING"

    assert module_from_path(
        "/api/v1/clinical-histories/patient/1"
    ) == "CLINICAL_HISTORIES"


def test_should_audit_path() -> None:
    assert should_audit_path(
        "/api/v1/patients"
    )
    assert not should_audit_path(
        "/api/v1/health"
    )
