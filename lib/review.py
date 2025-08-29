from __init__ import CONN, CURSOR

class Review:
    all = {} 

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review id={self.id} year={self.year} employee_id={self.employee_id} summary={self.summary!r}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()
        cls.all.clear()

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("year must be an int >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("summary must be a non-empty string")
        self._summary = value.strip()

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("employee_id must be an integer")
        from employee import Employee 
        if Employee.find_by_id(value) is None:
            raise ValueError("employee_id must refer to a persisted Employee")
        self._employee_id = value

    def save(self):
        if self.id is not None:
            return self.update()
        CURSOR.execute(
            "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
            (self.year, self.summary, self.employee_id)
        )
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
        return self

    @classmethod
    def create(cls, year, summary, employee_id):
        inst = cls(year, summary, employee_id)
        inst.save()
        return inst

    @classmethod
    def instance_from_db(cls, row):
        if not row:
            return None
        rid, year, summary, employee_id = row
        if rid in cls.all:
            inst = cls.all[rid]
            inst._year = year
            inst._summary = summary
            inst._employee_id = employee_id
            return inst
        inst = cls(year, summary, employee_id, id=rid)
        cls.all[rid] = inst
        return inst

    @classmethod
    def find_by_id(cls, rid):
        CURSOR.execute("SELECT id, year, summary, employee_id FROM reviews WHERE id = ?", (rid,))
        return cls.instance_from_db(CURSOR.fetchone())

    def update(self):
        if self.id is None:
            raise ValueError("cannot update a review that has not been saved")
        CURSOR.execute(
            "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
            (self.year, self.summary, self.employee_id, self.id)
        )
        CONN.commit()
        type(self).all[self.id] = self
        return self

    def delete(self):
        if self.id is None:
            return
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        type(self).all.pop(self.id, None)
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT id, year, summary, employee_id FROM reviews")
        return [cls.instance_from_db(r) for r in CURSOR.fetchall()]
