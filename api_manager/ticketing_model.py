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
    project_id: Mapped[typing.Optional[str]] = mapped_column("project_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    board_id: Mapped[typing.Optional[str]] = mapped_column("board_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    workflow_id: Mapped[typing.Optional[str]] = mapped_column("workflow_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    status_id: Mapped[typing.Optional[str]] = mapped_column("status_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    ticket_status: Mapped[typing.Any] = mapped_column("ticket_status", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    ticket_state: Mapped[typing.Any] = mapped_column("ticket_state", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    ticket_severity: Mapped[typing.Any] = mapped_column("ticket_severity", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    summary: Mapped[typing.Optional[str]] = mapped_column("summary", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    description: Mapped[typing.Optional[str]] = mapped_column("description", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    comment: Mapped[typing.Optional[str]] = mapped_column("comment", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    file_attachment: Mapped[typing.Optional[typing.List[str]]] = mapped_column("file_attachment", ARRAY(String), index=False, nullable=True, default="", primary_key=False, unique=False)
    file_attachment_name: Mapped[typing.Optional[str]] = mapped_column("file_attachment_name", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    file_attachment_id: Mapped[typing.Optional[str]] = mapped_column("file_attachment_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    merge_status: Mapped[typing.Optional[bool]] = mapped_column("merge_status", Boolean, index=False, nullable=True, default=False, primary_key=False, unique=False)
    milestone_id: Mapped[typing.Optional[str]] = mapped_column("milestone_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    assignee_id: Mapped[typing.Optional[str]] = mapped_column("assignee_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    reporter_id: Mapped[typing.Optional[str]] = mapped_column("reporter_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    parent_ticket_id: Mapped[typing.Optional[str]] = mapped_column("parent_ticket_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    estimated_hours: Mapped[typing.Optional[datetime.datetime]] = mapped_column("estimated_hours", DateTime(timezone=True), index=False, nullable=True, default=None, primary_key=False, unique=False)
    total_hours_spent: Mapped[typing.Optional[datetime.datetime]] = mapped_column("total_hours_spent", DateTime(timezone=True), index=False, nullable=True, default=None, primary_key=False, unique=False)
    due_date: Mapped[typing.Optional[datetime.datetime]] = mapped_column("due_date", DateTime(timezone=True), index=False, nullable=True, default=None, primary_key=False, unique=False)
    start_date: Mapped[typing.Optional[datetime.datetime]] = mapped_column("start_date", DateTime(timezone=True), index=False, nullable=True, default=None, primary_key=False, unique=False)
    end_date: Mapped[typing.Optional[datetime.datetime]] = mapped_column("end_date", DateTime(timezone=True), index=False, nullable=True, default=None, primary_key=False, unique=False)

    __table_args__ = (UniqueConstraint(ticket_id, name="ticketing_ticket_id"),)


class TicketingCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'ticketing'
    
    ticket_name: typing.Optional[str] = pydantic.Field("", **{})
    ticket_id: str
    project_id: typing.Optional[str] = pydantic.Field("", **{})
    board_id: typing.Optional[str] = pydantic.Field("", **{})
    workflow_id: typing.Optional[str] = pydantic.Field("", **{})
    status_id: typing.Optional[str] = pydantic.Field("", **{})
    ticket_status: ticketing_enum.Status
    ticket_state: ticketing_enum.State
    ticket_severity: ticketing_enum.Severity
    summary: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    comment: typing.Optional[str] = pydantic.Field("", **{})
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    file_attachment_name: typing.Optional[str] = pydantic.Field("", **{})
    file_attachment_id: typing.Optional[str] = pydantic.Field("", **{})
    merge_status: typing.Optional[bool] = pydantic.Field(False, )
    milestone_id: typing.Optional[str] = pydantic.Field("", **{})
    assignee_id: typing.Optional[str] = pydantic.Field("", **{})
    reporter_id: typing.Optional[str] = pydantic.Field("", **{})
    parent_ticket_id: typing.Optional[str] = pydantic.Field("", **{})
    estimated_hours: typing.Optional[datetime.datetime] | None = None
    total_hours_spent: typing.Optional[datetime.datetime] | None = None
    due_date: typing.Optional[datetime.datetime] | None = None
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None

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
    project_id: typing.Optional[str] = pydantic.Field("", **{})
    board_id: typing.Optional[str] = pydantic.Field("", **{})
    workflow_id: typing.Optional[str] = pydantic.Field("", **{})
    status_id: typing.Optional[str] = pydantic.Field("", **{})
    ticket_status: typing.Optional[ticketing_enum.Status] | None = None
    ticket_state: typing.Optional[ticketing_enum.State] | None = None
    ticket_severity: typing.Optional[ticketing_enum.Severity] | None = None
    summary: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    comment: typing.Optional[str] = pydantic.Field("", **{})
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    file_attachment_name: typing.Optional[str] = pydantic.Field("", **{})
    file_attachment_id: typing.Optional[str] = pydantic.Field("", **{})
    merge_status: typing.Optional[bool] = pydantic.Field(False, )
    milestone_id: typing.Optional[str] = pydantic.Field("", **{})
    assignee_id: typing.Optional[str] = pydantic.Field("", **{})
    reporter_id: typing.Optional[str] = pydantic.Field("", **{})
    parent_ticket_id: typing.Optional[str] = pydantic.Field("", **{})
    estimated_hours: typing.Optional[datetime.datetime] | None = None
    total_hours_spent: typing.Optional[datetime.datetime] | None = None
    due_date: typing.Optional[datetime.datetime] | None = None
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None

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
    project_id: typing.Optional[str] = pydantic.Field("", **{})
    board_id: typing.Optional[str] = pydantic.Field("", **{})
    workflow_id: typing.Optional[str] = pydantic.Field("", **{})
    status_id: typing.Optional[str] = pydantic.Field("", **{})
    ticket_state: ticketing_enum.State
    ticket_severity: ticketing_enum.Severity
    summary: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    comment: typing.Optional[str] = pydantic.Field("", **{})
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    assignee_id: typing.Optional[str] = pydantic.Field("", **{})
    reporter_id: typing.Optional[str] = pydantic.Field("", **{})
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingAttachFileParams(pydantic.BaseModel):
    ticket_id: typing.Optional[str] = pydantic.Field("", **{})
    file_path: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingUpdateTicketParams(pydantic.BaseModel):
    update_id: str
    ticket_state: ticketing_enum.State
    ticket_severity: ticketing_enum.Severity
    summary: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    comment: typing.Optional[str] = pydantic.Field("", **{})
    merge_status: typing.Optional[bool] = pydantic.Field(False, )
    file_attachment: typing.Optional[typing.List[str]] = pydantic.Field("", **{})
    reporter_id: typing.Optional[str] = pydantic.Field("", **{})
    assignee_id: typing.Optional[str] = pydantic.Field("", **{})
    start_date: typing.Optional[datetime.datetime] | None = None
    end_date: typing.Optional[datetime.datetime] | None = None

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketHistorySchema(UrdhvaPostgresBase):
    __tablename__ = 'ticket_history'
    
    ticket_id: Mapped[typing.Optional[int]] = mapped_column("ticket_id", Integer, ForeignKey('ticketing.id'), index=False, nullable=True, default=None, primary_key=False, unique=False)
    changed_by: Mapped[typing.Optional[str]] = mapped_column("changed_by", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    field_name: Mapped[typing.Optional[str]] = mapped_column("field_name", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    old_value: Mapped[typing.Optional[str]] = mapped_column("old_value", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    new_value: Mapped[typing.Optional[str]] = mapped_column("new_value", String, index=False, nullable=True, default="", primary_key=False, unique=False)


class TicketHistoryCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'ticket_history'
    
    ticket_id: typing.Optional[int] = pydantic.Field(0, **{})
    changed_by: typing.Optional[str] = pydantic.Field("", **{})
    field_name: typing.Optional[str] = pydantic.Field("", **{})
    old_value: typing.Optional[str] = pydantic.Field("", **{})
    new_value: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = TicketHistorySchema
        upsert_keys = []


class TicketHistory(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'ticket_history'
    
    ticket_id: typing.Optional[int] = pydantic.Field(0, **{})
    changed_by: typing.Optional[str] = pydantic.Field("", **{})
    field_name: typing.Optional[str] = pydantic.Field("", **{})
    old_value: typing.Optional[str] = pydantic.Field("", **{})
    new_value: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = TicketHistorySchema
        upsert_keys = []


class TicketHistoryGetResp(pydantic.BaseModel):
    data: typing.List[TicketHistory]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class TickethistoryCreateHistoryParams(pydantic.BaseModel):
    ticket_id: typing.Optional[int] = pydantic.Field(0, **{})
    changed_by: typing.Optional[str] = pydantic.Field("", **{})
    field_name: typing.Optional[str] = pydantic.Field("", **{})
    old_value: typing.Optional[str] = pydantic.Field("", **{})
    new_value: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
