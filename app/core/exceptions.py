from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=303, detail=detail)

class AlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail)

class AlreadyBookedException(HTTPException):
    def __init__(self, detail: str = "Slot already booked"):
        super().__init__(status_code=409, detail=detail)
    
class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=403, detail=detail)
    
class AlreadyCancelledException(HTTPException):
    def __init__(self, detail: str = "Interview already cancelled"):
        super().__init__(status_code=400, detail=detail)

class InvalidSlotTimeException(HTTPException):
    def __init__(self, detail: str = "End time must be after start time"):
        super().__init__(status_code=400, detail=detail)

class SlotOverlapException(HTTPException):
    def __init__(self, detail: str = "Slot overlaps with an existing slot"):
        super().__init__(status_code=409, detail=detail)

class InvalidStatusTransitionException(HTTPException):
    def __init__(self, detail: str = "Invalid status transition"):
        super().__init__(status_code=400, detail=detail)