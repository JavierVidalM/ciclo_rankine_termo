from bokeh.models import ColumnDataSource, Slider
from bokeh.layouts import column, row
from pyXSteam.XSteam import XSteam
from bokeh.plotting import figure
from bokeh.models import Div, Text
from bokeh.io import curdoc
import numpy as np
from bokeh.models import HTMLTemplateFormatter


# Crear la fuente de datos
'''
Las unidades de medida que utiliza el XSteam con el systema "BARE" son las siguiente:
- metros [m]
- kilogramos [kg]
- segundo [sec]
- Kelvin [°K]
- Mega Pascales [MPa]*
- Watts [W]
'''
steamTable = XSteam(XSteam.UNIT_SYSTEM_BARE)


'''
Se define la estructura de datos del grafico como vacío 
para actualizarlo una vez se modifiquen los datos en bokeh
'''
source = ColumnDataSource(data=dict(x=[], y=[]))


def Calcular(TL,TH, CB):
    # Definir valores iniciales
    '''
    TH: Temperatura salida de la caldera
    TL: Temperatura salida del condensador
    CB: Compresión de la bomba (en Mega Pascales)
    
    
    Las temperaturas por la librería de pyXSteam las está 
    calculando actualmente en Kelvin pero los sliders toman
    la temperatura en Celcius.   
    '''
    TH = TH.value + 273.15
    TL = TL.value + 273.15
    
    # PUNTO 1 - Salida del condensador, antes de la bomba
    Temp1 = TL
    Pres1 = 0.01 #10 kPa
    # Se calculan los valores de entalpía y entropía con hL ya que son liquido saturado en este punto del ciclo
    h1 = steamTable.hL_t(Temp1)
    s1 = steamTable.sL_t(Temp1)

    
    # PUNTO 2 - Salida de la bomba, antes de la caldea
    s2 = s1
    Pres2 = CB.value
    Temp2 = steamTable.t_ps(Pres2, s2)
    h2 = steamTable.h_ps(Pres2,s2)
    
    # Calculo del trabajo requerido por la bomba
    W_bmb = -(h2 - h1)
    
    
    # PUNTO 3 - Salida de la caldera, antes de la turbina
    Pres3 = Pres2
    Temp3 = TH
    # Se calculan los valores de entalpía y entropía con hV al ser vapor saturado a alta presión
    h3 = steamTable.hV_p(Pres3)
    s3 = steamTable.sV_t(Temp3)

    
    # PUNTO 4 - Salida de la turbina, antes del condensador --> PUNTO 1 
    s4 = s3
    Pres4 = Pres1
    Temp4 = steamTable.t_ps(Pres4,s4)
    h4 = steamTable.h_ps(Pres4,s4)
    
    #trabajo de la turbina
    W_tur = (h3 - h4)

    # Q de entrada y Q de salida
    Qin = (h3 - h2)
    Qout = (h4 - h1)
    
    # Eficiencia    
    n = ((W_tur + W_bmb)/Qin)*100

    
    Mostrar_resultados(Pres1,Pres2,Pres3,Pres4,Temp1,Temp2,Temp3,Temp4,h1,h2,h3,h4,s1,s2,s3,s4,Qin,Qout,n,W_bmb,W_tur)


def Mostrar_resultados(P1, P2, P3, P4, T1, T2, T3, T4, H1, H2, H3, H4, S1, S2, S3, S4,Qin, Qout, n,W_bmb,W_tur):
        #Proceso 1 
    infopto1temperatura.text = f"Temperatura: {round(T1,4)} [°K]"
    infopto1presion.text = f"Presión: {round(P1,4)} [MPa]"
    infopto1entalpia.text = f"Entalpía: {round(H1,4)} [kJ/kg]"
    infopto1entropia.text = f"Entropía: {round(S1,4)} [kJ/kg]"
    #Proceso 2 
    infopto2temperatura.text = f"Temperatura: {round(T2,4)} [°K]"
    infopto2presion.text = f"Presión: {round(P2,4)} [MPa]"
    infopto2entalpia.text = f"Entalpía: {round(H2,4)} [kJ/kg]"
    infopto2entropia.text = f"Entropía: {round(S2,4)} [kJ/kg]"

    #Proceso 3 
    infopto3temperatura.text = f"Temperatura: {round(T3,4)} [°K]"
    infopto3presion.text = f"Presión: {round(P3,4)} [MPa]"
    infopto3entalpia.text = f"Entalpía: {round(H3,4)} [kJ/kg]"
    infopto3entropia.text = f"Entropía: {round(S3,4)} [kJ/kg]"

    #Proceso 4
    infopto4temperatura.text = f"Temperatura: {round(T4,4)} [°K]"
    infopto4presion.text = f"Presión: {round(P4,4)} [MPa]"
    infopto4entalpia.text = f"Entalpía: {round(H4,4)} [kJ/kg]"
    infopto4entropia.text = f"Entropía: {round(S4,4)} [kJ/kg]"
    #Datos eficiencia
    infobomba.text=f"El trabajo requerido por la bomba es de: {round(W_bmb,4)} [kJ/kg]"
    infoturbina.text=f"El trabajo que produce la turbina es de: {round(W_tur,4)} [kJ/kg]"
    eficiencia.text=f"La eficiencia del sistema es de un {round(n,2)}%"
    
    Qentrada.text=f"Q de entrada: {round(Qin,4)} [kJ/kg]"
    Qsalida.text=f"Q de salida: {round(Qout,4)} [kJ/kg]"

    entropia = [S1, S2, S3, S4]
    temperatura = [T1, T2, T3, T4]
    actualizar_grafico(entropia, temperatura)


# Actualizar la función de gráficos
def actualizar_grafico(entropia, temperatura):
    source.data = dict(x=entropia, y=temperatura)


# Widgets
plot = figure(
    height = 500,
    width = 500,
    title = "Ciclo Rankine",
    tools = "pan, reset, save, wheel_zoom",
    toolbar_location = 'above',
    x_axis_label = "Entropía",
    y_axis_label = "Temperatura (K)",
    x_range = (-1, 10),
    y_range = (200, 800)
)

plot.line(
    'x',
    'y',
    source = source,
    line_width = 3,
    line_alpha = 0.6
)

titulo = Div(
    text = "<h1>Ciclo de rankine</h1>"
)

temperatura_H = Slider(
    title ="Temperatura de salida Caldera (°C)",
    value = 200,
    start = 150,
    end = 370,
    step = 10
)

temperatura_L = Slider(
    title ="Temperatura de salida Condensador (°C)",
    value = 30,
    start = 5,
    end = 80,
    step = 5
)


compresion_bomba = Slider(
    title = "Compresión de salida de la Bomba (MPa)",
    value = 5,
    start = 5.0,
    end = 20.0,
    step = 1
)

# Actualizar los valores de los sliders
temperatura_L.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,compresion_bomba))
temperatura_H.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,compresion_bomba))
compresion_bomba.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,compresion_bomba))


# Configuración de los textos de información

# Punto 1
infopto1temperatura = Div(width=400, height=10)
infopto1presion = Div(width=400, height=10)
infopto1entalpia = Div(width=400, height=10)
infopto1entropia = Div(width=400, height=10)

# Punto 2
infopto2entalpia = Div(width=400, height=10)
infopto2entropia = Div(width=400, height=10)
infopto2presion =  Div( width=400, height=10)
infopto2temperatura = Div( width=400, height=10)

# Punto 3
infopto3temperatura = Div(width=400, height=10)
infopto3presion = Div(width=400, height=10)
infopto3entalpia = Div(width=400, height=10)
infopto3entropia = Div(width=400, height=10)

# Punto 4
infopto4temperatura = Div( width=400, height=10)
infopto4presion = Div( width=400, height=10)
infopto4entalpia = Div( width=400, height=10)
infopto4entropia = Div( width=400, height=10)

#Eficiencia
infobomba=Div( width=400, height=10)
infoturbina= Div( width=400, height=10)
eficiencia= Div(width=400, height=10)
Qentrada= Div( width=400, height=10)
Qsalida= Div( width=400, height=10)


# Estilo para los titulos
estilos_css = """
<style>
body {
    font-family: monospace; 
    background-color: #f4f4f4; 
    color: #333; 
}

h2 {
    color: #428bca; 
}

.footer {
    text-align: center;
    padding: 10px;
}

</style>
"""


# Procesos
info_proceso_1 = column(
    Div(text=estilos_css + "<h2>PROCESO 1</h2>", width=400, height=40),
    infopto1temperatura,
    infopto1presion,
    infopto1entalpia,
    infopto1entropia
)

info_proceso_2 = column(
    Div(text=estilos_css + "<h2>PROCESO 2</h2>", width=400, height=40),
    infopto2temperatura,
    infopto2presion,
    infopto2entalpia,
    infopto2entropia
)

info_proceso_3 = column(
    Div(text=estilos_css + "<h2>PROCESO 3</h2>", width=400, height=40),
    infopto3temperatura,
    infopto3presion,
    infopto3entalpia,
    infopto3entropia
)

info_proceso_4 = column(
    Div(text=estilos_css + "<h2>PROCESO 4</h2>", width=400, height=40),
    infopto4temperatura,
    infopto4presion,
    infopto4entalpia,
    infopto4entropia
)

info_datos=column(
    Div(text=estilos_css + "<h2>Datos Finales </h2>", width=400, height=40),
    infobomba,
    infoturbina,
    eficiencia,
    Qentrada,
    Qsalida,
)

nombres = Div(text = estilos_css +
             """
             <footer class="footer">
             <h3>Ciclo de rankine por Fabián Espinoza, Miguel Quintero, Miguel Quiroz, Nicolás Sanchez y Javier Vidal.</h3>
             <p>© 2023. Todos los derechos resevados.</p>
             </footer>
             """,
)

info_procesos = column(
    info_proceso_1,
    info_proceso_2,
    info_proceso_3,
    info_proceso_4,
    info_datos
)

# Organizar los widgets
inputs = column(
    titulo,
    temperatura_H,
    temperatura_L,
    compresion_bomba,
)

# Gráfica de la curva de entropía

# Se generan los datos de temperatura para el rango de los datos
T = np.linspace(274,647,400)
# Se extraen de la tabla los datos de entropía en base a la temperatura
svap = [s for s in [steamTable.sL_t(t) for t in T]]
sliq = [s for s in [steamTable.sV_t(t) for t in T]]

plot.line(
    x = svap,
    y = T,
    line_color = (0,0,255)
)

plot.line(
    x = sliq,
    y = T,
    line_color = (255,0,0)
)

# Información de los procesos
layout = column(
    row(
        inputs,
        plot,
        column(
            row(column(info_proceso_1), column(info_proceso_2)),
            row(column(info_proceso_3), column(info_proceso_4)),
            info_datos,
        ),
        # width=100
    ),
    nombres
)

curdoc().add_root(layout)
curdoc().title = "Ciclo de Rankine"
Calcular(temperatura_L,temperatura_H,compresion_bomba)