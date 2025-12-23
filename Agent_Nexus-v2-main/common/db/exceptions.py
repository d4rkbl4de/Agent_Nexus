class DatabaseError(Exception):
    def __init__(self, message: str = "An internal database error occurred"):
        self.message = message
        super().__init__(self.message)

class RecordNotFoundError(DatabaseError):
    pass

class DuplicateEntryError(DatabaseError):
    pass

class IntegrityMappingError(DatabaseError):
    pass

class TransactionError(DatabaseError):
    pass

class VectorStoreError(DatabaseError):
    pass

class VectorDimensionMismatchError(VectorStoreError):
    pass

class CollectionNotFoundError(VectorStoreError):
    pass

class ConnectionTimeoutError(DatabaseError):
    pass