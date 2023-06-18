import mysql.connector
import pymysql.err

class Crud:
    def __init__(self, name):
        self.table_name = name
        
    def connect(self):
        try:
            con = mysql.connector.connect(
                host = 'containers-us-west-51.railway.app',
                port = 7905,
                user = 'root',
                password = 'o2ujFD2j5g889iHzkIOI',
                database = 'railway'
            )
            return con
        except mysql.connector.Error as ex:
            print(ex, "\nFailed to connect.")
            return None
        
    def string_insert(self, colunas):
        sql_string = f"INSERT INTO {self.table_name} ("
        for i in range(len(colunas)):
            sql_string += colunas[i]
            if i == len(colunas) - 1:
                sql_string += ") "
                break
            sql_string += ","
        sql_string += "VALUES ("
        for i in range(len(colunas)):
            sql_string += "%s"
            if i == len(colunas) - 1:
                sql_string += ")"
                break
            sql_string += ","
        return sql_string
        
    def insert(self, colunas, valores):
        try:
            con = self.connect()
            sql_string = self.string_insert(colunas)
            print(sql_string)
            p_state = con.cursor(prepared=True)
            p_state.execute(sql_string, valores)
            con.commit()
            print("inserted")
        except mysql.connector.Error as e:
            print(e, "\nError on insert")
    
    def update_element(self, id_, colunas, valores, table_id):
        try:
            con = self.connect()
            sql_string = f"UPDATE {self.table_name} SET "
            for i in range(len(colunas)):
                sql_string += f"{colunas[i]} = %s "
                if i == len(colunas) - 1:
                    sql_string += ""
                    break
                sql_string += ","
            sql_string += f"WHERE {table_id} = %s"
            p_state = con.cursor(prepared=True)
            p_state.execute(sql_string, valores + [id_])
            con.commit()
            print("updated")
        except pymysql.err.MySQLError as e:
            print(e, "\nError on update")
        
    def delete_element(self, value, col):
        try:
            con = self.connect()
            sql_string = f"DELETE FROM {self.table_name} WHERE {col} = %s"
            p_state = con.cursor(prepared=True)
            p_state.execute(sql_string, [value])
            con.commit()
            print("deleted")
        except mysql.connector.Error as e:
            print(e, "\nError on delete")
    

    def get_all_elements(self):
        try:
            con = self.connect()
            sql_string = f"SELECT * FROM {self.table_name}"
            pstat = con.cursor(dictionary=True)
            pstat.execute(sql_string)
            return pstat.fetchall()
        except mysql.connector.Error as e:
            print(e, "\nError on get all elements")
            return None
        
    def get_element_by_pk(self, id_, table_id):
        try:
            con = self.connect()
            sql_string = f"SELECT * FROM {self.table_name} WHERE {table_id} = %s"
            p_state = con.cursor(prepared=True, dictionary=True)
            p_state.execute(sql_string, [id_])
            return p_state.fetchone()
        except mysql.connector.Error as e:
            print(e, "\nError on get element by PK")
            return None
        
    def get_elements_by_string_field(self, col, value):
        try:
            con = self.connect()
            sql_string = f"select * from {self.table_name} where {col} = %s"
            p_state = con.cursor(prepared=True, dictionary=True)
            p_state.execute(sql_string, (value,))
            res = p_state.fetchall()
            return res
        except mysql.connector.Error as e:
            print(e, "\nerror on database")
            return None

    #####

    def string_and_operator(self, colunas):
        sql_string = f"select * from {self.table_name} where "
        for i in range(len(colunas)):
            sql_string += colunas[i] + " = ?"
            if i != len(colunas) - 1:
                sql_string += " and "
        return sql_string

    def getElements_and_operator(self, col, value):
        try:
            con = self.connect()
            sql_string = self.string_and_operator(col)
            p_state = con.cursor(prepared=True, dictionary=True)
            print(sql_string)
            p_state.execute(sql_string, value)
            return p_state.fetchall()
        except pymysql.err.MySQLError as e:
            print(str(e) + "\nerror on database")
            return None

    def getElementsLike(self, col, value):
        try:
            con = self.connect()
            sql_string = f"select * from {self.table_name} where {col} like %s"
            wildcard_value = f"%{value}%"
            p_state = con.cursor(dictionary=True)
            p_state.execute(sql_string, (wildcard_value,))
            return p_state.fetchall()
        except pymysql.err.MySQLError as e:
            print(str(e) + "\nerror on getElementsLike")
            return None
    
    def get_tables(self):
        cnx = self.connect()
        cursor = cnx.cursor()
        query = "SHOW TABLES"
        cursor.execute(query)
        tables = cursor.fetchall()
        cursor.close()
        cnx.close()
        tables_name = []
        for table in tables:
            #print(table[0])
            tables_name.append(table[0])
        return tables_name

    def get_columns(self):
        cnx = self.connect()
        cursor = cnx.cursor()
        query = "DESCRIBE " + self.table_name
        cursor.execute(query)
        columns = cursor.fetchall()
        cursor.close()
        cnx.close()
        columns_name = []
        for column in columns:    
            columns_name.append(column[0])
        return columns_name

    def get_table_id_name(self):
        table_id = self.get_columns()
        return table_id[0]