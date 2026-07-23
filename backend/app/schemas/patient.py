from datetime import date, datetime
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


ALLOWED_SEXES = {
    "MASCULINO",
    "FEMENINO",
    "OTRO",
}


class LegalGuardianInput(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    identificacion: str = Field(min_length=4, max_length=30)
    parentesco: str = Field(min_length=2, max_length=50)
    telefono: str = Field(min_length=8, max_length=20)
    correo: EmailStr | None = None

    @field_validator(
        "nombres",
        "apellidos",
        "identificacion",
        "parentesco",
        "telefono",
    )
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip()


class LegalGuardianResponse(BaseModel):
    responsable_id: int
    nombres: str
    apellidos: str
    identificacion: str
    parentesco: str
    telefono: str
    correo: EmailStr | None
    principal: bool

    model_config = ConfigDict(from_attributes=True)


class PatientBase(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    fecha_nacimiento: date
    sexo: str
    identificacion: str | None = Field(
        default=None,
        min_length=4,
        max_length=30,
    )
    telefono: str | None = Field(
        default=None,
        min_length=8,
        max_length=20,
    )
    correo: EmailStr | None = None
    direccion: str | None = Field(
        default=None,
        max_length=250,
    )

    @field_validator("nombres", "apellidos")
    @classmethod
    def strip_names(cls, value: str) -> str:
        return value.strip()

    @field_validator(
        "identificacion",
        "telefono",
        "direccion",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("sexo")
    @classmethod
    def validate_sex(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in ALLOWED_SEXES:
            allowed = ", ".join(sorted(ALLOWED_SEXES))
            raise ValueError(
                f"El sexo debe ser uno de estos valores: {allowed}."
            )

        return normalized

    @field_validator("fecha_nacimiento")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError(
                "La fecha de nacimiento no puede estar en el futuro."
            )

        return value


class PatientCreate(PatientBase):
    responsable_legal: LegalGuardianInput | None = None


class PatientUpdate(BaseModel):
    nombres: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    apellidos: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    fecha_nacimiento: date | None = None
    sexo: str | None = None
    identificacion: str | None = Field(
        default=None,
        min_length=4,
        max_length=30,
    )
    telefono: str | None = Field(
        default=None,
        min_length=8,
        max_length=20,
    )
    correo: EmailStr | None = None
    direccion: str | None = Field(
        default=None,
        max_length=250,
    )
    responsable_legal: LegalGuardianInput | None = None

    @field_validator("nombres", "apellidos")
    @classmethod
    def strip_optional_names(
        cls,
        value: str | None,
    ) -> str | None:
        return value.strip() if value is not None else None

    @field_validator(
        "identificacion",
        "telefono",
        "direccion",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("sexo")
    @classmethod
    def validate_optional_sex(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip().upper()

        if normalized not in ALLOWED_SEXES:
            allowed = ", ".join(sorted(ALLOWED_SEXES))
            raise ValueError(
                f"El sexo debe ser uno de estos valores: {allowed}."
            )

        return normalized

    @field_validator("fecha_nacimiento")
    @classmethod
    def validate_optional_birth_date(
        cls,
        value: date | None,
    ) -> date | None:
        if value is not None and value > date.today():
            raise ValueError(
                "La fecha de nacimiento no puede estar en el futuro."
            )

        return value

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        return self


class PatientResponse(BaseModel):
    paciente_id: int
    numero_expediente: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    edad: int
    menor_de_edad: bool
    sexo: str
    identificacion: str | None
    telefono: str | None
    correo: EmailStr | None
    direccion: str | None
    activo: bool
    responsables_legales: list[LegalGuardianResponse]
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class PatientListResponse(BaseModel):
    items: list[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
