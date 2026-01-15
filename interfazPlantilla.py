import tkinter as tk
from tkinter import messagebox

COLOR_FONDO = "#808080"
COLOR_FONDO_CLARO = "#c0c0c0"
COLOR_FUENTE_BOTON = "#ffffff"
COLOR_FUENTE_TITULO = "#000000"
COLOR_BOTON_CONTINUAR = "#118844"
COLOR_BOTON_CANCELAR = "#880000"
COLOR_NARANJA = "#dd6600"
COLOR_LIMON = "#ddaa22"
COLOR_MANZANA = "#dd0000"

FUENTE_TITULO = ("Arial", 16, "bold")
FUENTE_NORMAL = ("Arial", 12, "bold")
FUENTE_MONOSPACE = ("Courier New", 12)
FUENTE_MONOSPACE_TITULO = ("Courier New", 16, "bold")

class Plantilla_Interfaz():

    def __init__(self, root):
        self.ventana_principal = root

        self.ventana_principal.minsize(820, 600)
        self.ventana_principal.configure(bg=COLOR_FONDO)

        self.monto_ingresos = 0.0
        self.cnt_B5 = 0
        self.cnt_B10 = 0
        self.cnt_B25 = 0
        self.monto_saldo = 0.0
        self.monto_faltante = 0.0
        self.estado_maquina = "e0"

        self.crear_scroll_vertical()
        self.crear_encabezado()
        self.crear_panel_ingresos()
        self.crear_panel_estado()
        self.crear_botones_jugos()
        self.crear_botones_billetes()
        self.crear_controles_proceso()
        self.crear_indicador_estado()

    def crear_scroll_vertical(self):

        self.marco_principal = tk.Frame(self.ventana_principal, bg=COLOR_FONDO) # , relief="groove", bd=4)
        self.marco_principal.pack(fill="both", expand=True)

        lienzo_scroll = tk.Canvas(self.marco_principal, bg="#0000ff", highlightthickness=0)
        barra_scroll = tk.Scrollbar(self.marco_principal, orient="vertical", command=lienzo_scroll.yview)

        self.marco_principal_contenedor = tk.Frame(lienzo_scroll, bg=COLOR_FONDO_CLARO, relief="groove", bd=4)
        # self.marco_principal_contenedor.pack(fill="both", expand=True, padx=20, pady=20)

        lienzo_scroll.configure(yscrollcommand=barra_scroll.set)
        lienzo_scroll.pack(side="left", fill="both", expand=True)
        barra_scroll.pack(side="right", fill="y")

        ventana_lienzo = lienzo_scroll.create_window((0,0), window=self.marco_principal_contenedor, anchor="nw")

        self.marco_principal_contenedor.bind("<Configure>", lambda e: lienzo_scroll.configure(scrollregion=lienzo_scroll.bbox("all")))
        lienzo_scroll.bind("<Configure>", lambda e: lienzo_scroll.itemconfig(ventana_lienzo, width=e.width))

        def rueda_mouse(event):
            lienzo_scroll.yview_scroll(int(-1*(event.delta/120)), "units")

        lienzo_scroll.bind_all("<MouseWheel>", rueda_mouse)

    def crear_encabezado(self):

        marco_encabezado = tk.Frame(self.marco_principal_contenedor, bg=COLOR_FONDO_CLARO, relief="groove", bd=4)
        marco_encabezado.pack(fill="x", padx=20, pady=10)

        encabezado_etiqueta = tk.Label(marco_encabezado, 
            text="INTERFAZ DE PRUEBAS - PROYECTO No. 2",
            font=FUENTE_TITULO,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO_CLARO,
        ).pack()

    def crear_panel_ingresos(self):

        self.marco_ingresos = tk.Frame(self.marco_principal_contenedor, bg=COLOR_FONDO, relief="groove", bd=4)
        self.marco_ingresos.pack(fill="x", padx=20, pady=(0, 10))

        marco_ingresos_contenedor = tk.Frame(self.marco_ingresos, bg=COLOR_FONDO)
        marco_ingresos_contenedor.pack()

        ingresos_etiqueta = tk.Label(marco_ingresos_contenedor, text="VENTAS TOTALES",
            font=FUENTE_TITULO,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO
        ).grid(row=0, column=0, padx=20, pady= (10, 0)) #.pack(side="left", padx=20, pady=10)

        self.monto_ingresos_etiqueta = tk.Label(marco_ingresos_contenedor,
            text=f"${self.monto_ingresos:.2f}",
            font=FUENTE_MONOSPACE_TITULO,
            fg="#00ff00",
            bg=COLOR_FUENTE_TITULO,
            relief="sunken",
            bd=4
        )
        self.monto_ingresos_etiqueta.grid(row=0, column=1, columnspan=6, sticky="ew", padx=5, pady=(10, 0)) #.pack(side="left", padx=10, pady=10)

        cnt_B_etiqueta = tk.Label(marco_ingresos_contenedor, text="CANTIDAD DE BILLETES",
            font=FUENTE_NORMAL,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO
        ).grid(row=1, column=0, padx=5, pady=10) #.pack(side="bottom", pady=10)

        B5_etiqueta = tk.Label(marco_ingresos_contenedor, text="5$",
            font=FUENTE_NORMAL,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO
        ).grid(row=1, column=1, padx=5, pady=10) #.pack(side="bottom", pady=10)

        self.cnt_B5_etiqueta = tk.Label(marco_ingresos_contenedor,
            text=f"${int(self.cnt_B5)}",
            font=FUENTE_MONOSPACE_TITULO,
            fg="#00ff00",
            bg=COLOR_FUENTE_TITULO,
            relief="sunken",
            bd=4
        )
        self.cnt_B5_etiqueta.grid(row=1, column=2, padx=5, pady=10)

        B10_etiqueta = tk.Label(marco_ingresos_contenedor, text="10$",
            font=FUENTE_NORMAL,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO
        ).grid(row=1, column=3, padx=5, pady=10) #.pack(side="bottom", pady=10)

        self.cnt_B10_etiqueta = tk.Label(marco_ingresos_contenedor,
            text=f"${int(self.cnt_B10)}",
            font=FUENTE_MONOSPACE_TITULO,
            fg="#00ff00",
            bg=COLOR_FUENTE_TITULO,
            relief="sunken",
            bd=4
        )
        self.cnt_B10_etiqueta.grid(row=1, column=4, padx=5, pady=10)

        B25_etiqueta = tk.Label(marco_ingresos_contenedor, text="25$",
            font=FUENTE_NORMAL,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO
        )
        B25_etiqueta.grid(row=1, column=5, padx=5, pady=10) #.pack(side="bottom", pady=10)

        self.cnt_B25_etiqueta = tk.Label(marco_ingresos_contenedor,
            text=f"${int(self.cnt_B25)}",
            font=FUENTE_MONOSPACE_TITULO,
            fg="#00ff00",
            bg=COLOR_FUENTE_TITULO,
            relief="sunken",
            bd=4
        )
        self.cnt_B25_etiqueta.grid(row=1, column=6, padx=5, pady=10)

    def crear_panel_estado(self):

        self.marco_estado = tk.Frame(self.marco_principal_contenedor, bg=COLOR_FUENTE_TITULO, relief="sunken", bd=4)
        self.marco_estado.pack(fill="x", padx=20, pady=(0,10))

        marco_estado_contenedor = tk.Frame(self.marco_estado, bg=COLOR_FUENTE_TITULO)
        marco_estado_contenedor.pack()

        self.estado_etiqueta = tk.Label(marco_estado_contenedor,
            text="INGRESE LOS BILLETES PARA COMPRAR UNA BEBIDA",
            font=FUENTE_MONOSPACE_TITULO,
            fg="#ffff00",
            bg=COLOR_FUENTE_TITULO,
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        self.saldo_etiqueta = tk.Label(marco_estado_contenedor,
            text=f"SALDO: ${self.monto_saldo:.2f}",
            font=FUENTE_MONOSPACE,
            fg="#00ff00",
            bg=COLOR_FUENTE_TITULO
        )
        self.saldo_etiqueta.grid(row=1, column=0, pady=(0,10), padx=20)

        self.restante_etiqueta = tk.Label(marco_estado_contenedor,
            text=f"RESTANTE: ${self.monto_saldo:.2f}",
            font=FUENTE_MONOSPACE,
            fg=COLOR_MANZANA,
            bg=COLOR_FUENTE_TITULO
        )
        self.restante_etiqueta.grid(row=1, column=1, pady=(0,10), padx=20)

    def crear_botones_jugos(self):

        self.marco_jugos = tk.Frame(self.marco_principal_contenedor, bg=COLOR_FONDO, relief="groove", bd=4)
        self.marco_jugos.pack(fill="x", padx=20, pady=(0,10))

        marco_jugos_etiqueta = tk.Label(self.marco_jugos, text="SELECCIONE LA BEBIDA",
            font=FUENTE_NORMAL,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO
        ).pack(pady=10)

        marco_botones_jugos = tk.Frame(self.marco_jugos, bg=COLOR_FONDO)
        marco_botones_jugos.pack(padx=20, pady=(0,10))

        marco_naranja = tk.Frame(marco_botones_jugos)
        marco_naranja.grid(row=0, column=0, padx=20, pady=10)

        self.boton_naranja = tk.Button(marco_naranja, 
            text=f"NARANJA\n(N)\n30$",
            font=FUENTE_NORMAL,
            bg=COLOR_NARANJA, 
            fg=COLOR_FUENTE_BOTON,
            width=12,
            height=4,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("N"))
        )
        self.boton_naranja.pack()

        marco_limon = tk.Frame(marco_botones_jugos)
        marco_limon.grid(row=0, column=1, padx=20, pady=10)

        self.boton_limon = tk.Button(marco_limon, 
            text=f"LIMON\n(L)\n30$",
            font=FUENTE_NORMAL,
            bg=COLOR_LIMON, 
            fg=COLOR_FUENTE_BOTON,
            width=12,
            height=4,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("L"))
        )
        self.boton_limon.pack()

        marco_manzana = tk.Frame(marco_botones_jugos)
        marco_manzana.grid(row=0, column=2, padx=20, pady=10)

        self.boton_manzana = tk.Button(marco_manzana, 
            text=f"MANZANA\n(M)\n30$",
            font=FUENTE_NORMAL,
            bg=COLOR_MANZANA, 
            fg=COLOR_FUENTE_BOTON,
            width=12,
            height=4,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("M"))
        )
        self.boton_manzana.pack()

    def crear_botones_billetes(self):
        
        self.marco_billetes = tk.Frame(self.marco_principal_contenedor, bg=COLOR_FONDO, relief="groove", bd=4)
        self.marco_billetes.pack(fill="x", padx=20, pady=(0,10))

        marco_billetes_contenedor = tk.Frame(self.marco_billetes, bg=COLOR_FONDO)
        marco_billetes_contenedor.pack(pady=10)

        self.boton_B5 = tk.Button(marco_billetes_contenedor,
            text="$5",
            font=FUENTE_TITULO,
            fg=COLOR_FUENTE_BOTON,
            bg=COLOR_FONDO_CLARO,
            width=8,
            height=2,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("5"))
        )
        self.boton_B5.grid(row=1, column=0, padx=10, pady=(0,10))

        self.boton_B10 = tk.Button(marco_billetes_contenedor,
            text="$10",
            font=FUENTE_TITULO,
            fg=COLOR_FUENTE_BOTON,
            bg=COLOR_FONDO_CLARO,
            width=8,
            height=2,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("10"))
        )
        self.boton_B10.grid(row=1, column=1, padx=10, pady=(0,10))

        self.boton_B25 = tk.Button(marco_billetes_contenedor,
            text="$25",
            font=FUENTE_TITULO,
            fg=COLOR_FUENTE_BOTON,
            bg=COLOR_FONDO_CLARO,
            width=8,
            height=2,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("25"))
        )
        self.boton_B25.grid(row=1, column=2, padx=10, pady=(0,10))

    def crear_controles_proceso(self):

        self.marco_controles = tk.Frame(self.marco_principal_contenedor, bg=COLOR_FONDO, relief="groove", bd=4)
        self.marco_controles.pack(fill="x", padx=20, pady=(0,10))

        marco_controles_contenedor = tk.Frame(self.marco_controles, bg=COLOR_FONDO)
        marco_controles_contenedor.pack(pady=10)

        self.boton_continuar = tk.Button(marco_controles_contenedor,
            text="CONTINUAR\nPROCESO",
            font=FUENTE_MONOSPACE_TITULO,
            fg=COLOR_FUENTE_BOTON,
            bg=COLOR_BOTON_CONTINUAR,
            width=12,
            height=3,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("Continuar"))
        )
        self.boton_continuar.grid(row=0, column=0, padx=10)

        self.boton_cancelar = tk.Button(marco_controles_contenedor,
            text="FINALIZAR\nPROCESO",
            font=FUENTE_MONOSPACE_TITULO,
            fg=COLOR_FUENTE_BOTON,
            bg=COLOR_BOTON_CANCELAR,
            width=12,
            height=3,
            relief="raised",
            bd=4,
            command=lambda: print(self.leer_evento("Cancelar"))
        )
        self.boton_cancelar.grid(row=0, column=1, padx=10)

    def crear_indicador_estado(self):
        
        self.marco_indicador_estado = tk.Frame(self.marco_principal_contenedor, bg=COLOR_FONDO_CLARO)
        self.marco_indicador_estado.pack(fill="x", padx=20, pady=(0,10))

        self.indicador_estado_etiqueta = tk.Label(self.marco_indicador_estado,
            text=f"ESTADO ACTUAL DE LA MAQUINA: {self.estado_maquina}",
            font=FUENTE_MONOSPACE_TITULO,
            fg=COLOR_FUENTE_TITULO,
            bg=COLOR_FONDO_CLARO,
        )
        self.indicador_estado_etiqueta.pack()

    def leer_evento(self, evento):
        if hasattr(self, 'boton_naranja') and evento == 'N':
            return 'Boton Naranja'
        elif hasattr(self, 'boton_limon') and evento == 'L':
            return 'Boton Limon'
        elif hasattr(self, 'boton_manzana') and evento == 'M':
            return 'Boton Manzana'
        elif hasattr(self, 'boton_B5') and evento == '5':
            return '5'
        elif hasattr(self, 'boton_B10') and evento == '10':
            return '10'
        elif hasattr(self, 'boton_B25') and evento == '25':
            return '25'
        elif hasattr(self, 'boton_continuar') and evento == 'Continuar':
            return 'Boton Continuar'
        elif hasattr(self, 'boton_cancelar') and evento == 'Cancelar':
            return 'Boton Cancelar'
        else:
            return None

    def mostrar_evento(self, evento):
        print(f"Evento recibido: {evento}")

    def hay_evento(self):
        if self.leer_evento() is not None:
            return True
        return False
    
    def actualizar_interfaz(self, monto_ingresos, cnt_B5, cnt_B10, cnt_B25, monto_saldo, monto_faltante, estado_maquina):
        self.monto_ingresos = monto_ingresos
        self.cnt_B5 = cnt_B5
        self.cnt_B10 = cnt_B10
        self.cnt_B25 = cnt_B25
        self.monto_saldo = monto_saldo
        self.monto_faltante = monto_faltante
        self.estado_maquina = estado_maquina

        self.monto_ingresos_etiqueta.config(text=f"${self.monto_ingresos:.2f}")
        self.cnt_B5_etiqueta.config(text=f"{int(self.cnt_B5)}")
        self.cnt_B10_etiqueta.config(text=f"{int(self.cnt_B10)}")
        self.cnt_B25_etiqueta.config(text=f"{int(self.cnt_B25)}")
        self.saldo_etiqueta.config(text=f"SALDO: ${self.monto_saldo:.2f}")
        self.restante_etiqueta.config(text=f"RESTANTE: ${self.monto_faltante:.2f}")
        self.indicador_estado_etiqueta.config(text=f"ESTADO ACTUAL DE LA MAQUINA: {self.estado_maquina}")

    def habilitar_botones_monedas(self, habilitar):
        estado = "normal" if habilitar else "disabled"
        self.boton_B5.configure(state=estado)
        self.boton_B10.configure(state=estado)
        self.boton_B25.configure(state=estado)
    
    def habilitar_botones_productos(self, habilitar):
        estado = "normal" if habilitar else "disabled"
        self.boton_naranja.configure(state=estado)
        self.boton_limon.configure(state=estado)
        self.boton_manzana.configure(state=estado)

    def habilitar_boton_continuar(self, habilitar):
        estado = "normal" if habilitar else "disabled"
        self.boton_continuar.configure(state=estado)
    
    def habilitar_boton_cancelar(self, habilitar):
        estado = "normal" if habilitar else "disabled"
        self.boton_cancelar.configure(state=estado)

    def crear_alerta(self, titulo, mensaje):
        messagebox.showinfo(titulo, mensaje)