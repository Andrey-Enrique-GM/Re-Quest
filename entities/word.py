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