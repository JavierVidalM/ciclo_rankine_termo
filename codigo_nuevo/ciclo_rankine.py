from tkinter import *
import sys
from pyXSteam.XSteam import XSteam
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.layouts import column

bgc = 'slate gray'

#se crea una variable con los datos de las tablas termodinamicas
steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)



########################Funciones necesarias##############################
def calcular():
    global ef
    global temperatura1,temperatura2,temperatura3,temperatura4
    global presion1,presion2,presion3,presion4
    global entropia1,entropia2,entropia3,entropia4
    global entalpia1,entalpia2,entalpia3,entalpia4

    #convertir flujo kg/h a kg/s
    flujo_hora = float(esc_fjo.get())
    
    flujo_segundo = round((flujo_hora/3600),5)


    #proceso 1
    presion1 = 0.01 #bar
    entropia1 = steamTable.sL_p(presion1)
    temperatura1 = steamTable.t_ps(presion1, entropia1)
    entalpia1 = steamTable.hL_p(presion1)

    volumen = 1/steamTable.rhoL_p(presion1)
    #proceso 2
    presion2 = 200 #bar

    w_p = volumen*(presion2-presion1)

    
    entropia2 = entropia1
    entalpia2 = entalpia1+w_p
    temperatura2 = steamTable.t_ps(presion2, entropia2)

    #proceso 3

    presion3 = presion2
    entalpia3 = steamTable.hV_p(presion2)
    entropia3 = steamTable.sV_p(presion2)

    #calculo 
    h2dash = steamTable.hL_p(presion2)
    s2dash = steamTable.sL_p(presion2)
    T2dash = steamTable.t_ph(presion2, h2dash)

    temperatura3 = T2dash

    #proceso 4
    entropia4 = entropia3
    presion4 = presion1
    temperatura4 = steamTable.t_ps(presion4, entropia4)
    x4 = steamTable.x_ps(presion4, entropia4)
    entalpia4 = steamTable.h_px(presion4, x4)

    Q_en = (entalpia3-entalpia2)
    #calculo calor expulsado por el condensador
    Q_sal = (entalpia4-entalpia1)

    #calculo del trabajo generado por la turbina
    W_tur = flujo_segundo*(entalpia3-entalpia4)
    #calculo del trabajo usado por la bomba
    W_bom =flujo_segundo*w_p
    ef = ((W_tur-W_bom)/Q_en)*100

    #convertir los valores a string
    Q_entrada = str(round((Q_en),5))
    Q_salida = str(round((Q_sal),5))
    W_bomba = str(round((W_bom),5))
    W_turbina = str(round((W_tur),5))
    EF = str(round((ef),3))

    #Limpiar cajas de texto
    c1.delete(0,END)
    c2.delete(0,END)
    c3.delete(0,END)
    c4.delete(0,END)
    c5.delete(0,END)
    c6.delete(0,END)
    c7.delete(0,END)
    c8.delete(0,END)
    c9.delete(0,END)
    c10.delete(0,END)
    c11.delete(0,END)
    c12.delete(0,END)
    c13.delete(0,END)
    c14.delete(0,END)
    c15.delete(0,END)
    c16.delete(0,END)
    c17.delete(0,END)
    Caldera.delete(0,END)
    Bomba.delete(0,END)
    Turbina.delete(0,END)
    Condensador.delete(0,END)


    #Insertar valores en cajas
    c1.insert(0,flujo_segundo)
    c2.insert(0,(str(round((presion1),3))+' [bar]'))
    c3.insert(0,(str(round((temperatura1),3))+' [°C]'))
    c4.insert(0,(str(round((entalpia1),3))+' [kJ/kg]'))
    c5.insert(0,(str(round((entropia1),3))+' [kJ/kg °K]'))
    c6.insert(0,(str(round((presion2),3))+' [bar]'))
    c7.insert(0,(str(round((temperatura2),3))+' [°C]'))
    c8.insert(0,(str(round((entalpia2),3))+' [kJ/kg]'))
    c9.insert(0,(str(round((entropia2),3))+' [kJ/kg °K]'))
    c10.insert(0,(str(round((presion4),3))+' [bar]'))
    c11.insert(0,(str(round((temperatura4),3))+' [°C]'))
    c12.insert(0,(str(round((entalpia4),3))+' [kJ/kg]'))
    c13.insert(0,(str(round((entropia4),3))+' [kJ/kg °K]'))
    c14.insert(0,(str(round((presion3),3))+' [bar]'))
    c15.insert(0,(str(round((temperatura3),3))+' [°C]'))
    c16.insert(0,(str(round((entalpia3),3))+' [kJ/kg]'))
    c17.insert(0,(str(round((entropia3),3))+' [kJ/kg °K]'))
    Caldera.insert(0,Q_entrada+' [kJ/kg °C]')
    Bomba.insert(0,W_bomba+' [W]')
    Turbina.insert(0,W_turbina+' [W]')
    Condensador.insert(0,Q_salida+' [kJ/Kg °C]]')
    Eficiencia.config(text=f'Eficiencia (n): {EF} %')
    

def bokeh_plot():
    plot = figure(title="Diagram T-s Ciclo de Rankine Ideal", x_axis_label="Entropía (s)", y_axis_label="Temperatura (°C)")
    plot.line([entropia1, entropia2, entropia3, entropia4, entropia1], [temperatura1, temperatura2, temperatura3, temperatura4, temperatura1], line_color="blue", line_width=2)
    
    source = ColumnDataSource(data=dict(x=[entropia1, entropia2, entropia3, entropia4, entropia1], y=[temperatura1, temperatura2, temperatura3, temperatura4, temperatura1]))
    labels = [f'(1)\nT = {round(float(temperatura1), 2)} C\nP = {round(float(presion1), 1)} bar\nh = {round(float(entalpia1), 1)} kJ/kg\ns = {round(float(entropia1), 3)} kJ/kgK',
              f'(2)\nT = {round(float(temperatura2), 2)} C\nP = {round(float(presion2), 1)} bar\nh = {round(float(entalpia2), 1)} kJ/kg\ns = {round(float(entropia2), 3)} kJ/kgK',
              f"(3)\nT = {round(float(temperatura2), 2)} C\nP = {round(float(presion2), 1)} bar\nh = {round(float(entalpia3), 1)} kJ/kg\ns = {round(float(entropia3), 3)} kJ/kgK",
              f'(4)\nT = {round(float(temperatura4), 2)} C\nP = {round(float(presion2), 1)} bar\nh = {round(float(entalpia4), 1)} kJ/kg\ns = {round(float(entalpia4), 3)} kJ/kgK']
    
    plot.text(x=[entropia1, entropia2, entropia3, entropia4], y=[temperatura1, temperatura2, temperatura3, temperatura4], text=labels, text_font_size="10pt", text_align="left", text_baseline="middle")
    
    show(column(plot))

def salir():
    sys.exit()
########################Creación de la ventana############################
main=Tk()
main.title("Ciclo de Rankine")
main.geometry('1200x700')
main.config(bg='slate gray')
Titulo = Label(main, text="Ciclo de Rankine",bg=bgc,fg='white',font=(('Sans Serif'),30,'bold')).place(x=10,y=10)                                        

#Diagrama del ciclo
img=PhotoImage(file='rankine.png')
rnk_img = Label(main, bg=bgc,image=img)
rnk_img.place(x=630,y=50)

cal = IntVar()
Caldera = Entry(main,textvariable=(cal,'W'))
Caldera.place(x=793,y=110)

bmb = IntVar()
Bomba = Entry(main)
Bomba.place(x=630,y=320)

trb = IntVar()
Turbina = Entry(main)
Turbina.place(x=1020,y=320)

cnd = IntVar()
Condensador = Entry(main)
Condensador.place(x=795,y=520)

Eficiencia=Label(None, text="Eficiencia (n):",bg=bgc,fg='white',font=(('Sans Serif'),12,'bold'))
Eficiencia.place(x=630,y=550)

#Rango de flujo
Flujo_Label = Label(main, text="Flujo Entrada\n(Kg/h)",bg=bgc,fg='white')
Flujo_Label.place(x=10,y=120)

esc_fjo = Scale(main,from_ = 1000, to = 3000,length=390, tickinterval=200, orient = HORIZONTAL,bd=0,bg=bgc,fg='white')  
esc_fjo.place(x=90,y=100)

#Rango temperatura
# Temp_Label = Label(main, text="Temperatura\nEntrada (°C)",bg=bgc,fg='white')
# Temp_Label.place(x=10,y=190)

# esc_temp = Scale(main,from_ = 100, to = 340,length=390, tickinterval=20, orient = HORIZONTAL,bd=0,bg=bgc,fg='white')  
# esc_temp.place(x=90,y=180)

Fjo=IntVar()
Texto1 = Label(None, text="Flujo Entrada\n(Kg/s)",bg=bgc,fg='white').place(x=500, y=85)
c1=Entry(main, textvariable=Fjo,width=10)
c1.place(x=500,y=120,height=30)

#Proceso 1
pro1 = Label(None, text="Proceso 1",bg=bgc,fg='white',font=(('Sans Serif'),10,'bold')).place(x=10, y=270)
Texto2 = Label(None, text="Presion1",bg=bgc,fg='white').place(x=10, y=310)
Texto3 = Label(None, text="Temperatura 1",bg=bgc,fg='white').place(x=10, y=340)
Texto4 = Label(None, text="Entalpía 1",bg=bgc,fg='white').place(x=10, y=370)
Texto5 = Label(None, text="Entropía 1",bg=bgc,fg='white').place(x=10, y=400)

P1=IntVar()
c2=Entry(main, textvariable=P1)
c2.place(x=100,y=310)

T1=IntVar()
c3=Entry(main, textvariable=T1)
c3.place(x=100,y=340)

H1=IntVar()
c4=Entry(main, textvariable=H1)
c4.place(x=100,y=370)

S1=IntVar()
c5=Entry(main, textvariable=S1)
c5.place(x=100,y=400)

#Proceso 2
pro2 = Label(None, text="Proceso 2",bg=bgc,fg='white',font=(('Sans Serif'),10,'bold')).place(x=270, y=270)
Texto6 = Label(None, text="Presión 2",bg=bgc,fg='white').place(x=270, y=310)
Texto7 = Label(None, text="Temperatura 2",bg=bgc,fg='white').place(x=270, y=340)
Texto8 = Label(None, text="Entalpía 2",bg=bgc,fg='white').place(x=270, y=370)
Texto9 = Label(None, text="Entropía 2",bg=bgc,fg='white').place(x=270, y=400)

P2=IntVar()
c6=Entry(main, textvariable=P2)
c6.place(x=360,y=310)

T2=IntVar()
c7=Entry(main, textvariable=T2)
c7.place(x=360,y=340)

H2=IntVar()
c8=Entry(main, textvariable=H2)
c8.place(x=360,y=370)

S2=IntVar()
c9=Entry(main, textvariable=S2)
c9.place(x=360,y=400)

#Proceso 4

pro4 = Label(None, text="Proceso 3",bg=bgc,fg='white',font=(('Sans Serif'),10,'bold')).place(x=270, y=450)
Texto14 = Label(None, text="Presión 3",bg=bgc,fg='white').place(x=270, y=500)
Texto15 = Label(None, text="Temperatura 3",bg=bgc,fg='white').place(x=270, y=530)
Texto16 = Label(None, text="Entalpía 3",bg=bgc,fg='white').place(x=270, y=560)
Texto17 = Label(None, text="Entropía 3",bg=bgc,fg='white').place(x=270, y=590)

P3=IntVar()
c10=Entry(main, textvariable=P3)
c10.place(x=100,y=500)

T3=IntVar()
c11=Entry(main, textvariable=T3)
c11.place(x=100,y=530)

H3=IntVar()
c12=Entry(main, textvariable=H3)
c12.place(x=100,y=560)

S3=IntVar()
c13=Entry(main, textvariable=S3)
c13.place(x=100,y=590)

#Proceso 3

pro3 = Label(None, text="Proceso 4",bg=bgc,fg='white',font=(('Sans Serif'),10,'bold')).place(x=10, y=450)
Texto10 = Label(None, text="Presión 4",bg=bgc,fg='white').place(x=10, y=500)
Texto11 = Label(None, text="Temperatura 4",bg=bgc,fg='white').place(x=10, y=530)
Texto12 = Label(None, text="Entalpía 4",bg=bgc,fg='white').place(x=10, y=560)
Texto13 = Label(None, text="Entropía 4",bg=bgc,fg='white').place(x=10, y=590)

P4=IntVar()
c14=Entry(main, textvariable=P4)
c14.place(x=360,y=500)

T4=IntVar()
c15=Entry(main, textvariable=T4)
c15.place(x=360,y=530)

H4=IntVar()
c16=Entry(main, textvariable=H4)
c16.place(x=360,y=560)

S4=IntVar()
c17=Entry(main, textvariable=S4)
c17.place(x=360,y=590)

#Botones
Calculo = Button(main,text="Calcular",width=10,height=3,bd=0,bg='green3',fg='white',font=(('Arial Black'),10,'bold'),command=calcular)
Calculo.place(x=80,y=630)

BokehButton = Button(main, text="Gráfico Bokeh", width=15, height=3, bd=0, bg='dodger blue', fg='white', font=(('Arial Black'), 10, 'bold'), command=bokeh_plot)
BokehButton.place(x=380, y=630)

Salir = Button(main,text="Cerrar",width=10,height=3,bd=0,bg='red2',fg='white',font=(('Arial Black'),10,'bold'),command = salir)
Salir.place(x=280,y=630)


main.mainloop()
