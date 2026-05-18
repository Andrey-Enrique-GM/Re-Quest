from typing import Optional
import pymysql
from persistence.db import get_connection


class Winner:
    """Representa el registro de puntaje de un usuario al completar el juego."""
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

    @classmethod
    def get_winners(cls) -> list:
        """
            Obtiene una lista de los ganadores ordenados por puntaje de mayor a menor.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = """
                SELECT w.id, w.score, w.id_user, u.name 
                FROM winners w 
                JOIN user u ON w.id_user = u.id 
                ORDER BY w.score DESC
            """
            cursor.execute(sql)
            winners = cursor.fetchall()
            return winners
        except Exception as e:
            print(f"Error al obtener los ganadores: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def get_user_best_score(cls, id_user: int) -> Optional[int]:
        """
            Obtiene el mejor puntaje registrado para un usuario específico.

            Parameters:
                id_user (int): El ID del usuario.

            Returns:
                Optional[int]: El mejor puntaje del usuario o None si no tiene registros.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT score FROM winners WHERE id_user = %s"
            cursor.execute(sql, (id_user,))
            row = cursor.fetchone()

            return row['score'] if row else None
        except Exception as e:
            print(f"Error al obtener el mejor puntaje del usuario: {e}")
            return None
        finally:
            cursor.close()
            connection.close()