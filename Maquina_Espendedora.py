class MaquinaExpendedora:
    def __init__(self):

        self.productos = {
            "N": {"nombre": "Naranja", "stock": 10, "precio": 30.00},
            "L": {"nombre": "Limon", "stock": 10, "precio": 30.00},
            "M": {"nombre": "Manzana", "stock": 10, "precio": 30.00}
        }
        
        # Precio fijo para todos los productos
        self.precio = 30.00
        
        # Saldos y reservas totales
        # NOTA: Con estas variables se guardan las reservas y ventas totales en la máquina. Éstas
        #       son las que se usan para el cálculo del vuelto.
        self.saldo = 0
        self.saldo_reservado_5 = 8
        self.saldo_reservado_10 = 5
        self.saldo_reservado_25 = 3
        self.saldo_reservado = 25*self.saldo_reservado_25 + 10*self.saldo_reservado_10 + 5*self.saldo_reservado_5

        # Cantidad total de billetes ingresados por el cliente (Para la interfaz)
        # NOTA: Estas cantidades registran todos los billetes ingresados desde que el programa se
        #       ejecuta, sin contar las reservas internas. Se usarán solo con fines de control.
        self.cantidad_B5 = 0
        self.cantidad_B10 = 0
        self.cantidad_B25 = 0

        # Cantidad total de billetes ingresados por el cliente para una operacion determinada.
        # NOTA: Estas variables permiten hacer un seguimiento de los billetes ingresados por el
        #       cliente en una transaccion determinada y el saldo que acumule en la misma. 
        #       Facilitarán el reinicio de la transacción sin afectar los montos acumulados 
        #       previamente en la máquina. Se reinician a 0 cada vez que se termina una operación.
        self.cantidad_B5_operacion_actual = 0
        self.cantidad_B10_operacion_actual = 0
        self.cantidad_B25_operacion_actual = 0
        self.saldo_actual = 0
        self.falta = 30.00
        
        # ====================================================================
        # ESTADOS MEF
        # ====================================================================

        self.estados = [
            "ESPERANDO_BILLETE",        # 0 - Espera que el usuario inserte billete
            "VALIDANDO_BILLETE",        # 1 - Está verificando si el billete es válido
            "ESPERANDO_MAS_DINERO",     # 2 - Billete válido, pero saldo insuficiente
            "LISTO_SELECCION",          # 3 - Tiene saldo suficiente para seleccionar producto
            "VALIDANDO_SELECCION",      # 4 - Está verificando la selección del producto
            "ESPERANDO_CONFIRMACION",   # 5 - Producto seleccionado, espera confirmación
            "PROCESANDO_PAGO",          # 6 - Está procesando el pago
            "DESPACHANDO_PRODUCTO",     # 7 - Está entregando el producto
            "DEVOLVIENDO_CAMBIO",       # 8 - Está devolviendo el cambio
            "ERROR",                    # 9 - Ocurrió un error
            "CANCELADO"                 # 10 - El usuario canceló
        ]
        
        # ====================================================================
        # EVENTOS MEF
        # ====================================================================
        self.eventos = [
            "BILLETE_INSERTADO",        # 0 - El usuario insertó un billete
            "BILLETE_VALIDO",           # 1 - El billete es válido (5, 10, 25)
            "BILLETE_INVALIDO",         # 2 - El billete NO es válido
            "SALDO_SUFICIENTE",         # 3 - Tiene al menos $30 de saldo
            "SALDO_INSUFICIENTE",       # 4 - Tiene menos de $30 de saldo
            "PRODUCTO_SELECCIONADO",    # 5 - El usuario seleccionó un producto (N, L, M)
            "PRODUCTO_VALIDO",          # 6 - El producto existe y hay saldo
            "PRODUCTO_INVALIDO",        # 7 - El producto no existe
            "CONFIRMAR_COMPRA",         # 8 - El usuario confirmó la compra
            "CANCELAR_OPERACION",       # 9 - El usuario canceló
            "PAGO_EXITOSO",             # 10 - El pago se procesó correctamente
            "PAGO_FALLIDO",             # 11 - Falló el procesamiento del pago
            "PRODUCTO_DESPACHADO",      # 12 - El producto fue entregado
            "CAMBIO_DEVUELTO",          # 13 - El cambio fue devuelto
            "REINICIAR",                # 14 - Reiniciar la máquina
            "STOCK_INSUFICIENTE",       # 15 - No hay stock del producto seleccionado
        ]
        
        # Estado inicial
        self.estado_actual = 0
        
        # Variables de transacción
        self.producto_seleccionado = None
        self.cambio_a_devolver = 0
        self.billete_actual = 0
        
        # Historial
        self.historial_estados = []
        
        # Registrar estado inicial
        self.registrar_estado("INICIALIZACION", "Máquina lista para operar")
    
    # ========================================================================
    # MÉTODOS PRINCIPALES MEF
    # ========================================================================
    
    def manejar_evento(self, evento, dato=None):
        """
        Maneja un evento según el estado actual de la MEF
        """
        
        # Convertir evento a índice si es string
        if isinstance(evento, str):
            try:
                evento_idx = self.eventos.index(evento)
            except ValueError:
                return self.error(f"Evento desconocido: {evento}")
        else:
            evento_idx = evento
        
        estado_anterior = self.estado_actual
        resultado = None
        
        # ====================================================================
        # TABLA DE TRANSICIONES DE ESTADO
        # ====================================================================
        
        # ESTADO: ESPERANDO_BILLETE (0)
        if self.estado_actual == 0:
            if evento_idx == 0:  # BILLETE_INSERTADO
                resultado = self.procesar_billete_insertado(dato)
            elif evento_idx == 14:  # REINICIAR
                resultado = self.reiniciar_maquina()
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: VALIDANDO_BILLETE (1)
        elif self.estado_actual == 1:
            if evento_idx == 1:  # BILLETE_VALIDO
                resultado = self.procesar_billete_valido(dato)
            elif evento_idx == 2:  # BILLETE_INVALIDO
                resultado = self.procesar_billete_invalido(dato)
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: ESPERANDO_MAS_DINERO (2)
        elif self.estado_actual == 2:
            if evento_idx == 0:  # BILLETE_INSERTADO
                resultado = self.procesar_billete_insertado(dato)
            elif evento_idx == 9:  # CANCELAR_OPERACION
                resultado = self.cancelar_operacion()
            elif evento_idx == 14:  # REINICIAR
                resultado = self.reiniciar_maquina()
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: LISTO_SELECCION (3)
        elif self.estado_actual == 3:
            if evento_idx == 0:  # BILLETE_INSERTADO (para agregar más dinero)
                resultado = self.procesar_billete_insertado(dato)
            elif evento_idx == 5:  # PRODUCTO_SELECCIONADO
                resultado = self.procesar_producto_seleccionado(dato)
            elif evento_idx == 9:  # CANCELAR_OPERACION
                resultado = self.cancelar_operacion()
            elif evento_idx == 14:  # REINICIAR
                resultado = self.reiniciar_maquina()
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: VALIDANDO_SELECCION (4)
        elif self.estado_actual == 4:
            if evento_idx == 6:  # PRODUCTO_VALIDO
                resultado = self.procesar_producto_valido(dato)
            elif evento_idx == 7:  # PRODUCTO_INVALIDO
                resultado = self.procesar_producto_invalido(dato)
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: ESPERANDO_CONFIRMACION (5)
        elif self.estado_actual == 5:
            if evento_idx == 8:  # CONFIRMAR_COMPRA
                resultado = self.confirmar_compra()
            elif evento_idx == 9:  # CANCELAR_OPERACION
                resultado = self.cancelar_seleccion()
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: PROCESANDO_PAGO (6)
        elif self.estado_actual == 6:
            if evento_idx == 10:  # PAGO_EXITOSO
                resultado = self.procesar_pago_exitoso()
            elif evento_idx == 11:  # PAGO_FALLIDO
                resultado = self.procesar_pago_fallido()
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: DESPACHANDO_PRODUCTO (7)
        elif self.estado_actual == 7:
            if evento_idx == 12:  # PRODUCTO_DESPACHADO
                resultado = self.despachar_producto()
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: DEVOLVIENDO_CAMBIO (8)
        elif self.estado_actual == 8:
            if evento_idx == 13:  # CAMBIO_DEVUELTO
                resultado = self.devolver_cambio2()
            else:
                resultado = self.error(f"Evento {self.eventos[evento_idx]} no permitido en {self.estados[self.estado_actual]}")
            self.siguiente_evento(evento_idx)
        
        # ESTADO: ERROR (9) o CANCELADO (10)
        elif self.estado_actual in [9, 10]:
            if evento_idx == 14:  # REINICIAR
                if self.saldo_actual > 0:
                    self.cancelar_seleccion()
                else:
                    self.cancelar_operacion()
                    resultado = self.reiniciar_maquina()
            else:
                resultado = self.error(f"Máquina en estado {self.estados[self.estado_actual]}. Use REINICIAR")
            self.siguiente_evento(evento_idx)
        
        # ====================================================================
        # REGISTRAR Y RETORNAR RESULTADO
        # ====================================================================
        
        if resultado:
            self.registrar_estado(
                self.eventos[evento_idx],
                f"{resultado['mensaje']} | Estado: {self.estados[estado_anterior]} → {self.estados[self.estado_actual]}"
            )
            
            return resultado
        else:
            return self.error("No se pudo procesar el evento")
    
    # ========================================================================
    # MÉTODOS DE PROCESAMIENTO DE EVENTOS
    # ========================================================================
    
    def procesar_billete_insertado(self, valor):
        """Procesa un billete insertado"""
        if self.validar_stock():
            self.billete_actual = valor
            
            # Cambiar a estado de validación
            self.estado_actual = 1  # VALIDANDO_BILLETE
            
            # Validar billete
            if self.validar_billete(valor):
                return self.manejar_evento(1, valor)  # BILLETE_VALIDO
            else:
                return self.manejar_evento(2, valor)  # BILLETE_INVALIDO
        else:
            return self.manejar_evento(15)  # STOCK_INSUFICIENTE
    
    def procesar_billete_valido(self, valor):
        """Procesa un billete válido"""
        # Actualizamos el saldo actual, segun el monto ingresado por el cliente.
        self.saldo_actual += valor
        
        # Actualizar reservas para los calculos, cantidad de billetes totales ingresados 
        # y el conteo de los billetes ingresados en la operacion actual.
        if valor == 5:
            self.saldo_reservado_5 += 1
            self.cantidad_B5 += 1
            self.cantidad_B5_operacion_actual += 1
        elif valor == 10:
            self.saldo_reservado_10 += 1
            self.cantidad_B10 += 1
            self.cantidad_B10_operacion_actual += 1
        elif valor == 25:
            self.saldo_reservado_25 += 1
            self.cantidad_B25 += 1
            self.cantidad_B25_operacion_actual += 1

        puede_seleccionar = False
        
        # Determinar próximo estado
        for key,val in self.productos.items():
            if self.saldo_actual >= val["precio"]:
                puede_seleccionar = True

        if puede_seleccionar:
            self.estado_actual = 3  # LISTO_SELECCION
            mensaje = f"Billete de ${valor} válido. Saldo: ${self.saldo_actual}. ¡Puede seleccionar producto!"
        else:
            self.estado_actual = 2  # ESPERANDO_MAS_DINERO
            self.falta = self.precio - self.saldo_actual
            mensaje = f"Billete de ${valor} válido. Saldo: ${self.saldo_actual}. Faltan: ${self.falta:.2f}"

        return {
            'exito': True,
            'mensaje': mensaje,
            'saldo': self.saldo_actual,
            'estado': self.estado_actual
        }
    
    def siguiente_evento(self, eve):
        evento = eve
        return evento

    def procesar_billete_invalido(self, valor):
        """Procesa un billete inválido"""
        # Volver a estado inicial
        self.estado_actual = 0  # ESPERANDO_BILLETE
        
        return {
            'exito': False,
            'mensaje': f"Billete de ${valor} no aceptado. Solo $5, $10, $25",
            'saldo': self.saldo_actual,
            'estado': self.estado_actual
        }
    
    def procesar_producto_seleccionado(self, producto):
        """Procesa selección de producto"""
        # Guardar producto seleccionado
        self.producto_seleccionado = producto
        
        # Cambiar a validación
        self.estado_actual = 4  # VALIDANDO_SELECCION
        
        # Validar selección
        if self.producto_seleccionado in self.productos[producto]["nombre"] and self.validar_saldo(self.productos[producto]["precio"]) and self.productos[producto]["stock"] > 0:
            return self.manejar_evento(6, producto)  # PRODUCTO_VALIDO
        else:
            return self.manejar_evento(7, producto)  # PRODUCTO_INVALIDO
    
    def procesar_producto_valido(self, producto):
        """Procesa producto válido"""
        self.estado_actual = 5  # ESPERANDO_CONFIRMACION
        if producto in self.productos:
            nombre_producto = self.productos[producto]["nombre"]
        else:
            nombre_producto = producto
        
        return {
            'exito': True,
            'mensaje': f"{nombre_producto} seleccionado. Precio: ${self.productos[producto]["precio"]}. Confirme la compra.",
            'producto': producto,
            'precio': self.precio,
            'estado': self.estado_actual
        }
    
    def procesar_producto_invalido(self, producto):
        """Procesa producto inválido"""
        self.estado_actual = 3  # LISTO_SELECCION
        self.producto_seleccionado = None
        
        if producto not in self.productos:
            mensaje = f"Producto '{producto}' no válido. Use 'N', 'L' o 'M'."
        else:
            mensaje = f"Saldo insuficiente para {self.productos[producto]["nombre"]}. Necesita: ${self.productos[producto]["precio"]}, Tiene: ${self.saldo_actual}"
        
        return {
            'exito': False,
            'mensaje': mensaje,
            'estado': self.estado_actual,
            'saldo': self.saldo_actual
        }
    
    def confirmar_compra(self):
        """Confirma la compra"""
        self.estado_actual = 6  # PROCESANDO_PAGO
        
        # Procesar pago
        if self.saldo_actual >= self.productos[self.producto_seleccionado]["precio"]:
            # Calcular cambio
            self.cambio_a_devolver = self.saldo_actual - self.productos[self.producto_seleccionado]["precio"]
            self.saldo_actual = 0
            
            # Disparar evento PAGO_EXITOSO
            return self.manejar_evento(10)  # PAGO_EXITOSO
        else:
            # Disparar evento PAGO_FALLIDO
            return self.manejar_evento(11)  # PAGO_FALLIDO
    
    def procesar_pago_exitoso(self):
        """Procesa pago exitoso"""
        self.estado_actual = 7  # DESPACHANDO_PRODUCTO

        if self.producto_seleccionado in self.productos:
            nombre_producto = self.productos[self.producto_seleccionado]["nombre"]
        else:
            nombre_producto = self.producto_seleccionado
        
        return {
            'exito': True,
            'mensaje': f"Pago exitoso. Despachando {nombre_producto}...",
            'producto': self.producto_seleccionado,
            'cambio': self.cambio_a_devolver,
            'estado': self.estado_actual
        }
    
    def procesar_pago_fallido(self):
        """Procesa pago fallido"""
        self.estado_actual = 9  # ERROR
        
        # Devolver el dinero al cliente
        cambio = self.saldo_actual
        self.reiniciar_transaccion(exito=0)
        return {
            'exito': False,
            'mensaje': f"Error en el procesamiento del pago. Se devuelven: ${cambio}",
            'cambio': cambio,
            'estado': self.estado_actual
        }
    
    def despachar_producto(self):
        """Despacha el producto"""
        self.actualizar_stock(self.producto_seleccionado)

        # Si hay cambio, ir a estado de devolución
        if self.cambio_a_devolver > 0:
            self.estado_actual = 8  # DEVOLVIENDO_CAMBIO
            mensaje = f"Producto entregado. Preparando cambio: ${self.cambio_a_devolver}"
            self.manejar_evento(13)  # CAMBIO_DEVUELTO
            return {
                'exito': True,
                'mensaje': mensaje,
                'estado': self.estado_actual,
                'cambio': self.cambio_a_devolver
            }
        else:
            # Sin cambio, reiniciar directamente
            self.reiniciar_transaccion(exito=1)
            self.estado_actual = 0  # ESPERANDO_BILLETE
            mensaje = "Producto entregado. ¡Gracias por su compra!"
            # self.manejar_evento(14)  # REINICIAR
            return {
                'exito': True,
                'mensaje': mensaje,
                'estado': self.estado_actual
            }
    
    # Función para devolución de cambio.
    # NOTA: A diferencia de la función anterior, esta distribuye el monto a devolver entre los
    #       billetes disponibles de manera mas uniforme. Ejemplo: para dar un vuelto de 100$, 
    #       utilizara 3 billetes de $25, 2 de 10$ y 1 de 5$. Incluye ademas dos revisiones a la
    #       reserva, para encontrar la forma de cubrir el monto a devolver cuidando en lo posible
    #       no agotar los billetes disponibles para cualquier denominacion. Vigila tambien si el
    #       monto de la devolución es par y las cantidades de billetes de 25$ y 5$ que puede dar,
    #       para distribuir el monto dependiendo de la existencia de los billetes en la reserva.
    #
    #       Si se desea cambiar el número de billetes máximos que se dan de cada denominación, sólo
    #       hay que modificar la iteracion en que la bandera respectiva se vuelve 'True'.
    def devolver_cambio2(self):
        """Devuelve el cambio"""
        # Se guarda el cambio total a devolver junto con las reservas iniciales para el cálculo.
        cambio = self.cambio_a_devolver
        saldo_inicial_25 = self.saldo_reservado_25
        saldo_inicial_10 = self.saldo_reservado_10
        saldo_inicial_5 = self.saldo_reservado_5
        cambio_inicial = cambio
        # self.reiniciar_transaccion()
        
        # Se verifica si el monto del cambio es par y la cantidad de billetes que pueden darse de
        # cada denominación para cubrirlo (sin contar las reservas).
        cambio_par = int(cambio % 2) == 0
        cambio_25 = int(cambio // 25)
        cambio_10 = int(cambio // 10)
        cambio_5 = int(cambio // 5)

        # Variables de control para la operación de devolución.
        vuelto_B5 = 0
        vuelto_B10 = 0          # Contadores de los billetes del vuelto dado de cada denominación.
        vuelto_B25 = 0
        procesar_vuelto = True  # Variable de control del bucle 'while'.
        num_revision = 0        # Número de revisión de las reservas (se admiten hasta dos revisiones).
        min_B25 = False
        min_B10 = False         # Banderas para determinar si ya se dió el monto mínimo para cada denominación (2 o 3 a lo sumo, según el caso)
        min_B5 = False

        # Función que ajusta la cantidad de billetes de $25 que pueden darse de acuerdo a ciertos
        # parámetros (si el cambio es par, la cantidad de billetes que pueden darse, si dicha cantidad
        # de billetes es par, si hay billetes de $5 en la reserva y el número de iteración).
        # Según el caso, pueden darse 1, 2 o 3 billetes máximo. Se llama solo en el cálculo de los
        # billetes de $25 a devolver.
        def verificar_monto_minimo_B25(camb_par, camb_25, camb_25_par, iter):
            if camb_par and camb_25 == 1 and self.saldo_reservado_5 > 0:
                print("Cambio par, cantidad de $25 a dar igual a 1 y hay billetes de $5 para dar.")
                return None
            elif camb_par and camb_25 == 1 and self.saldo_reservado_5 <= 0:
                print("Cambio par, cantidad de $25 a dar igual a 1 y no hay billetes de $5 para dar.")
                return True
            elif camb_par and not camb_25_par and self.saldo_reservado_5 > 0:
                if iter == 3:
                    print("Cambio par, cantidad de $25 a dar impar y hay billetes de $5 para dar.")
                    return True
            elif camb_par and not camb_25_par and self.saldo_reservado_5 <= 0:
                if iter == 2:
                    print("Cambio par, cantidad de $25 a dar impar y no hay billetes de $5 para dar.")
                    return True
            elif camb_par and camb_25_par and self.saldo_reservado_5 > 0:
                if iter == 3:
                    print("Cambio par, cantidad de $25 a dar par y hay billetes de $5 para dar.")
                    return True
            elif camb_par and camb_25_par and self.saldo_reservado_5 <= 0:
                if iter == 2:
                    print("Cambio par, cantidad de $25 a dar par y no hay billetes de $5 para dar.")
                    return True
            elif not camb_par and camb_25_par and self.saldo_reservado_5 > 0:
                if iter == 2:
                    print("Cambio impar, cantidad de $25 a dar par y hay billetes de $5 para dar.")
                    return True
            elif not camb_par and camb_25_par and self.saldo_reservado_5 <= 0:
                if iter == 3:
                    print("Cambio impar, cantidad de $25 a dar par y no hay billetes de $5 para dar.")
                    return True
            elif not camb_par and not camb_25_par and self.saldo_reservado_5 > 0:
                if iter == 2:
                    print("Cambio impar, cantidad de $25 a dar impar y hay billetes de $5 para dar.")
                    return True
            elif not camb_par and not camb_25_par and self.saldo_reservado_5 <= 0:
                if iter == 3:
                    print("Cambio impar, cantidad de $25 a dar impar y no hay billetes de $5 para dar.")
                    return True

        print(f"Para ${cambio} pueden darse:\nBilletes de 5$: {cambio_5}\nBilletes de 10$: {cambio_10}\nBilletes de 25$: {cambio_25}")

        # Bucle principal de revisión de reservas.
        while procesar_vuelto:

            # Condicional para devolver billetes de 25$.
            if cambio_25 > 0 and self.saldo_reservado_25 > 0 and cambio >= 25 and not min_B25:
                print(f"{self.saldo_reservado_5}, {self.saldo_reservado_10}, {self.saldo_reservado_25}, {cambio}")
                iter_25 = cambio_25               # Guardamos la cantidad posible de billetes a dar.
                iter_25_par = (iter_25 % 2) == 0  # Verificamos si dicha cantidad es par.
                for i in range(iter_25):          # Iteramos de acuerdo a la cantidad posible.
                    
                    # Verificamos el número de revisión para ajustar la cantidad mínima a devolver.
                    if num_revision == 0:
                        min_B25 = verificar_monto_minimo_B25(cambio_par, iter_25, iter_25_par, i)

                        # Si se alcanzó la cantidad mínima, salimos del bucle. Esta bandera también
                        # asegura que en las siguientes iteraciones del bucle 'while' no volvamos
                        # a dar billetes de $25.
                        if min_B25:
                            print("Tres billetes de 25$ dados.")
                            break
                    elif num_revision == 1:
                        min_B25 = verificar_monto_minimo_B25(cambio_par, iter_25, iter_25_par, i)
                        if min_B25:
                            print("Tres billetes de 25$ dados nuevamente.")
                            break
                    
                    # Si hay billetes ingresados por el cliente, además de los disponibles en reserva,
                    # actualizamos el contador total (el que está en la interfaz).
                    if self.cantidad_B25 > 0 and self.saldo_reservado_25 > 0:
                        self.cantidad_B25 -= 1
                        self.saldo_reservado_25 -= 1
                        cambio -= 25                   # Se restan $25 al vuelto en cada iteración.
                        vuelto_B25 += 1                # Contamos los billetes de $25 devueltos.
                        cambio_25 -= 1                 # Disminuimos la cantidad posible a dar.
                    elif self.saldo_reservado_25 > 0:  # Si no hay billetes ingresados por el cliente, actualizamos las variables internas.
                        self.saldo_reservado_25 -= 1
                        cambio -= 25
                        vuelto_B25 += 1
                        cambio_25 -= 1
                    else:
                        print("Billetes de $25 agotados.")

                    # Si se cubre todo el cambio, retornamos los resultados.
                    if cambio == 0:
                        print(f"{self.saldo_reservado_5}, {self.saldo_reservado_10}, {self.saldo_reservado_25}, {cambio}")

                        # Actualizamos la variable de control del bucle 'while' y las reservas totales.
                        # Sumamos al saldo total (los ingresos) el precio de los productos.
                        procesar_vuelto = False
                        self.saldo_reservado = 25*self.saldo_reservado_25 + 10*self.saldo_reservado_10 + 5*self.saldo_reservado_5
                        self.saldo += self.productos[self.producto_seleccionado]["precio"]

                        self.estado_actual = 0
                        self.reiniciar_transaccion(exito=1)

                        return {
                            'exito': True,
                            'mensaje': f"Cambio de ${cambio_inicial} devuelto.\nBilletes de 5$: {vuelto_B5}\nBilletes de 10$: {vuelto_B10}\nBilletes de 25$: {vuelto_B25}\n¡Gracias por su compra!",
                            'cambio': cambio_inicial,
                            'vuelto_B5': vuelto_B5,
                            'vuelto_B10': vuelto_B10,
                            'vuelto_B25': vuelto_B25,
                            'estado': self.estado_actual
                        }
                    
                # Si el monto del cambio aún no ha sido cubierto, actualizamos la cantidad posible
                # de billetes a dar según el monto restante.
                cambio_25 = int(cambio // 25)
                cambio_10 = int(cambio // 10)
                cambio_5 = int(cambio // 5)
            
            # Condicional para devolver billetes de $10.
            if cambio_10 > 0 and self.saldo_reservado_10 > 0 and cambio >= 10 and not min_B10:
                print(f"{self.saldo_reservado_5}, {self.saldo_reservado_10}, {self.saldo_reservado_25}, {cambio}")
                print("Se metio aqui")
                iter_10 = cambio_10      # Guardamos la cantidad posible de billetes para el vuelto.
                for i in range(iter_10): # Iteramos sobre la cantidad anterior.

                    # Controlamos la cantidad de billetes dados para una revisión determinada.
                    # Si se dan tres billetes, salimos del bucle.
                    if iter_10 >= 3 and num_revision == 0:
                        if i == 3:
                            print("Tres billetes de 10$ dados.")
                            min_B10 = True
                            break
                    elif iter_10 >= 3:
                        if i == 3:
                            print("Tres billetes de 10$ dados nuevamente.")
                            min_B10 = True
                            break
                    
                    # Actualizamos las variables internas y para la interfaz según el caso.
                    if self.cantidad_B10 > 0 and self.saldo_reservado_10 > 0:
                        self.cantidad_B10 -= 1
                        self.saldo_reservado_10 -= 1
                        cambio -= 10
                        vuelto_B10 += 1
                        cambio_10 -= 1
                    elif self.saldo_reservado_10 > 0:
                        self.saldo_reservado_10 -= 1
                        cambio -= 10
                        vuelto_B10 += 1
                        cambio_10 -= 1
                    else:
                        print("Billetes de $10 agotados.")

                    # Si se cubrió el vuelto completo, retornamos los resultados.
                    if cambio == 0:
                        print(f"{self.saldo_reservado_5}, {self.saldo_reservado_10}, {self.saldo_reservado_25}, {cambio}")
                        # Actualizamos la variable de control del bucle 'while' y las reservas.
                        # Sumamos al saldo total (los ingresos) el precio de los productos.
                        procesar_vuelto = False
                        self.saldo_reservado = 25*self.saldo_reservado_25 + 10*self.saldo_reservado_10 + 5*self.saldo_reservado_5
                        self.saldo += self.productos[self.producto_seleccionado]["precio"]

                        self.estado_actual = 0
                        self.reiniciar_transaccion(exito=1)

                        return {
                            'exito': True,
                            'mensaje': f"Cambio de ${cambio_inicial} devuelto.\nBilletes de 5$: {vuelto_B5}\nBilletes de 10$: {vuelto_B10}\nBilletes de 25$: {vuelto_B25}\n¡Gracias por su compra!",
                            'cambio': cambio_inicial,
                            'vuelto_B5': vuelto_B5,
                            'vuelto_B10': vuelto_B10,
                            'vuelto_B25': vuelto_B25,
                            'estado': self.estado_actual
                        }
                
                # Actualizamos la cantidad posible de billetes a dar a partir del cambio
                # restante.
                cambio_25 = int(cambio // 25)
                cambio_10 = int(cambio // 10)
                cambio_5 = int(cambio // 5)
                
            # Condicional para devolver billetes de $5.
            if cambio_5 > 0 and self.saldo_reservado_5 > 0 and cambio >= 5 and not min_B5:
                print(f"{self.saldo_reservado_5}, {self.saldo_reservado_10}, {self.saldo_reservado_25}, {cambio}")
                print("Se metio aqui tambien")
                iter_5 = cambio_5       # Guardamos la cantidad de billetes posible.
                for i in range(iter_5): # Iteramos sobre dicha cantidad.

                    # Validamos la cantidad de billetes mínimos dados.
                    if iter_5 >= 5 and num_revision == 0:
                        if i == 5:
                            print("Tres billetes de $5 dados.")
                            min_B5 = True
                            break
                    elif iter_5 >= 5:
                        if i == 5:
                            print("Tres billetes de $5 dados nuevamente.")
                            min_B5 = True
                            break
                    
                    # Actualizamos las variables internas y para la interfaz según el caso.
                    if self.cantidad_B5 > 0 and self.saldo_reservado_5 > 0:
                        self.cantidad_B5 -= 1
                        self.saldo_reservado_5 -= 1
                        cambio -= 5
                        vuelto_B5 += 1
                        cambio_5 -= 1
                    elif self.saldo_reservado_5 > 0:
                        self.saldo_reservado_5 -= 1
                        cambio -= 5
                        vuelto_B5 += 1
                        cambio_5 -= 1
                    else:
                        print("Billetes de $5 agotados.")
                
                    # Si el monto fue cubierto, retornamos los resultados.
                    if cambio == 0:
                        print(f"{self.saldo_reservado_5}, {self.saldo_reservado_10}, {self.saldo_reservado_25}, {cambio}")
                        
                        # Actualizamos la variable de control del bucle 'while' y las reservas.
                        # Sumamos al saldo total (los ingresos) el precio de los productos.
                        procesar_vuelto = False
                        self.saldo_reservado = 25*self.saldo_reservado_25 + 10*self.saldo_reservado_10 + 5*self.saldo_reservado_5
                        self.saldo += self.productos[self.producto_seleccionado]["precio"]

                        self.estado_actual = 0
                        self.reiniciar_transaccion(exito=1)

                        return {
                            'exito': True,
                            'mensaje': f"Cambio de ${cambio_inicial} devuelto.\nBilletes de 5$: {vuelto_B5}\nBilletes de 10$: {vuelto_B10}\nBilletes de 25$: {vuelto_B25}\n¡Gracias por su compra!",
                            'cambio': cambio_inicial,
                            'vuelto_B5': vuelto_B5,
                            'vuelto_B10': vuelto_B10,
                            'vuelto_B25': vuelto_B25,
                            'estado': self.estado_actual
                        }
                
                # Actualizamos la cantidad de billetes posible a dar en caso de que aún quede
                # vuelto por dar.
                cambio_25 = int(cambio // 25)
                cambio_10 = int(cambio // 10)
                cambio_5 = int(cambio // 5)
                
            # Si al completar dos revisiones de las reservas aún queda cambio por dar, retornamos
            # los resultados y la operacion como fallida.
            if num_revision >= 1:
                print(f"{self.saldo_reservado_5}, {self.saldo_reservado_10}, {self.saldo_reservado_25}, {cambio}")

                # Actualizamos la variable de control del bucle 'while' y reestablecemos los valores
                # de las reservas y la cantidad de billetes a sus valores originales.
                procesar_vuelto = False
                self.saldo_reservado_25 = saldo_inicial_25
                self.saldo_reservado_10 = saldo_inicial_10
                self.saldo_reservado_5 = saldo_inicial_5
                self.cantidad_B25 += vuelto_B25
                self.cantidad_B10 += vuelto_B10
                self.cantidad_B5 += vuelto_B5
                self.saldo_reservado = 25*self.saldo_reservado_25 + 10*self.saldo_reservado_10 + 5*self.saldo_reservado_5

                self.estado_actual = 0
                self.reiniciar_transaccion(exito=0)

                return {
                        'exito': False,
                        'mensaje': f"Cambio de ${cambio_inicial}. No se dispone de billetes para devolucion completa",
                        'cambio': cambio_inicial,
                        'estado': self.estado_actual
                    }
            
            # Si al terminar las devoluciones respectivas aún queda cambio por dar y es la primera
            # revision a las reservas, reiniciamos las banderas a 'False' y aumentamos el número
            # de revisión.
            if num_revision == 0 and cambio != 0:
                min_B25 = False
                min_B10 = False
                min_B5 = False
                num_revision += 1
    
    def cancelar_operacion(self):
        """Cancela la operación completa"""
        cambio = self.saldo_actual
        self.cambio_a_devolver = cambio
        self.estado_actual = 10  # CANCELADO
        
        # Devolver dinero
        self.reiniciar_transaccion(exito=0)
        
        return {
            'exito': True,
            'mensaje': f"Operación cancelada. Se devuelven: ${cambio}",
            'cambio': cambio,
            'estado': self.estado_actual
        }
    
    def cancelar_seleccion(self):
        """Cancela solo la selección (no la operación completa)"""
        self.producto_seleccionado = None
        self.estado_actual = 3  # LISTO_SELECCION
        
        return {
            'exito': True,
            'mensaje': "Selección cancelada. Puede seleccionar otro producto.",
            'estado': self.estado_actual,
            'saldo': self.saldo_actual
        }
    
    def reiniciar_maquina(self):
        """Reinicia completamente la máquina"""
        self.reiniciar_transaccion(exito=2)
        self.estado_actual = 0  # ESPERANDO_BILLETE
        
        return {
            'exito': True,
            'mensaje': "Máquina reiniciada. Lista para nueva operación.",
            'estado': self.estado_actual
        }
    
    def reiniciar_transaccion(self, exito):
        """Reinicia solo la transacción actual"""
        # se reinician el monto ingresado por el cliente y las variables de control de transacciones
        self.saldo_actual = 0
        self.producto_seleccionado = None
        self.cambio_a_devolver = 0
        self.billete_actual = 0

        # Si la operación fue exitosa (1), reiniciamos el contador de billetes de la operación actual.
        # De lo contrario (0), deben reiniciarse tambien las variables internas modificadas.
        # Si exito == 2, devolvemos la máquina a su estado original.
        if exito == 1:
            self.cantidad_B25_operacion_actual = 0
            self.cantidad_B10_operacion_actual = 0
            self.cantidad_B5_operacion_actual = 0
        elif exito == 0:
            # Restamos de la cantidad total de billetes de cada denominación y sus reservas la 
            # cantidad específica ingresada para cada una por el cliente.
            if self.cantidad_B25_operacion_actual > 0:
                self.cantidad_B25 -= self.cantidad_B25_operacion_actual
                self.saldo_reservado_25 -= self.cantidad_B25_operacion_actual
                self.cantidad_B25_operacion_actual = 0
            
            if self.cantidad_B10_operacion_actual > 0:
                self.cantidad_B10 -= self.cantidad_B10_operacion_actual
                self.saldo_reservado_10 -= self.cantidad_B10_operacion_actual
                self.cantidad_B10_operacion_actual = 0

            if self.cantidad_B5_operacion_actual > 0:
                self.cantidad_B5 -= self.cantidad_B5_operacion_actual
                self.saldo_reservado_5 -= self.cantidad_B5_operacion_actual
                self.cantidad_B5_operacion_actual = 0
        elif exito == 2:

            self.saldo = 0
            self.saldo_reservado_5 = 8
            self.saldo_reservado_10 = 5
            self.saldo_reservado_25 = 3
            self.saldo_reservado = 25*self.saldo_reservado_25 + 10*self.saldo_reservado_10 + 5*self.saldo_reservado_5

            self.cantidad_B5 = 0
            self.cantidad_B10 = 0
            self.cantidad_B25 = 0

            self.cantidad_B5_operacion_actual = 0
            self.cantidad_B10_operacion_actual = 0
            self.cantidad_B25_operacion_actual = 0
            self.saldo_actual = 0
    
    def error(self, mensaje):
        """Maneja errores"""
        self.estado_actual = 0  # ESPERANDO_BILLETE
        
        self.registrar_estado("ERROR", mensaje)
        
        if self.saldo_actual > 0:
            self.cambio_a_devolver = self.saldo_actual
            self.devolver_cambio2()
            
        self.manejar_evento(14)

        self.reiniciar_transaccion(exito=0)

        return {
            'exito': False,
            'mensaje': f"ERROR: {mensaje}",
            'estado': self.estado_actual
        }
    
    def validar_billete(self, valor):
        if valor in [5, 10, 25]:
            return True
        return False
    
    def validar_saldo(self, precio):
        if precio > self.saldo_actual:
            return False
        return True
    
    def registrar_estado(self, evento, descripcion):
        """Registra un cambio de estado en el historial"""
        registro = (
            self.estados[self.estado_actual],  # Estado actual
            evento,                            # Evento que ocurrió
            descripcion,                       # Descripción
            self.saldo,                        # Saldo actual
            self.producto_seleccionado         # Producto seleccionado
        )
        self.historial_estados.append(registro)
    
    def validar_stock(self):
        """Valida si hay stock del producto seleccionado"""
        for key,val in self.productos.items():
            if val["nombre"] == self.productos[key]["nombre"] and self.productos[key]["stock"] > 0:
                return True
        return False
    
    def actualizar_stock(self, producto):
        """Actualiza el stock del producto seleccionado"""
        if producto in self.productos:
            if self.productos[producto]["stock"] > 0:
                self.productos[producto]["stock"] -= 1
                return True
        return False
    
    # ========================================================================
    # MÉTODOS DE CONSULTA Y VISUALIZACIÓN
    # ========================================================================
    
    def obtener_estado_actual(self):
        """Devuelve información del estado actual"""
        return {
            'estado_idx': self.estado_actual,
            'estado_nombre': self.estados[self.estado_actual],
            'saldo': self.saldo,
            'producto_seleccionado': self.producto_seleccionado,
            'cambio_pendiente': self.cambio_a_devolver,
            'billete_actual': self.billete_actual
        }
    
    def obtener_resumen(self):
        """Devuelve un resumen formateado"""
        estado = self.obtener_estado_actual()
        
        resumen = f"""
        ===== MÁQUINA EXPENDEDORA =====
        Estado: {estado['estado_nombre']}
        Saldo: ${estado['saldo']:.2f}
        Producto seleccionado: {estado['producto_seleccionado'] or 'Ninguno'}
        Cambio pendiente: ${estado['cambio_pendiente']:.2f}
        =================================
        """
        return resumen
    
    def obtener_historial(self):
        """Devuelve el historial completo"""
        if not self.historial_estados:
            return "No hay historial registrado"
        
        lineas = []
        lineas.append("=" * 70)
        lineas.append("HISTORIAL DE ESTADOS MEF")
        lineas.append("=" * 70)
        
        for i, registro in enumerate(self.historial_estados):
            # registro: (estado, evento, descripcion, saldo, producto)
            linea = f"[{i:03d}] {registro[0]:25} | Evento: {registro[1]:20} | "
            linea += f"Saldo: ${registro[3]:5.2f} | "
            if registro[4]:
                linea += f"Producto: {registro[4]}"
            else:
                linea += "Producto: ---"
            
            lineas.append(linea)
        
        lineas.append("=" * 70)
        return "\n".join(lineas)
    
    def imprimir_transiciones(self):
        """Imprime las transiciones de estado"""
        print("\n" + "=" * 60)
        print("TRANSICIONES DE ESTADO:")
        print("=" * 60)
        
        if len(self.historial_estados) < 2:
            print("No hay suficientes transiciones")
            return
        
        for i in range(1, len(self.historial_estados)):
            estado_anterior = self.historial_estados[i-1][0]
            estado_actual = self.historial_estados[i][0]
            evento = self.historial_estados[i][1]
            
            print(f"{estado_anterior} → {estado_actual} (por: {evento})")
        
        print("=" * 60)

""" diccio = {
    "N": {"nombre": "Naranja", "stock": 10},
    "M": {"nombre": "Manzana", "stock": 10},
    "L": {"nombre": "Limon", "stock": 10}
}

for i,j in diccio.items():
    print(i,j)
 """

