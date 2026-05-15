import pymysql
from persistence.db import get_connection


class Word:
    def __init__(self, id: int, word: str, phrase: str):
        self.id = id
        self.word = word
        self.phrase = phrase


    @classmethod
    def wordbyId(cls,id):
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT id, word, phrase FROM words WHERE id = %s"
        cursor.execute(sql, (id,))

        row = cursor.fetchone()
        print(f"Buscando ID {id}...") # Debug
        print(f"Resultado de la DB: {row}") # Debug

        cursor.close()
        connection.close()

        if row:
            return cls(row['id'], row['word'], row['phrase'])
        else:
            return None


    @classmethod
    def list_ids(cls):
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT id FROM words ORDER BY id"
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return [r['id'] for r in rows]


    @classmethod
    def update_word(cls, id, word, phrase):
        try:
            connection = get_connection()
            cursor = connection.cursor()
            sql = "UPDATE words SET word = %s, phrase = %s WHERE id = %s"
            cursor.execute(sql, (word, phrase, id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error updating word: {ex}")
            return False
