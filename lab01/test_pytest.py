import requests
import pytest
import requests_mock


@pytest.fixture
def mock_response():
    with requests_mock.Mocker() as m:
        # Simulamos la respuesta para obtener todas las películas
        m.get('http://localhost:5000/peliculas', json=[
            {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'},
            {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'}
        ])

        # Simulamos la respuesta para agregar una nueva película
        m.post('http://localhost:5000/peliculas', status_code=201,
               json={'id': 3, 'titulo': 'Pelicula de prueba',
                     'genero': 'Acción'})

        # Simulamos la respuesta para obtener
        # detalles de una película específica
        m.get('http://localhost:5000/peliculas/1',
              json={'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'})

        # Simulamos la respuesta para actualizar los detalles de una película
        m.put('http://localhost:5000/peliculas/1', status_code=200,
              json={'id': 1, 'titulo': 'Nuevo título', 'genero': 'Comedia'})

        # Simulamos la respuesta para eliminar una película
        m.delete('http://localhost:5000/peliculas/1', status_code=200)

        # Simulamos la respuesta para obtener todas las películas de un genero
        m.get('http://localhost:5000/peliculas/listado_genero/Fantasía', json=[
            {'id': 7, 'titulo': 'The Lord of the Rings', 'genero': 'Fantasía'}
        ])

        # Simulamos la respuesta para obtener
        # las peliculas cuyo titulo incluya un string
        m.get('http://localhost:5000/peliculas/listado_titulo/Star', json=[
            {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'}
        ])

        # Simulamos la respuesta para obtener pelicula aleatoria
        m.get('http://localhost:5000/peliculas/aleatorio', json=[
            {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'}
        ])

        # Simulamos la respuesta para obtener
        # pelicula aleatoria de un genero especifico
        m.get('http://localhost:5000/peliculas/aleatorio/Acción', json=[
            {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'}
        ])

        # Simulamos al respuesta para obtener una sugerencia de pelicula
        # aleatoria de un genero especifico para el proximo feriado
        m.get('http://localhost:5000/peliculas/feriado/Acción', json=[
            {
                "Película sugerida": {
                    "genero": "Acción",
                    "id": 2,
                    "titulo": "Star Wars"
                },
                "Próximo feriado": {
                    "dia": 29,
                    "id": "viernes-santo",
                    "info": "https://es.wikipedia.org/wiki/Viernes_Santo",
                    "mes": 3,
                    "motivo": "Viernes Santo Festividad Cristiana",
                    "tipo": "inamovible"
                }
            }])

        yield m


def test_obtener_peliculas(mock_response):
    response = requests.get('http://localhost:5000/peliculas')
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_agregar_pelicula(mock_response):
    nueva_pelicula = {'titulo': 'Pelicula de prueba', 'genero': 'Acción'}
    response = requests.post(
        'http://localhost:5000/peliculas', json=nueva_pelicula)
    assert response.status_code == 201
    assert response.json()['id'] == 3


def test_obtener_detalle_pelicula(mock_response):
    response = requests.get('http://localhost:5000/peliculas/1')
    assert response.status_code == 200
    assert response.json()['titulo'] == 'Indiana Jones'


def test_actualizar_detalle_pelicula(mock_response):
    datos_actualizados = {'titulo': 'Nuevo título', 'genero': 'Comedia'}
    response = requests.put(
        'http://localhost:5000/peliculas/1', json=datos_actualizados)
    assert response.status_code == 200
    assert response.json()['titulo'] == 'Nuevo título'


def test_eliminar_pelicula(mock_response):
    response = requests.delete('http://localhost:5000/peliculas/1')
    assert response.status_code == 200


def test_obtener_peliculas_genero(mock_response):
    response = requests.get(
        'http://localhost:5000/peliculas/listado_genero/Fantasía')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['titulo'] == 'The Lord of the Rings'


def test_obtener_peliculas_titulo(mock_response):
    response = requests.get(
        'http://localhost:5000/peliculas/listado_titulo/Star')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['titulo'] == 'Star Wars'


def test_obtener_pelicula_aleatoria(mock_response):
    response = requests.get('http://localhost:5000/peliculas/aleatorio')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['titulo'] == 'Indiana Jones'


def test_obtener_pelicula_aleatoria_genero(mock_response):
    response = requests.get('http://localhost:5000/peliculas/aleatorio/Acción')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['titulo'] == 'Indiana Jones'


def test_sugerir_pelicula_por_feriado(mock_response):
    response = requests.get(
        'http://localhost:5000/peliculas/feriado/Acción')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['Película sugerida']['titulo'] == 'Star Wars'
    assert response.json()[
        0]['Próximo feriado']['motivo'] == 'Viernes Santo Festividad Cristiana'
