import requests

# Obtener todas las películas
response = requests.get('http://localhost:5000/peliculas')
peliculas = response.json()
print("Películas existentes:")
for pelicula in peliculas:
    print(
        f"ID: {pelicula['id']}, Título: {pelicula['titulo']}, 
        Género: {pelicula['genero']}")
print()

# Agregar una nueva película
nueva_pelicula = {
    'titulo': 'Pelicula de prueba',
    'genero': 'Acción'
}
response = requests.post(
    'http://localhost:5000/peliculas', json=nueva_pelicula)
if response.status_code == 201:
    pelicula_agregada = response.json()
    print("Película agregada:")
    print(
        f"ID: {pelicula_agregada['id']}, 
        Título: {pelicula_agregada['titulo']}, 
        Género: {pelicula_agregada['genero']}")
else:
    print("Error al agregar la película.")
print()

# Obtener detalles de una película específica
id_pelicula = 1  # ID de la película a obtener
response = requests.get(f'http://localhost:5000/peliculas/{id_pelicula}')
if response.status_code == 200:
    pelicula = response.json()
    print("Detalles de la película:")
    print(
        f"ID: {pelicula['id']}, Título: {pelicula['titulo']}, 
        Género: {pelicula['genero']}")
else:
    print("Error al obtener los detalles de la película.")
print()

# Actualizar los detalles de una película
id_pelicula = 1  # ID de la película a actualizar
datos_actualizados = {
    'titulo': 'Nuevo título',
    'genero': 'Comedia'
}
response = requests.put(
    f'http://localhost:5000/peliculas/{id_pelicula}', json=datos_actualizados)
if response.status_code == 200:
    pelicula_actualizada = response.json()
    print("Película actualizada:")
    print(
        f"ID: {pelicula_actualizada['id']}, 
        Título: {pelicula_actualizada['titulo']}, 
        Género: {pelicula_actualizada['genero']}")
else:
    print("Error al actualizar la película.")
print()

# Eliminar una película
id_pelicula = 1  # ID de la película a eliminar
response = requests.delete(f'http://localhost:5000/peliculas/{id_pelicula}')
if response.status_code == 200:
    print("Película eliminada correctamente.")
else:
    print("Error al eliminar la película.")

# Obtener todas las películas de un genero
genero = "Fantasía"
response = requests.get(
    f'http://localhost:5000/peliculas/listado_genero/{genero}')
if response.status_code == 200:
    print(f"Listado de peliculas de un genero " +
          "especifico obtenido correctamente")
else:
    print("Error al obtener las peliculas de un genero especifico")

# Obtener las peliculas cuyo titulo incluya un string
string = "Star"
response = requests.get(
    f'http://localhost:5000/peliculas/listado_titulo/{string}')
if response.status_code == 200:
    print(f"Listado de peliculas cuyo titulo incluya un " + 
          "string especifico obtenido correctamente")
else:
    print("Error al obtener las peliculas cuyo titulo incluya un string")

# Obtener pelicula aleatoria
response = requests.get('http://localhost:5000/peliculas/aleatorio')
if response.status_code == 200:
    print("Película aleatoria obtenida correctamente")
else:
    print("Error al obtener una película aleatoria")

# Obtener pelicula aleatoria de un genero especifico
genero = "Fantasía"
response = requests.get(
    f'http://localhost:5000/peliculas/aleatorio/{genero}')
if response.status_code == 200:
    print(f"Película aleatoria de un genero especifico obtenida correctamente")
else:
    print("Error al obtener una película aleatoria de un genero especifico")

# Obtener sugerencia de pelicula aleatoria 
# de un genero especifico para el proximo feriado
genero = "Fantasía"
response = requests.get(
    f'http://localhost:5000/peliculas/feriado/{genero}')
if response.status_code == 200:
    print(f"Película aleatoria de un genero especifico " +
          "para el proximo feriado obtenida correctamente")
else:
    print("Error al obtener una película aleatoria de un genero " +
          "especifico para el proximo feriado")
