import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt


class PandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class LoggerModel:
    def __init__(self, db_path='/home/andrew/Documents/database/records.db'):
        self.db_path = db_path
        # self._create_households_tables()

    def _create_households_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS households (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    household_name TEXT,
                    current_person INTEGER
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS active_household (
                    household_id INTEGER REFERENCES households(id),
                    name TEXT
                )
            ''')
            conn.commit()

    def register_household(self, household):
        if self.get_household_by_name(household.get_name().upper()):
            raise ValueError("A household with the same name already exists")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO households (household_name, current_person) VALUES (?, ?)', (household.get_name().upper(), household.get_num_person()))
            conn.commit()

    def delete_household(self, household_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM households WHERE id = ?', (household_id,))
            cursor.execute('DELETE FROM households_data WHERE household_id = ?', (household_id,))
            cursor.execute('DELETE FROM active_household WHERE household_id = ?', (household_id,))
            conn.commit()

    def get_household_by_name(self, household_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM households WHERE household_name = ?', (household_name,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                }
            return None

    def get_registered_households(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM households')
            results = cursor.fetchall()

            households = []
            for result in results:
                household = {
                    'id': result[0],
                    'name': result[1]
                }
                households.append(household)

            return households

    def get_registered_household_id(self, household_name: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM households WHERE household_name = ?', (household_name,))
            result = cursor.fetchone()

            if result:
                return result[0]

            return None

    def get_active_household(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM active_household')
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                }
            return None

    def save_active_household(self, active_household: dict):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM active_household')
            cursor.execute('''
                INSERT INTO active_household (household_id, name)
                VALUES (?, ?)
            ''', (active_household['id'], active_household['name']))

            conn.commit()

    def _get_temp_and_energy_data(self, household: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM sensor_data WHERE household = ?;"
            df = pd.read_sql_query(query, conn, params=(household, ))
            conn.commit()
            
            return df
        
    def get_all_data(self, household: str):
        df = self._get_temp_and_energy_data(household)
        data = df.groupby(['datetime'], as_index=False).agg(
            {"household":"last", "temperature":"sum", "energy":"sum", "person":"sum"}
        )
        return data
    
    def _get_time_one_hour_ago(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        formatted_result = one_hour_ago.strftime("%d/%m/%Y %H:%M")
        return formatted_result