from database import with_connection
import subprocess
import time
from functools import wraps

def back_menu(function):
    @wraps(function)
    def _back_menu(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except KeyboardInterrupt as err:
            return
    return _back_menu

def clear_and_print(message=None):
    subprocess.run(["clear"])
    if message:
        print(message)

@with_connection
def create_table(connection, *args, **kwargs):
    with connection.cursor() as cursor:
        query = """CREATE TABLE IF NOT EXISTS users(
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(50) NOT NULL UNIQUE
        )
        """
        cursor.execute(query)
        connection.commit()
        print("Tabla creada con exito")
        return True

@with_connection
def get_user(connection, *args, **kwargs):
    with connection.cursor() as cursor:
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (args[0],))
        result = cursor.fetchone()
        return result

@with_connection
def username_exist(connection, *args, **kwargs):
    with connection.cursor() as cursor:
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (args[0],))
        return False if cursor.fetchone() is None else True


@with_connection
def email_exist(connection, *args, **kwargs):
    with connection.cursor() as cursor:
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (args[0],))
        return False if cursor.fetchone() is None else True

@back_menu
@with_connection
def add_user(connection, *args, **kwargs):
    """Crear un nuevo usuario
Usa (CTRL + C) para volver
    """
    while True:
        clear_and_print(add_user.__doc__)
        username = input("Usuario: ")
        if len(username) == 0:
            print("Usuario requerido")
            time.sleep(1)
        elif username_exist(username):
            print("El usuario ya existe")
            time.sleep(1)
        else:
            email = input("Email: ")
            if len(email) == 0:
                print("Email requerido")
                time.sleep(1)
            elif email_exist(email):
                print("El email ya existe")
                time.sleep(1)
            else:
                break

    with connection.cursor() as cursor:
        query = "INSERT INTO users(username, email) VALUES(%s, %s)"
        cursor.execute(query, (username, email))
        connection.commit()
        clear_and_print()
        print("Usuario creado con exito!")
        time.sleep(1)
        return True
            

@back_menu
@with_connection
def get_all_users(connection):
    """Listado de usuarios
Usa (CTRL + C) para volver
    """
    clear_and_print(get_all_users.__doc__)
    with connection.cursor() as cursor:
        query = "SELECT * FROM users"
        cursor.execute(query)
        for user in cursor.fetchall():
            print("{} {} {}".format(*user))
        time.sleep(2)
        return True

@back_menu
@with_connection
def update_user(connection, *args, **kwargs):
    """Actualizar usuario
Usa (CTRL + C) para volver
    """
    # Busca a el usuario en la base de datos
    while True:
        try:
            clear_and_print(update_user.__doc__)
            id_user = int(input("Ingresa el id del usuario: "))
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE id=%s"
                cursor.execute(query, (id_user),)
                result = cursor.fetchone()
                if result is not None:
                    id_user, old_username, old_email = result
                    break
                else:
                    print("Usuario no encontrado")
                    time.sleep(1)

        except ValueError as e:
            print("El id ingresado no es valido")
            time.sleep(1)

    # Ingreso de los nuevos valores
    while True:
        clear_and_print(update_user.__doc__)
        username = input("Usuario: ")
        if len(username) == 0:
            username = old_username
        elif username != old_username and username_exist(username):
            print("El usuario ya existe")
            time.sleep(1)
        
        email = input("Email: ")
        if len(email) == 0:
            email = old_email
            break
        elif email != old_email and email_exist(email):
            print("El email ya existe")
            time.sleep(1)
        else:
            break

    with connection.cursor() as cursor:
        query = None
        if old_username != username and old_email != email:
            query = "UPDATE users SET username='{}', email='{}' WHERE id = {}".format(username, email, id_user)
        elif old_username != username:
            query = "UPDATE users SET username='{}' WHERE id = {}".format(username, id_user)
        elif old_email != email:
            query = "UPDATE users SET email='{}' WHERE id = {}".format(email, id_user)


        clear_and_print()
        if query is not None:
            cursor.execute(query)
            connection.commit()
            print("Usuario actualizado con exito!")
        else:
            print("No se realizaron cambios")
        
        time.sleep(1)
        return True

@back_menu
@with_connection
def delete_user(connection, *args, **kwargs):
    """Eliminar usuario
Usa (CTRL + C) para volver
    """
    # Busca a el usuario en la base de datos
    while True:
        try:
            clear_and_print(delete_user.__doc__)
            id_user = int(input("Ingresa el id del usuario: "))
            if get_user(id_user) is None:
                print("El usuario no existe")
                time.sleep(1)
            else:
                with connection.cursor() as cursor:
                    query = "DELETE FROM users WHERE id=%s"
                    cursor.execute(query, (id_user),)
                    connection.commit()
                    print("Usuario eliminado")
                    time.sleep(1)
                    break
        except ValueError as e:
            print("El id ingresado no es valido")
            time.sleep(1)


def menu():
    """
    A) Crear un nuevo usuario
    B) Listar usuarios
    C) Actualizar usuario
    D) Eliminar usuario
    Q) Salir
    """

    MENU_OPTIONS = {
        "a": add_user,
        "b": get_all_users,
        "c": update_user,
        "d": delete_user,
        "q": exit
    }

    while True:
        clear_and_print(menu.__doc__)
        user_input = input("Selecciona una opción: ")

        option_selected = MENU_OPTIONS.get(user_input.lower(), ">>> Opción no valida")
        clear_and_print()
        if callable(option_selected):
            option_selected()
        else:
            print(option_selected)
            time.sleep(1)

if __name__ == "__main__":
    create_table()
    menu()
