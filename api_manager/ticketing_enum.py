import enum


class Status(str, enum.Enum):
    OPEN = 'Open'
    PENDING = 'Pending'
    CLOSE = 'Close'


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


class TicketType(str, enum.Enum):
    TODO = 'TicketRaised'
    INPROGRESS = 'TicketInProgress'
    CANCELLED = 'TicketCancelled'
    RESOLVED = 'TicketResolved'
    ONHOLD = 'TicketOnHold'
