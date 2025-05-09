#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import connection
import optparse
import socket
import sys
import threading
from constants import *


class Server(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print("Serving %s on %s:%s." % (directory, addr, port))
        
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
            self.s.bind((addr, port))		                      
            self.dir = directory
            self.s.listen(5)
            
            # Se inicializa el semáforo para limitar la cantidad de hilos
            self.sem = threading.BoundedSemaphore(MAX_THR)
        except(socket.error):
            sys.stderr.write("Error al generar socket\n")

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        try:
            while True:
                try:
                    c, a = self.s.accept()		
                    print("Conexión aceptada de %s:%s." % a)
                    con = connection.Connection(c, self.dir)
                    self.sem.acquire()
                    
                    # Se crea un nuevo hilo para manejar la conexión
                    def run():
                        try:
                            con.handle()
                        finally:
                            self.sem.release()
                    
                    thread = threading.Thread(target=run)
                    thread.start()
                except(socket.error):
                    sys.stderr.write("Error al aceptar la conexión\n")
                    sys.exit(1)
        except KeyboardInterrupt:
                print("\nCtrl+C: Deteniendo servidor")
                sys.exit(0)

def main():
    """Parsea los argumentos y lanza el server"""

    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar", default=DEFAULT_PORT)
    parser.add_option(
        "-a", "--address",
        help="Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option(
        "-d", "--datadir",
        help="Directorio compartido", default=DEFAULT_DIR)

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            "Numero de puerto invalido: %s\n" % repr(options.port))
        parser.print_help()
        sys.exit(1)

    server = Server(options.address, port, options.datadir)
    server.serve()

if __name__ == '__main__':
    main()
