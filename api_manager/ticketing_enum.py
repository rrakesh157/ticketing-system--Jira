import enum


class Status(str, enum.Enum):
    OPEN = 'Open'
    PENDING = 'Pending'
    CLOSE = 'Close'


class State(str, enum.Enum):
    TODO = 'ToDo'
    IN = 'in'
    PROGRESS = 'In Progress'
    CANCELLED = 'Cancelled'
    RESOLVED = 'Resolved'
    ON = 'on'
    HOLD = 'On Hold'
    RE = 're'
    OPEN = 'Re Open'


class Severity(str, enum.Enum):
    CRITICAL = 'Critical'
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'


class TicketType(str, enum.Enum):
    TODO = 'TicketRaised'
    IN = 'in'
    PROGRESS = 'TicketInProgress'
    CANCELLED = 'TicketCancelled'
    RESOLVED = 'TicketResolved'
    ON = 'on'
    HOLD = 'TicketOnHold'
    RE = 're'
    OPEN = 'TicketReOpened'
