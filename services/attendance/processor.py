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

        # Match by URN, not name, so duplicate-named
        # students are never conflated with each other
        morning_urns = {
            str(student["URN"]).strip()
            for student in self.morning_students
            if student.get("URN") not in (None, "")
        }

        afternoon_urns = {
            str(student["URN"]).strip()
            for student in self.afternoon_students
            if student.get("URN") not in (None, "")
        }

        for student in self.master_students:

            urn = str(student.get("URN", "")).strip()

            present_morning = urn in morning_urns
            present_afternoon = urn in afternoon_urns

            status = "P" if (present_morning and present_afternoon) else "A"

            attendance_result.append(
                {
                    **student,
                    "Status": status
                }
            )

        return attendance_result