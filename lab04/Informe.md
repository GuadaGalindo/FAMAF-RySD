<!-- omit in toc -->
# Análisis de enrutamiento en una red en anillo
<!-- omit in toc -->
## Redes y Sistemas Distribuidos 2024
<!-- omit in toc -->
### Grupo 14. Integrantes: Javier Adragna, Guadalupe Galindo, Tomás Romanutti
<!-- omit in toc -->
### Profesores: Delfina Velez, Gonzalo Vodanovic
<!-- omit in toc -->
## Contenido

- [Resumen / Abstract](#resumen--abstract)
- [Introducción](#introducción)
- [Métodos](#métodos)
- [Resultados](#resultados)
  - [Modelo con protocolo de enrutamiento simple - Test caso 1](#modelo-con-protocolo-de-enrutamiento-simple---test-caso-1)
  - [Modelo con protocolo de enrutamiento simple - Test caso 2](#modelo-con-protocolo-de-enrutamiento-simple---test-caso-2)
  - [Modelo con protocolo de enrutamiento inundación - Test caso 1](#modelo-con-protocolo-de-enrutamiento-inundación---test-caso-1)
  - [Modelo con protocolo de enrutamiento inundación - Test caso 2](#modelo-con-protocolo-de-enrutamiento-inundación---test-caso-2)
- [Conclusiones](#conclusiones)
- [Video](#video)
- [Bibliografía](#bibliografía)

-----------------------------------------------------------------------------------

## Resumen / Abstract

Implementamos un algoritmo de enrutamiento en un modelo de red en anillo simulado con OMNet++

Nuestra tarea fue diseñar este algoritmo, con el fin de analizar en distintos casos el rendimiento del sistema de enrutamiento planteado.

## Introducción

En una red, cada nodo puede contener múltiples interfaces sobre las cuales mandar información a distintos vecinos. La encargada de elegir por cuál interfaz mandar la información para lograr una comunicación óptima entre los nodos es la capa de red, a través de un proceso llamado enrutamiento.

En particular, en un modelo de anillo, cada nodo tiene específicamente dos interfaces que envían información a uno de sus dos vecinos. Los nodos están conectados de tal manera que el grafo asociado a la red acaba teniendo una forma circular. Por este motivo, clasificamos estas conexiones en dos grupos: las que envían información “_en sentido horario_” y las que envían “_en sentido antihorario_”.

Estas aristas son **full-duplex**, lo que significa que los paquetes pueden tomar cualquier dirección e incluso dar la vuelta y regresar por donde se enviaron.

![Modelo de red de anillo](/media/Modelo_Anillo.png)

_Figura 1. Diagrama del modelo de red de anillo. Fuente: elaboración propia._

Para testear los algoritmos de enrutamiento, probaremos dos situaciones en un modelo de anillo con ocho nodos: en la primera situación, dos nodos (`node[0]` y `node[2]` de la Figura 1) quieren enviar ambos información a un mismo nodo (`node[5]`, en nuestro caso particular). En la segunda situación todos los nodos se vuelven emisores, excepto un único receptor que es el objetivo del resto del anillo (nuestro ejemplo usa nuevamente a `node[5]` como el objetivo).

Se nos proveyó de un algoritmo simple de enrutamiento el cual mandaba todos los paquetes de datos en sentido horario, hasta llegar al nodo de destino. Si bien es una estrategia sencilla y funciona a la hora de siempre llegar a destino (ya que nunca va a parar), es ineficiente en algunos casos. Usando nuestra primera situación de ejemplo, `node[2]`, que es uno de los nodos emisores, enviaría su paquete a `node[1]`, que se encuentra en sentido horario. Eso causa que el paquete necesite 5 saltos entre nodos para llegar al receptor. Sin embargo, si se hubiera mandado por el sentido antihorario (por `node[3]`), tan solo hubiera necesitado 3 saltos para llegar.

## Métodos

Para la construcción de nuestro sistema de enrutamiento nos basamos en el “algoritmo de inundación” visto en el teórico, incorporando optimizaciones como registro de paquetes difundidos y contador de saltos.

Durante la inicialización de nuestra red, cada nodo envía un paquete `Hello` para descubrir el tamaño del anillo y configurar su contador de saltos. El campo Depth de cada paquete `Hello` se incrementa a medida que pasa por cada nodo, hasta que regresa al nodo emisor original. Es en este punto donde el nodo recibe la información sobre el tamaño del anillo.

Para la implementación del “_registro de paquetes difundidos_”, decidimos agregar a cada nodo una variable denominada `seqNumber`, que se incrementa cada vez que se envía un paquete. Esta variable se utiliza para establecer el campo `sequenceNumber` de cada paquete, el cual también fue añadido por nosotros. Además, para que cada nodo pueda llevar un registro de los paquetes vistos de cada emisor, incluimos en cada uno de ellos un diccionario llamado `routingTable`. Este diccionario mapea cada nodo con una estructura `s_table` que contienen un **contador** y una **lista de los números de secuencia vistos** de ese nodo.

Por otro lado, la optimización de “_contador de saltos_” la logramos sumando a cada paquete el campo `hopCount`, el cual seteamos en la mitad del tamaño del anillo. Esta decisión la tomamos teniendo en cuenta la elección de nuestro algoritmo y que alguno de los paquetes enviados por el emisor llegará máximo en esa cantidad de saltos. Este campo se actualiza en cada visita del paquete a un nuevo nodo, lo que garantiza que no puedan generarse _loops de enrutamiento_.

Con toda esta información, cada vez que un nodo emite un paquete, lo hace a través de ambas de sus interfaces, lo que resulta en un duplicado de cada paquete. Posteriormente, cuando un nodo recibe alguno de estos paquetes, lo reenvía a través de la interfaz por la cual no lo recibió inicialmente. Este proceso se repite hasta que el paquete llega a su destino o se agota su contador de saltos (`hopCount`). Si el anillo tiene tamaño par, ambos paquetes llegarían a destino antes de que finalice su contador de saltos. En este caso, el nodo destino detecta el paquete duplicado gracias a su `routingTable` y lo elimina.

## Resultados

Para poder analizar la mejora que surgió tras implementar nuestro algoritmo, necesitamos tomar ciertas métricas que nos ayudan a decidir la efectividad del cambio.

Tomamos las siguientes métricas:

- Usos de cada enlace, por nodo.
- Tamaño máximo del buffer de cada enlace, por nodo
- Paquetes entregados.
- Delay en cada entrega.
- Cantidad de saltos por paquete entregado.

A continuación mostraremos los resultados de las mediciones, separando por ambas situaciones previamente descritas:

### Modelo con protocolo de enrutamiento simple - Test caso 1

| Nodo  | Usos del Lnk 0 | Tamaño máximo del buffer de Lnk 0 | Usos del Lnk 1 | Tamaño máximo del buffer de Lnk 1 |
|-------|----------------|-----------------------------------|----------------|-----------------------------------|
| 0     | 387            | 586                               | 0              | 0                                 |
| 1     | 187            | 374                               | 0              | 0                                 |
| 2     | 189            | 377                               | 0              | 0                                 |
| 3     | -              | -                                 | 0              | 0                                 |
| 4     | -              | -                                 | 0              | 0                                 |
| 5     | -              | -                                 | 0              | 0                                 |
| 6     | 197            | 394                               | 0              | 0                                 |
| 7     | 198            | 396                               | 0              | 0                                 |
| Media | 231,60         | 425,40                            | 0              | 0                                 |

- Número de paquetes entregados = 196
- Delay promedio = 51,15
- Saltos promedio = 3,91

### Modelo con protocolo de enrutamiento simple - Test caso 2

| Nodo  | Usos del Lnk 0 | Tamaño máximo del buffer de Lnk 0 | Usos del Lnk 1 | Tamaño máximo del buffer de Lnk 1 |
|-------|----------------|-----------------------------------|----------------|-----------------------------------|
| 0     | 402            | 602                               | 0              | 0                                 |
| 1     | 394            | 593                               | 0              | 0                                 |
| 2     | 423            | 622                               | 0              | 0                                 |
| 3     | 371            | 570                               | 0              | 0                                 |
| 4     | 195            | 380                               | 0              | 0                                 |
| 5     | -              | -                                 | 0              | 0                                 |
| 6     | 364            | 564                               | 0              | 0                                 |
| 7     | 405            | 605                               | 0              | 0                                 |
| Media | 364,85         | 562,28                            | 0              | 0                                 |

- Número de paquetes entregados = 199
- Delay promedio = 64,53
- Saltos promedio = 2,06

![Métricas de red con protocolo de enrutamiento simple](/media/Metricas%20simple.png)

_Métricas de red con protocolo de enrutamiento simple . Fuente: elaboración propia._

-----------------------------------------------------------------------------------

Después de analizar el comportamiento de la red con el protocolo de enrutamiento simple, procedimos a realizar los mismos experimentos usando simulaciones en OMNeT++ para evaluar el rendimiento del algoritmo de enrutamiento por inundación  implementado. Para ello utilizamos  los mismos dos  casos e estudio.
Además de las estadísticas que tomamos con anterioridad, sumamos dos mediciones extra necesarias para analizar nuestro algoritmo:

- Número de paquetes duplicados.
- Número de paquetes muertos (por su cantidad de saltos).

### Modelo con protocolo de enrutamiento inundación - Test caso 1

| Nodo  | Usos del Lnk 0 | Tamaño máximo del buffer de Lnk 0 | Usos del Lnk 1 | Tamaño máximo del buffer de Lnk 1 | Paquetes duplicados | Paquetes muertos |
|-------|----------------|-----------------------------------|----------------|-----------------------------------|---------------------|------------------|
| 0     | 387            | 602                               | 201            | 397                               | 0                   | 0                |
| 1     | 187            | 195                               | 395            | 390                               | 0                   | 0                |
| 2     | 189            | 393                               | 383            | 582                               | 0                   | 0                |
| 3     | -              | 16                                | 198            | 396                               | 0                   | 0                |
| 4     | -              | 16                                | 100            | 200                               | 0                   | 0                |
| 5     | -              | 16                                | -              | -                                 | 0                   | -                |
| 6     | 107            | 230                               | -              | -                                 | 0                   | 0                |
| 7     | 198            | 609                               | -              | -                                 | 0                   | 0                |
| Media | 213,60         | 259,62                            | 255,40         | 393                               | -                   | 0                |

- Número de paquetes entregados = 205
- Delay promedio = 48,78
- Saltos promedio = 3

### Modelo con protocolo de enrutamiento inundación - Test caso 2

| Nodo  | Usos del Lnk 0 | Tamaño máximo del buffer de Lnk 0 | Usos del Lnk 1 | Tamaño máximo del buffer de Lnk 1 | Paquetes duplicados | Paquetes muertos |
|-------|----------------|-----------------------------------|----------------|-----------------------------------|---------------------|------------------|
| 0     | 381            | 597                               | 403            | 603                               | 0                   | 22               |
| 1     | 394            | 609                               | 395            | 594                               | 0                   | 0                |
| 2     | 423            | 638                               | 402            | 601                               | 0                   | 22               |
| 3     | 371            | 586                               | 371            | 570                               | 0                   | 15               |
| 4     | 195            | 396                               | 379            | 579                               | 0                   | 15               |
| 5     | -              | 16                                | -              | -                                 | 14                  | -                |
| 6     | 349            | 565                               | 165            | 329                               | 0                   | 16               |
| 7     | 393            | 609                               | 369            | 569                               | 0                   | 13               |
| Media | 364,42         | 502                               | 354,85         | 549,28                            | -                   | 14,71            |

- Número de paquetes entregados = 379
- Delay promedio = 62,64
- Saltos promedio = 1,72

![Métricas de red con protocolo de enrutamiento inundación](/media/Metricas%20inundacion.png)

_Métricas de red con protocolo de enrutamiento inundación. Fuente: elaboración propia._

## Conclusiones

Al analizar los datos obtenidos de las simulaciones, podemos observar varias mejoras en el rendimiento de la red al implementar el protocolo de enrutamiento por inundación comparado con el protocolo simple.

Porcentajes de mejora promedio en el rendimiento de la red al aplicar protocolo:

> Caso 1

| Promiedos                  | Reducción |
|----------------------------|-----------|
| Delay                      |  4,63%    |
| Saltos                     |  0,91%    |
| Usos del Lnk 0             |  7,77%    |
| Tamaño del buffer de Lnk 0 |  38,97%   |

> Caso 2

| Promiedos                  | Reducción |
|----------------------------|-----------|
| Delay                      |  2,92%    |
| Saltos                     |  16,50%   |
| Usos del Lnk 0             |  0,11%    |
| Tamaño del buffer de Lnk 0 |  10,72%   |

![Mejora delay Caso 1](/media/Delay%20caso%201.png)

_Delay en caso de análisis 1 para ambos enrutamientos. Fuente: elaboración propia._

![Mejora delay Caso 2](/media/Delay%20caso%201.png)

_Delay en caso de análisis 2 para ambos enrutamientos. Fuente: elaboración propia._

![Cantidad de saltos promedio por paquete entregado](/media/Saltos%20promedio.png)

_Cantidad de saltos promedio por paquete entregado. Fuente: elaboración propia._

![Tamaño máximo del buffer de Lnk 0](/media/Buffer%20Lnk%200.png)

_Tamaño máximo del buffer de Lnk 0. Fuente: elaboración propia._

De esas métricas resulta evidente que hubo una reducción considerable en el tamaño del buffer de los enlaces de sentido horario del primer caso y en la cantidad de saltos de ambas situaciones. Esto muestra que se produjo una mejora en la gestión del tráfico de la red, y que los paquetes siguieron rutas más cortas y eficientes (lo que generó menores tiempos de delay, mejorando la rapidez de entrega de los paquetes). En contrapartida, en ambos casos se requirió comenzar a utilizar Lnk 1, y por tanto también su respectivo buffer. Además el nodo receptor necesitó usar uno de sus buffers debido al proceso de inicialización.

Los resultados muestran que el protocolo de inundación mejora la eficiencia de la red en términos de delay y número de saltos, aunque introduce la complejidad adicional de gestionar los paquetes duplicados y muertos. Este protocolo también equilibra mejor la carga entre Lnk 0 y Lnk 1, optimizando el uso del buffer de los enlaces. El hecho de que el número de paquetes duplicados fue (prácticamente) cero en ambos casos, demuestra la eficacia de la tabla de enrutamiento para evitar redundancias.

Para mejorar aún más el rendimiento, podría implementarse un protocolo que calcule la mejor ruta en lugar de enviar paquetes en ambas direcciones. Esto reduciría la carga en la red y disminuiría el número de paquetes muertos. Además, la generalización del protocolo para adaptarse a topologías de red más complejas, utilizando algoritmos como el de Dijkstra, podría proporcionar rutas óptimas y mayor eficiencia.

## Video

Se puede encontrar nuestro video explicando estos conceptos y demostrando cómo funciona el algoritmo en [este enlace](https://drive.google.com/file/d/1RLzVIEPDh_03RGMkoxd3b-9guSAs80HS/view?usp=sharing)

## Bibliografía

- [Documentación de OMNeT++](https://doc.omnetpp.org/omnetpp/api/) version 6.0.3
- Contenido audiovisual [(videos y filminas)](https://famaf.aulavirtual.unc.edu.ar/course/view.php?id=300) provisto por la cátedra
- Tanembaum. Computer Networks: quinta edición - 2011.
