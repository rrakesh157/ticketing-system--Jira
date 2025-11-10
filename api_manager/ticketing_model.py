import typing
import datetime
import ipaddress
import fastapi
import pydantic
import shutil
import os
import urdhva_base.postgresmodel
import urdhva_base.queryparams
import urdhva_base.types
import ticketing_enum

from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    DateTime,
    Boolean,
    Interval,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from urdhva_base.postgresmodel import UrdhvaPostgresBase


class Ticket_HistoryCreate(pydantic.BaseModel):
    description: typing.Optional[str] = pydantic.Field("", **{})
    processed_time: typing.Optional[str] = pydantic.Field("", **{})
    allocated_time: typing.Optional[str] = pydantic.Field("", **{})
    action_msg: typing.Optional[str] = pydantic.Field("", **{})
    action_type: typing.Optional[str] = pydantic.Field("", **{})


class Merge_HistoryCreate(pydantic.BaseModel):
    ticket_id: typing.Optional[str] = pydantic.Field("", **{})
    merge_ticket_id: typing.List[str]
    comment: typing.Optional[str] = pydantic.Field("", **{})
    processed_time: typing.Optional[str] = pydantic.Field("", **{})
    allocated_time: typing.Optional[str] = pydantic.Field("", **{})
    action_msg: typing.Optional[str] = pydantic.Field("", **{})
    action_type: typing.Optional[str] = pydantic.Field("", **{})


class TicketingSchema(UrdhvaPostgresBase):
    __tablename__ = 'ticketing'
    
    ticket_name: Mapped[typing.Optional[str]] = mapped_column("ticket_name", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    ticket_id: Mapped[str] = mapped_column("ticket_id", String, index=True, nullable=False, default=None, primary_key=False, unique=False)
    ticket_status: Mapped[typing.Any] = mapped_column("ticket_status", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    ticket_state: Mapped[typing.Any] = mapped_column("ticket_state", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    start_date: Mapped[typing.Optional[datetime.datetime]] = mapped_column("start_date", DateTime(timezone=True), index=False, nullable=True, default=None, primary_key=False, unique=False)
    end_date: Mapped[typing.Optional[datetime.datetime]] = mapped_column("end_date", DateTime(timezone=True), index=False, nullable=True, default=None, primary_key=False, unique=False)
    summary: Mapped[str] = mapped_column("summary", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    description: Mapped[str] = mapped_column("description", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    ticket_severity: Mapped[typing.Any] = mapped_column("ticket_severity", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    ticket_history: Mapped[typing.Optional[typing.List[typing.Any]]] = mapped_column("ticket_history", JSONB, index=False, nullable=True, default=None, primary_key=False, unique=False)
    merge_history: Mapped[typing.Optional[typing.List[typing.Any]]] = mapped_column("merge_history", JSONB, index=False, nullable=True, default=None, primary_key=False, unique=False)
    file_attachment: Mapped[typing.Optional[typing.List[str]]] = mapped_column("file_attachment", ARRAY(String), index=False, nullable=True, default="", primary_key=False, unique=False)
    file_attachment_name: Mapped[typing.Optional[str]] = mapped_column("file_attachment_name", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    file_attachment_id: Mapped[typing.Optional[str]] = mapped_column("file_attachment_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    comment_text: Mapped[typing.Optional[str]] = mapped_column("comment_text", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    comment_id: Mapped[typing.Optional[str]] = mapped_column("comment_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    comment_attachment_path: Mapped[typing.Optional[str]] = mapped_column("comment_attachment_path", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    merge_status: Mapped[typing.Optional[bool]] = mapped_column("merge_status", Boolean, index=False, nullable=True, default=False, primary_key=False, unique=False)
    assignee: Mapped[typing.Optional[str]] = mapped_column("assignee", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    created_by: Mapped[typing.Optional[str]] = mapped_column("created_by", String, index=False, nullable=True, default="", primary_key=False, unique=False)

    __table_args__ = (UniqueConstraint(ticket_id, name="ticketing_ticket_id"),)


class TicketingCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'ticketing'
    
    ticket_name: typing.Optional[str] = pydantic.Field("", **{})
    ticket_id: str
    ticket_status: ticketing_enum.Status
    ticket_state: ticketing_enum.State
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None
    summary: str
    description: str
    ticket_severity: ticketing_enum.Severity
    ticket_history: typing.Optional[typing.List[Ticket_HistoryCreate]] | None = None
    merge_history: typing.Optional[typing.List[Merge_HistoryCreate]] | None = None
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    file_attachment_name: typing.Optional[str] = pydantic.Field("", **{})
    file_attachment_id: typing.Optional[str] = pydantic.Field("", **{})
    comment_text: typing.Optional[str] = pydantic.Field("", **{})
    comment_id: typing.Optional[str] = pydantic.Field("", **{})
    comment_attachment_path: typing.Optional[str] = pydantic.Field("", **{})
    merge_status: typing.Optional[bool] = pydantic.Field(False, )
    assignee: typing.Optional[str] = pydantic.Field("", **{})
    created_by: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = TicketingSchema
        upsert_keys = ['ticket_id']


class Ticketing(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'ticketing'
    
    ticket_name: typing.Optional[str] = pydantic.Field("", **{})
    ticket_id: typing.Optional[str] | None = None
    ticket_status: typing.Optional[ticketing_enum.Status] | None = None
    ticket_state: typing.Optional[ticketing_enum.State] | None = None
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None
    summary: typing.Optional[str] | None = None
    description: typing.Optional[str] | None = None
    ticket_severity: typing.Optional[ticketing_enum.Severity] | None = None
    ticket_history: typing.Optional[typing.List[Ticket_HistoryCreate]] | None = None
    merge_history: typing.Optional[typing.List[Merge_HistoryCreate]] | None = None
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    file_attachment_name: typing.Optional[str] = pydantic.Field("", **{})
    file_attachment_id: typing.Optional[str] = pydantic.Field("", **{})
    comment_text: typing.Optional[str] = pydantic.Field("", **{})
    comment_id: typing.Optional[str] = pydantic.Field("", **{})
    comment_attachment_path: typing.Optional[str] = pydantic.Field("", **{})
    merge_status: typing.Optional[bool] = pydantic.Field(False, )
    assignee: typing.Optional[str] = pydantic.Field("", **{})
    created_by: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = TicketingSchema
        upsert_keys = ['ticket_id']


class TicketingGetResp(pydantic.BaseModel):
    data: typing.List[Ticketing]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class TicketingCreateTicketParams(pydantic.BaseModel):
    ticket_state: ticketing_enum.State
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None
    summary: str
    description: str
    ticket_severity: ticketing_enum.Severity
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    comment_text: typing.Optional[str] = pydantic.Field("", **{})
    assignee: typing.Optional[str] = pydantic.Field("", **{})
    created_by: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingUpdateTicketParams(pydantic.BaseModel):
    update_id: str
    ticket_state: ticketing_enum.State
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None
    summary: str
    description: str
    ticket_severity: ticketing_enum.Severity
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    comment_text: typing.Optional[str] = pydantic.Field("", **{})
    merge_status: typing.Optional[bool] = pydantic.Field(False, )
    assignee: typing.Optional[str] = pydantic.Field("", **{})
    created_by: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingAttachFileParams(pydantic.BaseModel):
    ticket_id: typing.Optional[str] = pydantic.Field("", **{})
    tid: typing.Optional[str] = pydantic.Field("", **{})
    file_path: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingGetTicketIdParams(pydantic.BaseModel):
    ticket_id: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
