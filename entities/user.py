from persistence.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from enums.profile import Profile
import pymysql


class User(UserMixin):
    def __init__(self, id: int, name: str, email: str, password_hash: str,
                 profile: Profile, is_active: bool):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        # Si profile es int, convertir a Enum
        if isinstance(profile, Profile):
            self.profile = profile
        else:
            self.profile = Profile(profile)
        self._is_active = is_active


    # Propiedad para obtener el estado de cuenta del usuario (Activo o Inactivo)
    @property
    def is_active(self):
        return self._is_active


    # Metodo para verificar si el correo ya se encuentra registrado en la base de datos
    def check_email_exists(email) -> bool:
        """
            Verifica si la cuenta de correo electrónico ya se encuentra registrada.

            Parameters:
                email (str): Correo electrónico a validar.

            Returns:
                bool: True si el correo ya se encunetra registrado; de lo contrario, False.
        """
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT email from user WHERE email = %s"
        cursor.execute(sql, (email,))

        row = cursor.fetchone()

        cursor.close()
        connection.close()
        return row is not None
    
        
    # Metodo para guardar un nuevo usuario en la base de datos
    def save(name: str, email:str, password:str) -> bool:
        """
            Guarda un registro de usuario en la base de datos

            Parameters:
                name (str): Nombre del usuario.
                email (str): Correo electrónico del usuario.
                password (str): Contraseña del usuario en texto plano.

            Returns:
                bool: True si la cuenta se guardó correctamente; de lo contrario, False.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor()
            hash_password = generate_password_hash(password)

            sql = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, hash_password))
            connection.commit()

            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error saving user:{ex}")
            return False
        

    # Metodo para verificar las credenciales de inicio de sesión
    def check_login(email, password):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            

            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE email = %s"
            cursor.execute(sql, (email,))

            user = cursor.fetchone()
            
            cursor.close()
            connection.close()

            if user and check_password_hash(user["password"], password):
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    "",
                    user["profile"],
                    user["is_active"]
                )

            return None
        except Exception as ex:
            print(f"Error login user:{ex}")
            return False
        

    # Metodo para obtener un usuario por su ID
    def get_by_id(id):
            try:
                connection = get_connection()
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                
                sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE id = %s"
                cursor.execute(sql, (id,))

                user = cursor.fetchone()
                
                cursor.close()
                connection.close()

                if user:
                    return User(
                        user["id"],
                        user["name"],
                        user["email"],
                        user["password"],
                        user["profile"],
                        user["is_active"]
                    )

                return None
            except Exception as ex:
                print(f"Error login user:{ex}")
                return False
