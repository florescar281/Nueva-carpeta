import tkinter as tk

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
        # Conectar los botones de la interfaz directamente a la máquina
        self.ventana.boton_naranja.configure(command=lambda: self.procesar_seleccion("N"))
        self.ventana.boton_limon.configure(command=lambda: self.procesar_seleccion("L"))
        self.ventana.boton_manzana.configure(command=lambda: self.procesar_seleccion("M"))
    
        self.ventana.boton_B5.configure(command=lambda: self.procesar_billete(5))
        self.ventana.boton_B10.configure(command=lambda: self.procesar_billete(10))
        self.ventana.boton_B25.configure(command=lambda: self.procesar_billete(25))
    
        self.ventana.boton_continuar.configure(command=self.procesar_continuar)
        self.ventana.boton_cancelar.configure(command=self.procesar_cancelar)

    def procesar_seleccion(self, producto):
        resultado = self.maquina.manejar_evento("PRODUCTO_SELECCIONADO", producto)
        self.actualizar_interfaz()
        print(f"Se ha seleccionado el producto {producto}: {resultado['mensaje']}")

    def procesar_billete(self, valor):
        resultado = self.maquina.manejar_evento("BILLETE_INSERTADO", valor)
        self.actualizar_interfaz()
        print(f"Se ha insertado un billete de {valor}$: {resultado['mensaje']}")

    def procesar_continuar(self):
        resultado = self.maquina.manejar_evento("CONFIRMAR_COMPRA")
        self.actualizar_interfaz()
        print(f"Continuar: {resultado['mensaje']}")
        if "exito" in resultado and resultado["exito"] and self.maquina.estado_actual != "ERROR":
            self.maquina.manejar_evento("REINICIAR")
            self.actualizar_interfaz()
            print(f"Producto despachado: {resultado['mensaje']}")
        elif "falta" in resultado:
            print(f"Falta dinero: ${resultado['falta']}")

    def procesar_cancelar(self):
        resultado = self.maquina.manejar_evento("CANCELAR_OPERACION")
        self.actualizar_interfaz()
        print(f"Cancelar: {resultado['mensaje']}")

    def actualizar_interfaz(self):
        """Este metodo actualiza los elementos de la interfaz
          grafica segun el estado de la maquina expendedora."""
        self.ventana.actualizar_interfaz(
            self.maquina.saldo,
            self.maquina.cantidad_B5,
            self.maquina.cantidad_B10,
            self.maquina.cantidad_B25,
            self.maquina.saldo_actual,
            self.maquina.falta,
            self.maquina.estado_actual
        )
    

if __name__ == "__main__":
    app = aplicacionPrincipal()