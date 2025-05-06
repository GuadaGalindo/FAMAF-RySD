# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
import os
from constants import *
from base64 import b64encode


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        """
        Inicializa al socket conectado
        """
        self.socket = socket
        self.directory = directory
        self.buffer = ''
        self.connected = True
        
    def send_msg(self, status):
        """
        Envia mensajes al cliente según el status
        """
        # Verifica que el socket esté activo y setea su nuevo status
        if self.socket:
            self.status = status
            if valid_status(status):
                # Si es un error válido, se envía el mensaje correspondiente
                message = str(status) + ' ' + error_messages[status]
                self.socket.send((message + EOL).encode("ascii"))
            if fatal_status(status):
                # Si es un error fatal, se reporta y se cierra la conexión
                message = str(status) + ' ' + error_messages[status]
                self.socket.send((message + EOL).encode("ascii"))
                self.socket.close()
                self.socket = None
                self.connected = False

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        # Si el socket no está conectado, se envía un error interno
        if (self.socket is None) or (not self.connected):
            self.send_msg(INTERNAL_ERROR)
        
        # Ciclo principal de la conexión con el cliente        
        while self.connected:
            
            # Se lee el buffer hasta encontrar un fin de línea
            self.buffer = ''
            while EOL not in self.buffer:
                data = self.socket.recv(4096).decode("ascii")
                self.buffer += data
            
            # Se separa el buffer en comandos y luego en argumentos
            commands = self.buffer.split(EOL)
            for command in commands: 
                command = command.strip()
                if command:
                    # Se verifica que el comando no contenga saltos de línea
                    if '\n' in command:
                        self.send_msg(BAD_EOL)
                    
                    # Se verifica que el comando no exceda el límite de bytes
                    spl = command.split()
                    if len(spl) > 4095:
                        self.send_msg(BAD_REQUEST)

                    # Se procesan los comandos
                    if spl[0] == "get_file_listing":
                        if len(spl[1:]) == 0:
                            self.get_file_listing()
                        else: self.send_msg(INVALID_ARGUMENTS)
                    elif spl[0] == "get_metadata":
                        if len(spl[1:]) == 1:
                            self.get_metadata(spl[1])
                        else: self.send_msg(INVALID_ARGUMENTS)
                    elif spl[0] == "get_slice":
                        if (
                            len(spl[1:]) == 3 and 
                            spl[2].isdigit() and spl[3].isdigit()):
                            self.get_slice(spl[1], int(spl[2]), int(spl[3]))
                        else: self.send_msg(INVALID_ARGUMENTS)
                    elif spl[0] == "quit":
                        if len(spl[1:]) == 0:
                            self.quit()
                        else: self.send_msg(INVALID_ARGUMENTS)
                    else:
                        self.send_msg(INVALID_COMMAND)
        if self.socket:
            # Si la conexión terminó y el socket sigue activo, se lo cierra
            self.socket.close()
            self.socket = None              

    def get_file_listing(self):
        """
        Devuelve la lista de archivos actualmente disponibles.
        """
        print("Request: get_file_listing")
        file_list = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
        
        # Verifica que el directorio exista y sea válido
        if not (os.path.exists(self.directory) and 
                os.path.isdir(self.directory)):
            self.send_msg(INTERNAL_ERROR)
        
        for dir in os.listdir(self.directory):
            file_list += f"{dir} {EOL}"
        self.status = CODE_OK
        self.socket.send((file_list).encode("ascii"))
        self.socket.send(EOL.encode('ascii'))

    def file_exist(self, filename):
        """
        Auxiliar: verifica si el filename existe en el directorio
        """
        file_path = os.path.join(self.directory, filename)
        return (os.path.isfile(file_path))

    def file_is_valid(self, filename):
        """
        Auxiliar: verifica si el filename tiene solo caracteres válidos
        """
        for char in filename:
            if char not in VALID_CHARS:
                return False
        return True

    def get_metadata(self, filename):
        """
        Devuelve el tamaño en bytes del filename.
        """
        print("Request: get_metadata %s" % filename)
        
        # Verifica que el filename sea válido y exista
        if not self.file_exist(filename):
            self.send_msg(FILE_NOT_FOUND)
        elif not self.file_is_valid(filename):
            self.send_msg(INVALID_ARGUMENTS)
        else:
            response = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
            response += str(self.get_size(filename)) + EOL
            self.status = CODE_OK
            self.socket.send((response).encode("ascii"))

    def get_size(self, filename):
        """
        Modularizado, devuelve el tamaño en bytes del filename
        """
        return os.path.getsize(os.path.join(self.directory, filename))

    def get_slice(self, filename, offset, size):
        """
        Devuelve una porción de tamaño size, desde un offset, del filename
        """
        print("Request: get_slice %s %s %s" % (filename, offset, size))
        
        # Verifica que el size y offset sean válidos y que exista el filename
        if int(offset) < 0 or int(size) < 0:
            self.send_msg(INVALID_ARGUMENTS)
        elif int(offset) + int(size) > self.get_size(filename):
            self.send_msg(BAD_OFFSET)
        elif not self.file_exist(filename):
            self.send_msg(FILE_NOT_FOUND)
        elif not self.file_is_valid(filename):
            self.send_msg(INVALID_ARGUMENTS)
        else:
            filepath = os.path.join(self.directory, filename)
            f = open(filepath, "rb")
            f.seek(offset)
            read = b64encode(f.read(size))
            f.close()
            self.send_msg(CODE_OK)
            self.status = CODE_OK
            self.socket.send(read)
            self.socket.send(EOL.encode('ascii'))

    def quit(self):
        """
        Termina la conexión con el cliente
        """
        print("Request: quit")
        self.send_msg(CODE_OK)
        self.socket.close()
        self.socket = None
        self.connected = False
