import enum


class BusinessUnit(str, enum.Enum):
    TAS = 'TAS'
    LPG = 'LPG'
    RO = 'RO'
    RDI = 'RDI'
    CP = 'CP'
    CDCMS = 'CDCMS'
    ALL = 'ALL'


class Status(str, enum.Enum):
    OPEN = 'Open'
    CLOSE = 'Close'
    PENDING = 'Pending'


class State(str, enum.Enum):
    TODO = 'ToDo'
    INPROGRESS = 'InProgress'
    CANCELLED = 'Cancelled'
    RESOLVED = 'Resolved'
    ONHOLD = 'OnHold'


class Severity(str, enum.Enum):
    CRITICAL = 'Critical'
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'


class Assignee(str, enum.Enum):
    NOVEXSUPPORT = 'NovexSupport'
    TECHSUPPORT = 'TechSupport'


class TicketType(str, enum.Enum):
    TODO = 'TicketRaised'
    INPROGRESS = 'TicketInProgress'
    CANCELLED = 'TicketCancelled'
    RESOLVED = 'TicketResolved'
    ONHOLD = 'TicketOnHold'


class ContextType(str, enum.Enum):
    HPCL = 'Hpcl'
    RECON = 'Recon'
    DATAVALIDATION = 'DataValidation'
