# Redes y Sistemas Distribuidos 2024

## Informe - Laboratorio 02: Aplicación Servidor

### Grupo: 14

### Integrantes

* Guadalupe Galindo
* Javier Adragna
* Tomás Romanutti

### [Video presentación del proyecto](https://drive.google.com/file/d/184wqzE3pfkS6DOY93Anevx5BQOUJb_xf/view)

---

## Protocolo HFTP

El proyecto consiste en la creación de un protocolo de transferencia de archivos casero, el Home-made File Transfer Protocol (HFTP), que utiliza TCP como protocolo de transporte. El mismo es un protocolo ASCII de capa de aplicación y garantiza una entrega segura, libre de errores y en orden de todas las transacciones. Los servidores que usan HFTP escuchan pedidos en el puerto TCP 19500.

### Preguntas

1. ¿Qué estrategias existen para poder implementar este mismo servidor pero con capacidad de atender múltiples clientes simultáneamente? Investigue y responda brevemente qué cambios serían necesarios en el diseño del código.

   Para implementar este mismo servidor con la capacidad de atender múltiples clientes simultáneamente, pueden seguirse varias estrategias:

   La primera, implementada en el laboratorio, es utilizar **hilos** (_threads_), uno por cada nueva conexión aceptada por el servidor. Cada hilo se ejecuta en paralelo para administrar un cliente, permitiendo al servidor manejar múltiples conexiones a la vez. Para aplicar esta estrategia, debería modificarse el bucle principal del servidor para que cada vez que una conexión sea aceptada se delegue la misma a un nuevo hilo. Además, debe establecerse un mecanismo de sincronización (en nuestro caso, un semáforo) para evitar problemas de concurrencia y sincronización que puedan darse mientras los distintos hilos trabajen en simultáneo sobre los mismos recursos.

   Otra opción es implementar múltiples clientes con **poll**, lo que permite monitorear varios sockets simultáneamente. A diferencia de la estrategia anterior, se requeriría adaptar más funciones además del bucle principal del servidor, aunque no sería necesario establecer un mecanismo de sincronización adicional.
   Similar a poll, la administración de múltiples sockets simultáneos se puede lograr con la función **select**. Sin embargo, select tiene una limitación en la cantidad máxima de descriptores de archivo que puede manejar y es menos eficiente que poll.

   Una tercera posibilidad es utilizar un paradigma basado en **eventos** para programar el servidor, lo que le permitiría manejar múltiples clientes de manera asíncrona. Aunque esto requeriría una reescritura completa del programa, seguir este modelo podría ofrecer grandes beneficios en términos de escalabilidad del proyecto.

2. Pruebe ejecutar el servidor en una máquina del laboratorio, mientras utiliza el cliente desde otra, hacia la IP de la máquina servidor. ¿Qué diferencia hay si se corre el servidor desde la IP “localhost”, “127.0.0.1” o la IP “0.0.0.0”?

   Tanto `localhost` como `127.0.0.1` representan la dirección IP local y no hay diferencia en correr el servidor desde cualquiera de ellas, ya que ambas crean una conexión con la misma computadora. Por otro lado, correr el servidor en `0.0.0.0` no lo conecta con ninguna dirección en particular, sino que lo hace disponible para escuchar conexiones desde cualquier dirección IP, tanto local como externa.


### Archivos modificados

* [server.py](server.py): Creación del socket y loop principal del servidor utilizando semáforos para gestionar múltiples clientes.
* [connection.py](connection.py): Implementación del handle de la conexión y distintos comandos que el servidor es capaz de aceptar.
* [client.py](client.py): Corrección de bug en la creación del cliente.
