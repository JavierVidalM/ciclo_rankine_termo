from bokeh.models import ColumnDataSource, Slider
from bokeh.layouts import column, row
from pyXSteam.XSteam import XSteam
from bokeh.plotting import figure
from bokeh.models import Div
from bokeh.io import curdoc
import numpy as np


# Crear la fuente de datos
'''
Las unidades de medida que utiliza el XSteam con el systema "BARE" son las siguiente:
- metros [m]
- kilogramos [kg]
- segundo [sec]
- Kelvin [°K]
- Mega Pascales [MPa]*
- Watts [W]

* Los valores de las presiones deben ser multiplicados por 1000 al estar en MPa, 
ya que para el programa se utilizan valores en KPa, para tenerlo en cuenta 
'''
steamTable = XSteam(XSteam.UNIT_SYSTEM_BARE)
'''
La calidad del fluido en el punto 3 se considera como 1 al considerar el ciclo
como un Ciclo de Rankine ideal, por lo mismo se establece que la calidad en el punto 1 es 0 
'''
X3 = 1
X1 = 0

source = ColumnDataSource(data=dict(x=[], y=[]))

curdoc().theme.theme = 'dark_minimal'

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
    h1 = steamTable.hL_t(Temp1)
    s1 = steamTable.sL_t(Temp1)
    
    PUNTO1 = f'''
    ====  PUNTO 1  ====
    Temperatura 1:
    {Temp1 - 273.15}
    Presión 1:
    {Pres1}
    Entalpía 1:
    {h1}
    Entropía 1:
    {s1}
    '''
    
    print(PUNTO1)

    
    # PUNTO 2 - Salida de la bomba, antes de la caldea
    s2 = s1
    Pres2 = CB.value
    Temp2 = steamTable.t_ps(Pres2, s2)

    # Trabajo de entrada [Win] - BOMBA
    h2 = steamTable.h_ps(Pres2,s2)
    
    '''
    BOMBA
    '''
    # Win = VolEsp * (Pres2 - Pres1)
    Win = -(h2 - h1)
    
    
    PUNTO2 = f'''
        ====  PUNTO 2  ====
        Temperatura 2:
        {Temp2 - 273.15}
        Presión 2:
        {Pres2}
        Entalpía 2:
        {h2}
        Entropía 2:
        {s2}
        '''
        
    print(PUNTO2)
    
    
    # PUNTO 3 - Salida de la caldera, antes de la turbina
    Pres3 = Pres2
    Temp3 = TH
    h3 = steamTable.hV_p(Pres3)
    s3 = steamTable.sV_t(Temp3)
    
    PUNTO3 = f'''
        ====  PUNTO 3  ====
        Temperatura 3:
        {Temp3 - 273.15}
        Presión 3:
        {Pres3}
        Entalpía 3:
        {h3}
        Entropía 3:
        {s3}
        '''
        
    print(PUNTO3)
    
    # PUNTO 4 - Salida de la turbina, antes del condensador --> PUNTO 1 
    s4 = s3
    Pres4 = Pres1
    Temp4 = steamTable.t_ps(Pres4,s4)
    h4 = steamTable.h_ps(Pres4,s4)
    
    #trabajo de la turbina
    W_tur = (h3 - h4)

    PUNTO4 = f'''
        ====  PUNTO 4  ====
        Temperatura 4:
        {Temp4 - 273.15}
        Presión 4:
        {Pres4}
        Entalpía 4:
        {h4}
        Entropía 4:
        {s4}
        '''
        
    print(PUNTO4)
    
    Qin = (h3 - h2)
    Qout = (h4 - h1)
    
    Wn = Qin - Qout
    
    # n = (W_tur-Win)/Qin*100
    n = ((W_tur + Win)/Qin)*100

    STATS = f'''
        El trabajo requerido por la bomba es de {round(Win,4)} [kJ/kg]
        El trabajo que produce la turbina es de {round(W_tur,4)} [kJ/kg]
        
        Q entrada {Qin}
        Q salida {Qout}
        
        La eficiencia del sistema es de un {round(n,2)} %
    '''
    print(STATS)
    
    Mostrar_resultados(Pres1,Pres2,Pres3,Pres4,Temp1,Temp2,Temp3,Temp4,h1,h2,h3,h4,s1,s2,s3,s4,Qin,Qout,n,Win,W_tur)


def Mostrar_resultados(P1, P2, P3, P4, T1, T2, T3, T4, H1, H2, H3, H4, S1, S2, S3, S4,Qin, Qout, n,Win,W_tur):
    # Actualizar valores de Punto 1
    infopto1temperatura.text = f"Temperatura: {T1}"
    infopto1presion.text = f"Presión: {P1}"
    infopto1entalpia.text = f"Entalpía: {H1}"
    infopto1entropia.text = f"Entropía: {S1}"

    # Actualizar valores de Punto 2
    infopto2temperatura.text = f"Temperatura: {T2}"
    infopto2presion.text = f"Presión: {P2}"
    infopto2entalpia.text = f"Entalpía: {H2}"
    infopto2entropia.text = f"Entropía: {S2}"

    # Actualizar valores de Punto 3
    infopto3temperatura.text = f"Temperatura: {T3}"
    infopto3presion.text = f"Presión: {P3}"
    infopto3entalpia.text = f"Entalpía: {H3}"
    infopto3entropia.text = f"Entropía: {S3}"

    # Actualizar valores de Punto 4
    infopto4temperatura.text = f"Temperatura: {T4}"
    infopto4presion.text = f"Presión: {P4}"
    infopto4entalpia.text = f"Entalpía: {H4}"
    infopto4entropia.text = f"Entropía: {S4}"
    #la otra wea q falta
    infobomba.text=f"El trabajo requerido por la bomba es de {round(Win,4)} [kJ/kg]"
    infoturbina.text=f"El trabajo que produce la turbina es de {round(W_tur,4)} [kJ/kg]"
    eficiencia.text=f"La eficiencia del sistema es de un {round(n,2)} %"
    
    Qentrada.text=f"Q entrada {Qin}"
    Qsalida.text=f"Q salida {Qout}"

    entalpia = [S1, S2, S3, S4]
    temperatura = [T1, T2, T3, T4]
    actualizar_grafico(entalpia, temperatura)


# Actualizar la función de gráficos
def actualizar_grafico(entalpia, temperatura):
    source.data = dict(x=entalpia, y=temperatura)


# Widgets
plot = figure(
    height = 500,
    width = 500,
    title = "Ciclo Rankine",
    tools = "crosshair, pan, reset, save, wheel_zoom",
    toolbar_location = 'above',
    x_axis_label = "Entropía",
    y_axis_label = "Temperatura (K)",
    x_range = (0, 10),
    y_range = (0, 600)
)

plot.line(
    'x',
    'y',
    source = source,
    line_width = 3,
    line_alpha = 0.6
)


temperatura_H = Slider(
    title = "Temperatura de salida Caldera (C)",
    value = 200,
    start = 150,
    end = 370,
    step = 10
)

temperatura_L = Slider(
    title = "Temperatura de salida Condensador (°C)",
    value = 30,
    start = 5,
    end = 80,
    step = 5
)


ratio_compresion = Slider(
    title = "Compresión de salida de la Bomba (MPa)",
    value = 5,
    start = 5.0,
    end = 20.0,
    step = 1
)

# Actualizar los valores modificando los sliders
temperatura_L.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,ratio_compresion))
temperatura_H.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,ratio_compresion))
ratio_compresion.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,ratio_compresion))


# Cajas de texto

# Punto 1

infopto1temperatura = Div(text="", width=400, height=50)
infopto1presion = Div(text="", width=400, height=50)
infopto1entalpia = Div(text="", width=400, height=50)
infopto1entropia = Div(text="", width=400, height=50)

# Punto 2

infopto2entalpia = Div(text="", width=400, height=50)
infopto2entropia = Div(text="", width=400, height=50)
infopto2presion =  Div(text="", width=400, height=50)
infopto2temperatura = Div(text="", width=400, height=50)

# Punto 3

infopto3temperatura = Div(text="", width=400, height=50)
infopto3presion = Div(text="", width=400, height=50)
infopto3entalpia = Div(text="", width=400, height=50)
infopto3entropia = Div(text="", width=400, height=50)

# Punto 4

infopto4temperatura = Div(text="", width=400, height=50)
infopto4presion = Div(text="", width=400, height=50)
infopto4entalpia = Div(text="", width=400, height=50)
infopto4entropia = Div(text="", width=400, height=50)

#las otras weas
infobomba=Div(text="", width=400, height=50)
infoturbina= Div(text="", width=400, height=50)
eficiencia= Div(text="", width=400, height=50)
Qentrada= Div(text="", width=400, height=50)
Qsalida= Div( width=400, height=50)

# Información

info_proceso_1 = column(
    Div(text="<h2>PROCESO 1</h2>", width=400, height=50),
    infopto1temperatura,
    infopto1presion,
    infopto1entalpia,
    infopto1entropia
)

info_proceso_2 = column(
    Div(text="<h2>PROCESO 2</h2>", width=400, height=50),
    infopto2temperatura,
    infopto2presion,
    infopto2entalpia,
    infopto2entropia
)

info_proceso_3 = column(
    Div(text="<h2>PROCESO 3</h2>", width=400, height=50),
    infopto3temperatura,
    infopto3presion,
    infopto3entalpia,
    infopto3entropia
)

info_proceso_4 = column(
    Div(text="<h2>PROCESO 4</h2>", width=400, height=50),
    infopto4temperatura,
    infopto4presion,
    infopto4entalpia,
    infopto4entropia
)
# Información
info_datos=column(
    Div(text="<h2>Eficiencia </h2>", width=400, height=50),
    infobomba,
    infoturbina,
    eficiencia,
    Qentrada,
    Qsalida,
)

info_procesos = column(
    info_proceso_1,
    info_proceso_2,
    info_proceso_3,
    info_proceso_4,
    info_datos
)

inputs = column(
    temperatura_H,
    temperatura_L,
    ratio_compresion,
)
# Organizar los widgets
inputs = column(
    temperatura_H,
    temperatura_L,
    ratio_compresion,
    infopto4presion,
    infopto4entalpia,
    infopto4entropia
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


# Agregar al documento
layout = row(inputs, column(plot,info_procesos), width=600)
curdoc().add_root(layout)
curdoc().title = "Ciclo de Rankine"
