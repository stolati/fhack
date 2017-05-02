from StringIO import StringIO


class TextMap:
    def __init__(self):
        self.y_positions = [[]]

    def add(self, e):  # e is EMF Record
        x_positions = self.y_positions[-1]
        if not x_positions:
            # Most likely first record
            x_positions.append(e)
            return
        if abs(e.rclBounds_top - x_positions[0].rclBounds_top) <= 2:
            if e.rclBounds_left >= x_positions[0].rclBounds_right:
                x_positions.append(e)
                return
            return self.insert_correct_x(e, x_positions)
        if e.rclBounds_top > x_positions[0].rclBounds_top:
            self.y_positions.append([e])
            return
        return self.insert_correct_y(e, self.y_positions)

    def insert_correct_y(self, e, y_positions):
        for x_positions in reversed(y_positions):
            if e.rclBounds_top < x_positions[0].rclBounds_top:
                self.insert_correct_x(e, x_positions)
                return

    def insert_correct_x(self, e, x_positions):
        for (i, record) in enumerate(x_positions):
            if e.rclBounds_left <= record.rclBounds_left:
                x_positions.insert(i, e)
                return

    def __str__(self):

        x_per_character = self.character_width() or 13
        txt = StringIO()
        for x_positions in self.y_positions:  # Extract all records at same vertical position
            txt.write("\n")
            previous_e = None
            for e in x_positions:  # Iterate through records in the same line
                if previous_e:
                    txt.write(" " *
                              ((e.rclBounds_left - previous_e.rclBounds_right) / x_per_character))
                previous_e = e
                txt.write(self.get_string(e))
        return txt.getvalue()

    def get_string(self, e):  # e is emf record
        txt = StringIO()
        if e.charsize == 2:
            txt.write(str(e.string.decode('utf-16le')))
        else:
            txt.write(str(e.string))

        return txt.getvalue()

    def character_width(self):
        for num_chars in range(10, -1, -1):
            for x_positions in self.y_positions:
                for e in x_positions:
                    # Look for a string with at least num_chars characters in order to determine width per character
                    if len(self.get_string(e)) > num_chars:
                        x_pixels = e.rclBounds_right - e.rclBounds_left
                        return x_pixels/len(self.get_string(e))

        return 0
