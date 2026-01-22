import tkinter as tk
from tkinter import messagebox

from interfazPlantilla import Plantilla_Interfaz
from Maquina_Espendedora import MaquinaExpendedora

class aplicacionPrincipal:
    def __init__(self):
        self.maquina = MaquinaExpendedora()
        self.root = tk.Tk()
        self.root.title("Plantilla de Interfaz Grafica - Proyecto No. 2")
        self.root.resizable(True, True)

        self.ancho_pantalla = self.root.winfo_screenwidth()
        self.alto_pantalla = self.root.winfo_screenheight()
        self.ancho_ventana = 820
        self.alto_ventana = 600
        self.centro_x = int(self.ancho_pantalla/2 - self.ancho_ventana/2)
        self.centro_y = int(self.alto_pantalla/2 - self.alto_ventana/2)
        self.root.geometry(f"{self.ancho_ventana}x{self.alto_ventana}+{self.centro_x}+{self.centro_y}")
        self.ventana = Plantilla_Interfaz(self.root)

        self.actualizar_interfaz()

        self.configurar_eventos()

        self.root.mainloop()
        
    def configurar_eventos(self):
        """Conectar los botones de la interfaz directamente a la máquina para que los eventos sean manejados"""
        self.ventana.boton_naranja.configure(command=lambda: self.procesar_seleccion("N"))
        self.ventana.boton_limon.configure(command=lambda: self.procesar_seleccion("L"))
        self.ventana.boton_manzana.configure(command=lambda: self.procesar_seleccion("M"))
    
        self.ventana.boton_B5.configure(command=lambda: self.procesar_billete(5))
        self.ventana.boton_B10.configure(command=lambda: self.procesar_billete(10))
        self.ventana.boton_B25.configure(command=lambda: self.procesar_billete(25))
    
        self.ventana.boton_continuar.configure(command=self.procesar_continuar)
        self.ventana.boton_cancelar.configure(command=self.procesar_cancelar)

    def mostrar_alerta(self, titulo, mensaje, tipo="error"):
        """Muestra una alerta al usuario"""
        if tipo == "error":
            messagebox.showerror(titulo, mensaje)
        elif tipo == "warning":
            messagebox.showwarning(titulo, mensaje)
        elif tipo == "info":
            messagebox.showinfo(titulo, mensaje)
        elif tipo == "yesno":
            return messagebox.askyesno(titulo, mensaje)

    def procesar_seleccion(self, producto):
        resultado = self.maquina.manejar_evento("PRODUCTO_SELECCIONADO", producto)
        self.actualizar_interfaz()
        print(f"Se ha seleccionado el producto {producto}: {resultado['mensaje']}")
        
        if not resultado.get('exito', False):
            self.mostrar_alerta("Error en Selección", resultado['mensaje'], "error")

    def procesar_billete(self, valor):
        resultado = self.maquina.manejar_evento("BILLETE_INSERTADO", valor)
        self.actualizar_interfaz()
        print(f"Se ha insertado un billete de {valor}$: {resultado['mensaje']}")
        
        if not resultado.get('exito', False):
            self.mostrar_alerta("Error en Billete", resultado['mensaje'], "error")
        elif self.maquina.estado_actual == 9:  
            self.mostrar_alerta("Error", resultado['mensaje'], "error")

    def procesar_continuar(self):
        resultado = self.maquina.manejar_evento("CONFIRMAR_COMPRA")
        self.actualizar_interfaz()
        print(f"Continuar: {resultado['mensaje']}")
        
        if not resultado.get('exito', False):
            self.mostrar_alerta("Error en Confirmación", resultado['mensaje'], "error")
            return
        
        estado = self.maquina.estado_actual
        
        # PASO 1: Si estamos en estado 7, despachar producto
        if estado == 7:
            resultado_despacho = self.maquina.manejar_evento("PRODUCTO_DESPACHADO")
            self.actualizar_interfaz()
            print(f"Despacho: {resultado_despacho['mensaje']}")
            
            if not resultado_despacho.get('exito', False):
                self.mostrar_alerta("Error en Despacho", resultado_despacho['mensaje'], "error")
                return
            
            # Después de despachar, verificar si hay cambio
            if self.maquina.estado_actual == 8:
                # Ahora manejar la pregunta del cambio
                self.manejar_cambio_despues_despacho(resultado_despacho)
        
        # PASO 2: Si estamos directamente en estado 8 (después de recargar)
        elif estado == 8:
            self.manejar_cambio_despues_despacho(resultado)
        
        elif estado == 0:
            if resultado.get('exito', False) and "Producto entregado" in resultado['mensaje']:
                self.mostrar_alerta("Compra Completada", 
                                "¡Compra exitosa!\n\nProducto entregado.\n¡Gracias por su compra!", 
                                "info")

    def manejar_cambio_despues_despacho(self, resultado):
        """Maneja la lógica del cambio después de despachar producto"""
        cambio = resultado.get('cambio', 0)
        
        if cambio >= 30:
            respuesta = self.mostrar_alerta(
                "Cambio disponible", 
                f"Tiene ${cambio} de cambio disponible.\n¿Desea usar este dinero para comprar otro producto?",
                "yesno"
            )
            
            if respuesta:
                # Usar cambio para nueva compra
                self.maquina.saldo_actual = cambio
                self.maquina.producto_seleccionado = None
                self.maquina.cambio_a_devolver = 0
                self.maquina.estado_actual = 3
                
                self.actualizar_interfaz()
                self.mostrar_alerta("Saldo disponible", 
                    f"Tiene ${cambio} disponibles para seleccionar otro producto.", 
                    "info")
            else:
                # Devolver cambio en efectivo
                resultado_cambio = self.maquina.manejar_evento("CAMBIO_DEVUELTO")
                self.actualizar_interfaz()
                
                if resultado_cambio.get('exito', False):
                    self.mostrar_alerta("Cambio Devuelto", resultado_cambio['mensaje'], "info")
                    self.maquina.manejar_evento("REINICIAR")
                    self.actualizar_interfaz()
        else:
            # Cambio menor a $30, devolver inmediatamente
            resultado_cambio = self.maquina.manejar_evento("CAMBIO_DEVUELTO")
            self.actualizar_interfaz()
            
            if resultado_cambio.get('exito', False):
                self.mostrar_alerta("Cambio Devuelto", resultado_cambio['mensaje'], "info")
                self.maquina.manejar_evento("REINICIAR")
                self.actualizar_interfaz()
    def procesar_cancelar(self):
        """Procesa la cancelación de la operación."""
        if self.maquina.estado_actual == 5:
            self.mostrar_alerta("Seleccion Cancelada", "Puede seleccionar otro producto.", "info")
            self.maquina.cancelar_seleccion()
            self.actualizar_interfaz()
        else:
            confirmar = self.mostrar_alerta("Confirmar Cancelación", 
                                        "¿Está seguro de que desea cancelar la operación?\nSe devolverá el dinero ingresado.", 
                                        "yesno")
            
            if confirmar:
                resultado = self.maquina.manejar_evento("CANCELAR_OPERACION")
                self.actualizar_interfaz()
                print(f"Cancelar: {resultado['mensaje']}")
                
                if resultado.get('exito', False):
                    self.mostrar_alerta("Operación Cancelada", resultado['mensaje'], "info")
                    self.maquina.manejar_evento("REINICIAR")
                    self.actualizar_interfaz()
                else:
                    self.mostrar_alerta("Error al Cancelar", resultado['mensaje'], "error")

    def actualizar_interfaz(self):
        """Este metodo actualiza los elementos de la interfaz
          grafica segun el estado de la maquina expendedora."""
        
        estado_actual = self.maquina.estado_actual
        estado_nombre = self.maquina.estados[estado_actual] if estado_actual < len(self.maquina.estados) else "DESCONOCIDO"
        
        monto_faltante = max(0, 30 - self.maquina.saldo_actual)
        
        self.ventana.actualizar_interfaz(
            monto_ingresos=self.maquina.saldo,  
            cnt_B5=self.maquina.cantidad_B5,
            cnt_B10=self.maquina.cantidad_B10,
            cnt_B25=self.maquina.cantidad_B25,
            monto_saldo=self.maquina.saldo_actual,  
            monto_faltante=monto_faltante,  
            estado_maquina=estado_nombre
        )
        
        if estado_actual == 9:  
            self.mostrar_alerta("Error del Sistema", 
                              "La máquina ha encontrado un error. Por favor, reinicie la operación.", 
                              "error")
            self.maquina.manejar_evento("REINICIAR")
            self.actualizar_interfaz()
        
        self.controlar_habilitacion_botones()

    def controlar_habilitacion_botones(self):
        """Este metodo controla la habilitacion y deshabilitacion
           de los botones segun el estado de la maquina expendedora."""
        estado = self.maquina.estado_actual
        saldo_actual = self.maquina.saldo_actual

        if estado == 0 or estado == 2:  
            self.ventana.habilitar_botones_monedas(True)
            self.ventana.habilitar_botones_productos(False)
            self.ventana.habilitar_boton_continuar(False)
            if estado == 0:
                self.ventana.habilitar_boton_cancelar(False)
            else:
                self.ventana.habilitar_boton_cancelar(True)
        elif estado == 3:  
            # self.ventana.habilitar_botones_monedas(False)
            # self.ventana.habilitar_botones_productos(True)
            self.ventana.habilitar_boton_continuar(False)
            self.ventana.habilitar_boton_cancelar(True)

            if saldo_actual >= self.maquina.productos["N"]["precio"]:
                self.ventana.habilitar_boton_naranja(True)
            else:
                self.ventana.habilitar_boton_naranja(False)

            if saldo_actual >= self.maquina.productos["L"]["precio"]:
                self.ventana.habilitar_boton_limon(True)
            else:
                self.ventana.habilitar_boton_limon(False)

            if saldo_actual >= self.maquina.productos["M"]["precio"]:
                self.ventana.habilitar_boton_manzana(True)
            else:
                self.ventana.habilitar_boton_limon(False)

        elif estado == 5: 
            self.ventana.habilitar_botones_monedas(False)
            self.ventana.habilitar_botones_productos(False)
            self.ventana.habilitar_boton_continuar(True)
            self.ventana.habilitar_boton_cancelar(True)
        else:
            self.ventana.habilitar_botones_monedas(False)
            self.ventana.habilitar_botones_productos(False)
            self.ventana.habilitar_boton_continuar(False)
            self.ventana.habilitar_boton_cancelar(False)

if __name__ == "__main__":
    app = aplicacionPrincipal()