class ValidationResult:
    """
    Stores the result of a validation process.
    """

    def __init__(self):

        self.is_valid = True

        self.errors = []

        self.warnings = []

        self.data = None

    def add_error(self, message):

        self.errors.append(message)

        self.is_valid = False

    def add_warning(self, message):

        self.warnings.append(message)