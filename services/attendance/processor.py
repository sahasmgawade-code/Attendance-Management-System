class AttendanceProcessor:
    """
    Processes attendance using the validated
    Morning and Afternoon batch data.
    """

    def __init__(self, master_students, morning_students, afternoon_students):

        self.master_students = master_students
        self.morning_students = morning_students
        self.afternoon_students = afternoon_students

    def process(self):

        attendance_result = []

        # Create lookup sets for fast searching
        morning_set = {
            self._normalize(student["Student Name"])
            for student in self.morning_students
        }

        afternoon_set = {
            self._normalize(student["Student Name"])
            for student in self.afternoon_students
        }

        for student in self.master_students:

            name = self._normalize(student["Student Name"])

            present_morning = name in morning_set
            present_afternoon = name in afternoon_set

            status = "P" if (present_morning and present_afternoon) else "A"

            attendance_result.append(
                {
                    **student,
                    "Status": status
                }
            )

        return attendance_result

    @staticmethod
    def _normalize(name):

        words = str(name).strip().lower().split()
        return frozenset(words)