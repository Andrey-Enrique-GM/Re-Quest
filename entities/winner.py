from typing import Optional
import pymysql
from persistence.db import get_connection


class Winner:
    def __init__(self, id: Optional[int], score: int, id_user: int):
        self.id = id
        self.score = score
        self.id_user = id_user


    def save(self) -> bool:
        """
            Guarda o actualiza el registro del ganador en la base de datos.
            Si el usuario ya tiene una fila en la tabla winners, suma el puntaje nuevo
            al puntaje que ya tenía registrado.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql_select = "SELECT score FROM winners WHERE id_user = %s"
            cursor.execute(sql_select, (self.id_user,))
            row = cursor.fetchone()

            if row:
                new_score = row['score'] + self.score
                sql_update = "UPDATE winners SET score = %s WHERE id_user = %s"
                cursor.execute(sql_update, (new_score, self.id_user))
            else:
                if self.id is None:
                    sql_insert = "INSERT INTO winners (score, id_user) VALUES (%s, %s)"
                    cursor.execute(sql_insert, (self.score, self.id_user))
                else:
                    sql_insert = "INSERT INTO winners (id, score, id_user) VALUES (%s, %s, %s)"
                    cursor.execute(sql_insert, (self.id, self.score, self.id_user))

            connection.commit()
            return True
        except Exception as e:
            print(f"Error al guardar el ganador: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
