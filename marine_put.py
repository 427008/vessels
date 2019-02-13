import sqlite3


class SQLiteBase:

    def __init__(self, path, file):
        self.connection_str = r'{0}/Data/{1}.sqlite'.format(path, file)


    def read_imo_list(self, timestamp=None):
        with sqlite3.connect(self.connection_str) as conn:
            cursor = conn.cursor()
            if timestamp is None:
                vessels_to_locate = r'SELECT imo FROM vessels_imo WHERE last_report_day=0'
                cursor.execute(vessels_to_locate)
            else:
                vessels_to_locate = r'SELECT imo FROM vessels_imo WHERE last_report_day<? and state<10'
                cursor.execute(vessels_to_locate, (timestamp, ))
            ret = [row[0].strip() for row in cursor.fetchall()]

        return ret


    def set_datestamp(self, imo, now_timestamp, vessel_data=None):
        with sqlite3.connect(self.connection_str) as conn:
            cursor = conn.cursor()
            if vessel_data is None:
                update_vessels = r'UPDATE vessels_imo SET last_report_day=?, state=state+1 WHERE imo=?'
                cursor.execute(update_vessels, (now_timestamp, imo))
            else:
                update_vessels = r'UPDATE vessels_imo SET area=?, deadweight=?, last_report_day=?, state=0 WHERE imo=?'
                cursor.execute(update_vessels, vessel_data + (now_timestamp, imo))
            conn.commit()


    def write_coordinates(self, vals):
        with sqlite3.connect(self.connection_str) as conn:
            cursor = conn.cursor()
            insert_vessels = r'INSERT INTO marinetraffic (imo, lat, lon, report_date, area, actuality_timestamp) ' \
                             r'VALUES(?, ?, ?, ?, ?, ?)'
            cursor.execute(insert_vessels, vals)
            conn.commit()
