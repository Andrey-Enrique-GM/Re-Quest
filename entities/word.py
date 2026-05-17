import pymysql
from persistence.db import get_connection


# Clase para representar una palabra y su frase asociada
class Word:
    def __init__(self, id: int, word: str, phrase: str, character: str):
        self.id = id
        self.word = word
        self.phrase = phrase
        self.character = character


# Método para obtener una palabra por su ID
    @classmethod
    def wordbyId(cls, id: int):
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            sql = "SELECT id, word, phrase, character FROM words WHERE id = %s"
            cursor.execute(sql, (id,))
        except:
            # Fallback si la columna character no existe
            sql = "SELECT id, word, phrase FROM words WHERE id = %s"
            cursor.execute(sql, (id,))

        row = cursor.fetchone()
        print(f"Buscando ID {id}...") # Debug
        print(f"Resultado de la DB: {row}") # Debug

        cursor.close()
        connection.close()

        if row:
            # Si character existe en la fila, usarlo; si no, asignar según el ID
            if 'character' in row and row['character']:
                character = row['character']
            else:
                # Mapeo de IDs a caracteres como fallback
                character_map = {
                    1: 'ayame.png',
                    2: 'sayori.png',
                    3: 'rin.png',
                    4: 'shogunRaiden.png',
                    5: 'abo.png'
                }
                character = character_map.get(id, 'ayame.png')
            
            return cls(row['id'], row['word'], row['phrase'], character)
        else:
            return None


# Método para listar todos los IDs de palabras disponibles
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


# Método para actualizar una palabra y su frase por ID
    @classmethod
    def update_word(cls, id: int, word: str, phrase: str, character: str = None):
        try:
            connection = get_connection()
            cursor = connection.cursor()
            sql = "UPDATE words SET word = %s, phrase = %s WHERE id = %s"
            cursor.execute(sql, (word, phrase, id))
            
            # Intentar actualizar character si la columna existe
            if character is not None:
                try:
                    sql = "UPDATE words SET character = %s WHERE id = %s"
                    cursor.execute(sql, (character, id))
                except:
                    pass  # Ignorar si la columna no existe
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error updating word: {ex}")
            return False
