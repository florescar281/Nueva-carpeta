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
        else:
            # Aqui se muestra imformacion de compra exitosa
            if "Producto entregado" in resultado['mensaje'] or "Pago exitoso" in resultado['mensaje']:
                self.mostrar_alerta("Compra Exitosa", resultado['mensaje'], "info")
        
        # Aqui se verifica si tenemos que procesar más eventos
        estado = self.maquina.estado_actual
        if estado == 7: 
            resultado_despacho = self.maquina.manejar_evento("PRODUCTO_DESPACHADO")
            self.actualizar_interfaz()
            print(f"Despacho: {resultado_despacho['mensaje']}")
            
            if not resultado_despacho.get('exito', False):
                self.mostrar_alerta("Error en Despacho", resultado_despacho['mensaje'], "error")
            elif resultado_despacho.get('exito', False):
                # El producto fue despachado exitosamente
                self.mostrar_alerta("Producto Entregado", resultado_despacho['mensaje'], "info")
            
            if self.maquina.estado_actual == 8:  
                resultado_cambio = self.maquina.manejar_evento("CAMBIO_DEVUELTO")
                self.actualizar_interfaz()
                print(f"Cambio: {resultado_cambio['mensaje']}")
                
                if not resultado_cambio.get('exito', False):
                    self.mostrar_alerta("Error en Cambio", resultado_cambio['mensaje'], "error")
                elif resultado_cambio.get('exito', False):
                    # Información detallada del cambio
                    mensaje_cambio = resultado_cambio['mensaje']
                    vuelto_B5 = resultado_cambio.get('vuelto_B5', 0)
                    vuelto_B10 = resultado_cambio.get('vuelto_B10', 0)
                    vuelto_B25 = resultado_cambio.get('vuelto_B25', 0)
                    
                    if vuelto_B5 > 0 or vuelto_B10 > 0 or vuelto_B25 > 0:
                        mensaje_detallado = f"¡Compra exitosa!\n\n"
                        mensaje_detallado += f"{mensaje_cambio.split('¡Gracias por su compra!')[0]}\n"
                        mensaje_detallado += "¡Gracias por su compra!"
                        self.mostrar_alerta("Compra Completada", mensaje_detallado, "info")
                    else:
                        # Si no hay cambio, mostrar mensaje simple de agradecimiento
                        self.mostrar_alerta("Compra Completada", 
                                          "¡Compra exitosa!\n\nProducto entregado.\n¡Gracias por su compra!", 
                                          "info")
                        
                self.maquina.manejar_evento("REINICIAR")
                self.actualizar_interfaz()
        elif estado == 0: 
            # Mostrar alerta de compra exitosa sin cambio
            if resultado.get('exito', False) and "Producto entregado" in resultado['mensaje']:
                self.mostrar_alerta("Compra Completada", 
                                  "¡Compra exitosa!\n\nProducto entregado.\n¡Gracias por su compra!", 
                                  "info")

    def procesar_cancelar(self):
        confirmar = self.mostrar_alerta("Confirmar Cancelación", 
                                       "¿Está seguro de que desea cancelar la operación?\nSe devolverá el dinero ingresado.", 
                                       "yesno")
        
        if confirmar:
            resultado = self.maquina.manejar_evento("CANCELAR_OPERACION")
            self.actualizar_interfaz()
            print(f"Cancelar: {resultado['mensaje']}")
            
            if resultado.get('exito', False):
                self.mostrar_alerta("Operación Cancelada", resultado['mensaje'], "info")
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

        if estado == 0 or estado == 2:  
            self.ventana.habilitar_botones_monedas(True)
            self.ventana.habilitar_botones_productos(False)
            self.ventana.habilitar_boton_continuar(False)
            self.ventana.habilitar_boton_cancelar(True)
        elif estado == 3:  
            self.ventana.habilitar_botones_monedas(False)
            self.ventana.habilitar_botones_productos(True)
            self.ventana.habilitar_boton_continuar(True)
            self.ventana.habilitar_boton_cancelar(True)
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