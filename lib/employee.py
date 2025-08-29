from __init__ import CONN, CURSOR  
from department import Department  

class Employee:
    all = {} 

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee id={self.id} name={self.name!r} title={self.job_title!r} dept_id={self.department_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()
        cls.all.clear()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("name must be a non-empty string")
        self._name = value.strip()

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("job_title must be a non-empty string")
        self._job_title = value.strip()

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if not isinstance(value, int):
            raise ValueError("department_id must be an integer")
        
        if Department.find_by_id(value) is None:
            raise ValueError("department_id must refer to a persisted Department")
        self._department_id = value

    def save(self):
        if self.id is not None:
            return self.update()
        CURSOR.execute(
            "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)",
            (self.name, self.job_title, self.department_id)
        )
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
        return self

    @classmethod
    def create(cls, name, job_title, department_id):
        inst = cls(name, job_title, department_id)
        inst.save()
        return inst

    @classmethod
    def instance_from_db(cls, row):
        if not row:
            return None
        rid, name, job_title, department_id = row
        if rid in cls.all:
            inst = cls.all[rid]
            inst._name = name
            inst._job_title = job_title
            inst._department_id = department_id
            return inst
        inst = cls(name, job_title, department_id, id=rid)
        cls.all[rid] = inst
        return inst

    @classmethod
    def find_by_id(cls, rid):
        CURSOR.execute("SELECT id, name, job_title, department_id FROM employees WHERE id = ?", (rid,))
        return cls.instance_from_db(CURSOR.fetchone())

    @classmethod
    def find_by_name(cls, name):
        CURSOR.execute(
            "SELECT id, name, job_title, department_id FROM employees WHERE name = ? LIMIT 1",
            (name,)
        )
        return cls.instance_from_db(CURSOR.fetchone())

    def update(self):
        if self.id is None:
            raise ValueError("cannot update an employee that has not been saved")
        CURSOR.execute(
            "UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?",
            (self.name, self.job_title, self.department_id, self.id)
        )
        CONN.commit()
        type(self).all[self.id] = self
        return self

    def delete(self):
        if self.id is None:
            return
        CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
        CONN.commit()
        type(self).all.pop(self.id, None)
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT id, name, job_title, department_id FROM employees")
        return [cls.instance_from_db(r) for r in CURSOR.fetchall()]

    def reviews(self):
        from review import Review 
        if not getattr(self, "id", None):
            return []
        CURSOR.execute(
            "SELECT id, year, summary, employee_id FROM reviews WHERE employee_id = ?",
            (self.id,)
        )
        return [Review.instance_from_db(r) for r in CURSOR.fetchall()]
