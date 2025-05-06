from flask import Flask, jsonify, request
from proximo_feriado import NextHoliday
import random

app = Flask(__name__)
peliculas = [
    {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'},
    {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'},
    {'id': 3, 'titulo': 'Interstellar', 'genero': 'Ciencia ficción'},
    {'id': 4, 'titulo': 'Jurassic Park', 'genero': 'Aventura'},
    {'id': 5, 'titulo': 'The Avengers', 'genero': 'Acción'},
    {'id': 6, 'titulo': 'Back to the Future', 'genero': 'Ciencia ficción'},
    {'id': 7, 'titulo': 'The Lord of the Rings', 'genero': 'Fantasía'},
    {'id': 8, 'titulo': 'The Dark Knight', 'genero': 'Acción'},
    {'id': 9, 'titulo': 'Inception', 'genero': 'Ciencia ficción'},
    {'id': 10, 'titulo': 'The Shawshank Redemption', 'genero': 'Drama'},
    {'id': 11, 'titulo': 'Pulp Fiction', 'genero': 'Crimen'},
    {'id': 12, 'titulo': 'Fight Club', 'genero': 'Drama'}
]


def obtener_peliculas():
    # Devuelve la lista de películas en formato JSON
    return jsonify(peliculas)


def obtener_pelicula(id):
    # Lógica para buscar la película por su ID y devolver sus detalles
    for pelicula in peliculas:
        if pelicula['id'] == id:
            pelicula_encontrada = pelicula
            return jsonify(pelicula_encontrada), 200
    return jsonify({'mensaje': 'Error, película no encontrada'}), 400


def agregar_pelicula():
    # Agrega una pelicula nueva al diccionario de peliculas
    nueva_pelicula = {
        'id': obtener_nuevo_id(),
        'titulo': request.json['titulo'],
        'genero': request.json['genero']
    }
    peliculas.append(nueva_pelicula)
    print(peliculas)
    return jsonify(nueva_pelicula), 201


def actualizar_pelicula(id):
    # Lógica para buscar la película por su ID y actualizar sus detalles
    for pelicula in peliculas:
        if pelicula['id'] == id:
            nuevo_titulo = request.json['titulo']
            nuevo_genero = request.json['genero']
            pelicula['titulo'] = nuevo_titulo
            pelicula['genero'] = nuevo_genero
            return jsonify(pelicula), 200
    return jsonify({'mensaje': 'Error, pelicula no encontrada'}), 400


def eliminar_pelicula(id):
    # Lógica para buscar la película por su ID y eliminarla
    for pelicula in peliculas:
        if pelicula['id'] == id:
            peliculas.remove(pelicula)
            return jsonify({
                'mensaje': 'Película eliminada correctamente'}), 200
    return jsonify({'mensaje': 'Error, película no encontrada'}), 400


def obtener_nuevo_id():
    # Modularizacion: Obtiene el ID de la nueva película a agregar
    if len(peliculas) > 0:
        ultimo_id = peliculas[-1]['id']
        return ultimo_id + 1
    else:
        return 1


def listado_genero(genero):
    # Modularizacion: Genera una lista de las películas de un genero específico
    peliculas_genero = []
    for pelicula in peliculas:
        if pelicula['genero'] == genero:
            peliculas_genero.append(pelicula)
    return peliculas_genero


def listado_genero_jsonify(genero):
    # Devuelve en formato JSON a la lista de películas de un genero específico
    return jsonify(listado_genero(genero)), 200


def listado_titulo(palabra):
    # Devuelve una lista de las peliculas que tienen palabra en el titulo
    peliculas_titulo = []
    for pelicula in peliculas:
        if palabra in pelicula['titulo']:
            peliculas_titulo.append(pelicula)
    return jsonify(peliculas_titulo), 200


def sugerir_aleatorio():
    # Sugiere una película aleatoria
    if peliculas != []:
        pelicula_sugerida = random.choice(peliculas)
        return jsonify(pelicula_sugerida), 200
    return jsonify({
        'mensaje': 'Error, la biblioteca de películas está vacía.'}), 400


def sugerir_genero(genero):
    # Sugiere una película aleatoria segun genero
    peliculas_genero = listado_genero(genero)
    if peliculas_genero != []:
        pelicula_sugerida = random.choice(peliculas_genero)
        return jsonify(pelicula_sugerida), 200
    return jsonify({
        'mensaje': 'Error, no existen películas con ese género.'}), 400


def sugerir_por_feriado(genero):
    # Indica el siguiente feriado y sugiere una película aleatoria del genero
    next_holiday = NextHoliday()
    next_holiday.fetch_holidays()

    peliculas_genero = listado_genero(genero)
    if peliculas_genero != []:
        pelicula_sugerida = random.choice(peliculas_genero)
        return jsonify({
            'Próximo feriado': next_holiday.holiday,
            'Película sugerida': pelicula_sugerida}), 200
    return jsonify({
        'mensaje': 'Error, no existen películas con ese género.'}), 400


app.add_url_rule('/peliculas', 'obtener_peliculas',
                 obtener_peliculas, methods=['GET'])
app.add_url_rule('/peliculas/<int:id>', 'obtener_pelicula',
                 obtener_pelicula, methods=['GET'])
app.add_url_rule('/peliculas', 'agregar_pelicula',
                 agregar_pelicula, methods=['POST'])
app.add_url_rule('/peliculas/<int:id>', 'actualizar_pelicula',
                 actualizar_pelicula, methods=['PUT'])
app.add_url_rule('/peliculas/<int:id>', 'eliminar_pelicula',
                 eliminar_pelicula, methods=['DELETE'])
app.add_url_rule('/peliculas/aleatorio', 'sugerir_aleatorio',
                 sugerir_aleatorio, methods=['GET'])
app.add_url_rule('/peliculas/aleatorio/<string:genero>',
                 'sugerir_genero', sugerir_genero, methods=['GET'])
app.add_url_rule('/peliculas/listado_titulo/<string:palabra>',
                 'listado_titulo', listado_titulo, methods=['GET'])
app.add_url_rule('/peliculas/listado_genero/<string:genero>',
                 'listado_genero', listado_genero_jsonify, methods=['GET'])
app.add_url_rule('/peliculas/feriado/<string:genero>',
                 'sugerir_por_feriado', sugerir_por_feriado, methods=['GET'])


if __name__ == '__main__':
    app.run()
