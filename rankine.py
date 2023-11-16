import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from pyXSteam.XSteam import XSteam
from bokeh.models import Div 


# Crear la fuente de datos
'''
Las unidades de medida que utiliza el XSteam con el systema "BARE" son las siguiente:
- metros [m]
- kilogramos [kg]
- segundo [sec]
- Kelvin [K]
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

def Calcular(TL,TH, Fm, RC):
    # Definir valores iniciales
    '''
    Las temperaturas por la librería de pyXSteam las está 
    calculando actualmente en Kelvin pero los sliders toman
    la temperatura en Celcius.
    '''
    Fm = Fm.value
    TH = TH.value + 273.15
    TL = TL.value + 273.15
    
    # PUNTO 1 - Salida del condensador, antes de la bomba
    Temp1 = TL
    Pres1 = steamTable.psat_t(Temp1) * 1000
    h1 = steamTable.hL_t(Temp1)
    s1 = steamTable.sL_t(Temp1)
    VolEsp = steamTable.v_ph(Pres1,h1)
    
    PUNTO1 = f'''
    ====  PUNTO 1  ====
    Temperatura 1:
    {Temp1}
    Presión 1:
    {Pres1}
    Entalpía 1:
    {h1}
    Entropía 1:
    {s1}
    
    Volumen Específico:
    {VolEsp}
    '''
    
    print(PUNTO1)

    
    # PUNTO 2 - Salida de la bomba, antes de la caldea
    '''
    El ratio de compresión de la bomba se calcula como:
    R = P out/P in
    Por lo tanto para calcular la presión de salida de la bomba sería:
    P out = R * P in
    '''
    s2 = s1
    Pres2 = RC.value * Pres1
    Temp2 = steamTable.t_ps(Pres2, s2)

    # Trabajo de entrada [Win] - BOMBA
    h2 = steamTable.h_ps(Pres2,s2)
    
    '''
    BOMBA
    '''
    # Win = VolEsp * (Pres2 - Pres1)
    Win = Fm * (h2 - h1)
    
    
    PUNTO2 = f'''
        ====  PUNTO 2  ====
        Temperatura 2:
        {Temp2}
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
    h3 = steamTable.hV_t(Temp3)
    s3 = steamTable.sV_t(Temp3)
    
    PUNTO3 = f'''
        ====  PUNTO 3  ====
        Temperatura 3:
        {Temp3}
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
    # X4 = steamTable.x_ps(Pres4, s4)
    h4 = steamTable.hV_p(Pres4)
    
    #trabajo de la turbina
    W_tur = (h3 - h4) * Fm

    PUNTO4 = f'''
        ====  PUNTO 4  ====
        Temperatura 4:
        {Temp4}
        Presión 4:
        {Pres4}
        Entalpía 4:
        {h4}
        Entropía 4:
        {s4}
        '''
        
    print(PUNTO4)
    
    Qin = (h3 - h2)
    Qout = (h1 - h4)
    
    Wn = Qin - Qout
    
    # n = (W_tur-Win)/Qin*100
    n = (W_tur - Win)/ (Qin * Fm)

    STATS = f''''
        El trabajo requerido por la bomba es de {round(Win,4)} [kJ/kg]
        El trabajo que produce la turbina es de {round(W_tur,4)} [kJ/kg]
        
        Q entrada {Qin}
        Q salida {Qout}
        
        La eficiencia del sistema es de un {round(n,2)} %
    '''
    print(STATS)
    
    Mostrar_resultados(Pres1,Pres2,Pres3,Pres4,Temp1,Temp2,Temp3,Temp4,h1,h2,h3,h4,s1,s2,s3,s4,Qin,Qout,n)
    
def Mostrar_resultados(P1, P2, P3, P4, T1, T2, T3, T4, H1, H2, H3, H4, S1, S2, S3, S4,Qin, Qout, n):
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
    infopto4presion.text = f"Q entrada: {Qin}"#Presion
    infopto4entalpia.text = f"Q salida: {Qout}"#entalpia
    infopto4entropia.text = f"Eficiencia: {n}"#entropia


plot = figure(
    height=500,
    width=500,
    title="Ciclo Rankine",
    tools="crosshair, pan, reset, save, wheel_zoom",
    x_range=(0, 100),
    y_range=(0, 100)
)

plot.line(
    'x',
    'y',
    source=source,
    line_width=3,
    line_alpha=0.6
)


temperatura_H = Slider(
    title="Temperatura de salida Caldera (C)",
    value=200,
    start=110,
    end=300,
    step=10
)

temperatura_L = Slider(
    title="Temperatura de salida Condensador (C)",
    value=30,
    start=5,
    end=60,
    step=5
)

flujo_masico = Slider(
    title="Flujo másico (kg/s)",
    value=100,
    start=100,
    end=1000,
    step=20
)

ratio_compresion = Slider(
    title="Ratio de Compresión para la Bomba",
    value=2.0,
    start=1.1,
    end=5.0,
    step=0.1
)

# Asociar la función de actualización al evento 'value_changed'
temperatura_L.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,flujo_masico,ratio_compresion))
temperatura_H.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,flujo_masico,ratio_compresion))
flujo_masico.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,flujo_masico,ratio_compresion))
flujo_masico.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,flujo_masico,ratio_compresion))
ratio_compresion.on_change('value', lambda attr, old, new: Calcular(temperatura_L,temperatura_H,flujo_masico,ratio_compresion))


# Cajas de texto

# Punto 1

infopto1temperatura = Div(text="a", width=400, height=50)
infopto1presion = Div(text="a", width=400, height=50)
infopto1entalpia = Div(text="a", width=400, height=50)
infopto1entropia = Div(text="a", width=400, height=50)

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

# Información



# Organizar los widgets
inputs = column(
    temperatura_H,
    temperatura_L,
    flujo_masico,
    ratio_compresion,
#    infopto1temperatura,
#     infopto1presion,
#     infopto1entalpia,
#     infopto1entropia,
#     infopto2temperatura,
#     infopto2presion,
#     infopto2entalpia,
#     infopto2entropia,
#     infopto3temperatura,
#     infopto3presion,
#     infopto3entalpia,
#     infopto3entropia,
#     infopto4temperatura,
    infopto4presion,
    infopto4entalpia,
    infopto4entropia
    )

# Agregar al documento
curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Ciclo de Rankine"
#aqui estoy, hola amigos UwU