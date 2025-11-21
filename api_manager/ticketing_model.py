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


class TicketingDeleteTicketParams(pydantic.BaseModel):
    delete_id: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingAttachFileParams(pydantic.BaseModel):
    ticket_id: typing.Optional[str] = pydantic.Field("", **{})
    file_path: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingDeleteFileAttachmentParams(pydantic.BaseModel):
    ticket_id: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingDragCardParams(pydantic.BaseModel):
    ticket_id: str
    ticket_state: ticketing_enum.State

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingUpdateAssigneeParams(pydantic.BaseModel):
    ticket_id: str
    assignee: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingUpdateReporterParams(pydantic.BaseModel):
    ticket_id: str
    reporter_name: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingAddCommentToTicketParams(pydantic.BaseModel):
    ticket_id: str
    comment_text: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingEditCommentParams(pydantic.BaseModel):
    ticket_id: str
    existing_comment_text: str
    comment_id: str
    new_comment: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class TicketingDeleteCommentParams(pydantic.BaseModel):
    ticket_id: str
    comment_id: str
    existing_comment_text: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class ZoneSchema(UrdhvaPostgresBase):
    __tablename__ = 'zone'
    
    zone_name: Mapped[str] = mapped_column("zone_name", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    zone_short_name: Mapped[str] = mapped_column("zone_short_name", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    zone_id: Mapped[typing.Optional[str]] = mapped_column("zone_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)

    __table_args__ = (UniqueConstraint(zone_name, zone_short_name, name="zone_zone_name_zone_short_name"),)


class ZoneCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'zone'
    
    zone_name: str
    zone_short_name: str
    zone_id: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = ZoneSchema
        upsert_keys = ['zone_name', 'zone_short_name']


class Zone(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'zone'
    
    zone_name: typing.Optional[str] | None = None
    zone_short_name: typing.Optional[str] | None = None
    zone_id: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = ZoneSchema
        upsert_keys = ['zone_name', 'zone_short_name']


class ZoneGetResp(pydantic.BaseModel):
    data: typing.List[Zone]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class ZoneAddNewZoneParams(pydantic.BaseModel):
    zone_name: str
    zone_short_name: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class RegionSchema(UrdhvaPostgresBase):
    __tablename__ = 'region'
    
    region_name: Mapped[str] = mapped_column("region_name", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    region_short_name: Mapped[str] = mapped_column("region_short_name", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    region_id: Mapped[typing.Optional[str]] = mapped_column("region_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)


class RegionCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'region'
    
    region_name: str
    region_short_name: str
    region_id: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = RegionSchema
        upsert_keys = []


class Region(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'region'
    
    region_name: typing.Optional[str] | None = None
    region_short_name: typing.Optional[str] | None = None
    region_id: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = RegionSchema
        upsert_keys = []


class RegionGetResp(pydantic.BaseModel):
    data: typing.List[Region]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class RegionAddNewRegionParams(pydantic.BaseModel):
    region_name: str
    region_short_name: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class MasterDataSchema(UrdhvaPostgresBase):
    __tablename__ = 'master_data'
    
    name: Mapped[str] = mapped_column("name", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    description: Mapped[str] = mapped_column("description", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    value: Mapped[str] = mapped_column("value", String, index=False, nullable=False, default=None, primary_key=False, unique=False)

    __table_args__ = (UniqueConstraint(value, name="master_data_value"),)


class MasterDataCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'master_data'
    
    name: str
    description: str
    value: str

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = MasterDataSchema
        upsert_keys = ['value']


class MasterData(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'master_data'
    
    name: typing.Optional[str] | None = None
    description: typing.Optional[str] | None = None
    value: typing.Optional[str] | None = None

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = MasterDataSchema
        upsert_keys = ['value']


class MasterDataGetResp(pydantic.BaseModel):
    data: typing.List[MasterData]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class MasterdataAddNewDataParams(pydantic.BaseModel):
    name: str
    description: str
    value: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class MasterdataUpdateDataParams(pydantic.BaseModel):
    md_id: str
    name: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    value: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class MasterdataDeleteDataParams(pydantic.BaseModel):
    md_id: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class WorkflowSchema(UrdhvaPostgresBase):
    __tablename__ = 'workflow'
    
    workflow_name: Mapped[str] = mapped_column("workflow_name", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    created_by: Mapped[str] = mapped_column("created_by", String, index=False, nullable=False, default=None, primary_key=False, unique=False)

    __table_args__ = (UniqueConstraint(workflow_name, name="workflow_workflow_name"),)


class WorkflowCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'workflow'
    
    workflow_name: str
    created_by: str

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = WorkflowSchema
        upsert_keys = ['workflow_name']


class Workflow(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'workflow'
    
    workflow_name: typing.Optional[str] | None = None
    created_by: typing.Optional[str] | None = None

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = WorkflowSchema
        upsert_keys = ['workflow_name']


class WorkflowGetResp(pydantic.BaseModel):
    data: typing.List[Workflow]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class WorkflowAddWorkflowParams(pydantic.BaseModel):
    workflow_name: str
    created_by: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class WorkflowUpdateWorkflowParams(pydantic.BaseModel):
    workflow_id: str
    workflow_name: str
    created_by: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class WorkflowDeleteWorkflowParams(pydantic.BaseModel):
    workflow_id: int

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class orderCreate(pydantic.BaseModel):
    ticket_state: str
    ticket_status: str


class WorkflowStatusSchema(UrdhvaPostgresBase):
    __tablename__ = 'workflow_status'
    
    workflow_id: Mapped[int] = mapped_column("workflow_id", Integer, ForeignKey('workflow.id'), index=False, nullable=False, default=None, primary_key=False, unique=False)
    ticket_state: Mapped[str] = mapped_column("ticket_state", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    ticket_status: Mapped[str] = mapped_column("ticket_status", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    order_no: Mapped[int] = mapped_column("order_no", Integer, index=False, nullable=False, default=None, primary_key=False, unique=False)


class WorkflowStatusCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'workflow_status'
    
    workflow_id: int
    ticket_state: str
    ticket_status: str
    order_no: int

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = WorkflowStatusSchema
        upsert_keys = []


class WorkflowStatus(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'workflow_status'
    
    workflow_id: typing.Optional[int] | None = None
    ticket_state: typing.Optional[str] | None = None
    ticket_status: typing.Optional[str] | None = None
    order_no: typing.Optional[int] | None = None

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = WorkflowStatusSchema
        upsert_keys = []


class WorkflowStatusGetResp(pydantic.BaseModel):
    data: typing.List[WorkflowStatus]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class WorkflowstatusUpdateOrderParams(pydantic.BaseModel):
    workflow_id: int
    workflow_order: typing.List[orderCreate]

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class BoardsSchema(UrdhvaPostgresBase):
    __tablename__ = 'boards'
    
    workflow_id: Mapped[int] = mapped_column("workflow_id", Integer, ForeignKey('workflow.id'), index=False, nullable=False, default=None, primary_key=False, unique=False)
    board_name: Mapped[str] = mapped_column("board_name", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    board_owner: Mapped[str] = mapped_column("board_owner", String, index=False, nullable=False, default=None, primary_key=False, unique=False)

    __table_args__ = (UniqueConstraint(board_name, name="boards_board_name"),)


class BoardsCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'boards'
    
    workflow_id: int
    board_name: str
    board_owner: str

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = BoardsSchema
        upsert_keys = ['board_name']


class Boards(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'boards'
    
    workflow_id: typing.Optional[int] | None = None
    board_name: typing.Optional[str] | None = None
    board_owner: typing.Optional[str] | None = None

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = BoardsSchema
        upsert_keys = ['board_name']


class BoardsGetResp(pydantic.BaseModel):
    data: typing.List[Boards]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class BoardsAddBoardParams(pydantic.BaseModel):
    workflow_id: int
    board_name: str
    board_owner: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class BoardsUpdateBoardParams(pydantic.BaseModel):
    board_id: str
    workflow_id: typing.Optional[int] = pydantic.Field(0, **{})
    board_name: typing.Optional[str] = pydantic.Field("", **{})
    board_owner: typing.Optional[str] = pydantic.Field("", **{})

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class BoardsDeleteBoardParams(pydantic.BaseModel):
    board_id: int

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields


class UsersSchema(UrdhvaPostgresBase):
    __tablename__ = 'users'
    
    user_id: Mapped[typing.Optional[str]] = mapped_column("user_id", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    first_name: Mapped[typing.Optional[str]] = mapped_column("first_name", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    last_name: Mapped[typing.Optional[str]] = mapped_column("last_name", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    email: Mapped[str] = mapped_column("email", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    password: Mapped[str] = mapped_column("password", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    phone_number: Mapped[typing.Optional[str]] = mapped_column("phone_number", String, index=False, nullable=True, default="", primary_key=False, unique=False)
    role: Mapped[str] = mapped_column("role", String, index=False, nullable=False, default=None, primary_key=False, unique=False)
    is_active: Mapped[bool] = mapped_column("is_active", Boolean, index=False, nullable=False, default=None, primary_key=False, unique=False)

    __table_args__ = (UniqueConstraint(email, name="users_email"),)


class UsersCreate(urdhva_base.postgresmodel.BasePostgresModel):
    __tablename__ = 'users'
    
    user_id: typing.Optional[str] = pydantic.Field("", **{})
    first_name: typing.Optional[str] = pydantic.Field("", **{})
    last_name: typing.Optional[str] = pydantic.Field("", **{})
    email: str
    password: str
    phone_number: typing.Optional[str] = pydantic.Field("", **{})
    role: str
    is_active: bool

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = UsersSchema
        upsert_keys = ['email']


class Users(urdhva_base.postgresmodel.PostgresModel):
    __tablename__ = 'users'
    
    user_id: typing.Optional[str] = pydantic.Field("", **{})
    first_name: typing.Optional[str] = pydantic.Field("", **{})
    last_name: typing.Optional[str] = pydantic.Field("", **{})
    email: typing.Optional[str] | None = None
    password: typing.Optional[str] | None = None
    phone_number: typing.Optional[str] = pydantic.Field("", **{})
    role: typing.Optional[str] | None = None
    is_active: typing.Optional[bool] | None = None

    class Config:
        collection_name = 'data_flow'
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
        schema_class = UsersSchema
        upsert_keys = ['email']


class UsersGetResp(pydantic.BaseModel):
    data: typing.List[Users]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class UsersAddUserParams(pydantic.BaseModel):
    email: typing.List[str]
    role: str

    class Config:
        if urdhva_base.settings.disable_api_extra_inputs:
            extra = "forbid"  # Disallow extra fields
