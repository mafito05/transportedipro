import streamlit as st
import pandas as pd

# Función para limpiar y procesar el archivo de despacho
def entrada(ruta):
    plan = pd.read_excel(ruta)
    plan = plan.iloc[7:]
    plan.reset_index(drop=True, inplace=True)
    plan.columns = plan.iloc[0]
    plan = plan.drop(plan.index[0])
    plan = plan.iloc[:-6]
    plan = plan.dropna(subset=["ID PRODUCTO"])
    plan['CANT.MAST'] = plan['CANT.MAST'].astype(int)
    plan['PESO'] = plan['PESO'].astype(float)
    plan['ID PRODUCTO'] = pd.to_numeric(plan['ID PRODUCTO'], errors='coerce')
    return plan

# Cargar archivos precargados
productos = pd.read_excel("C:/Users/mafit/PRACTICAS_PYTHON/app/producto_limpio.xlsx")
macro = pd.read_excel("C:/Users/mafit/PRACTICAS_PYTHON/app/MAYORISTA.xlsx")
tarifa = pd.read_excel("C:/Users/mafit/PRACTICAS_PYTHON/app/tarifas.xlsx")

# Configurar la interfaz de Streamlit
st.title('Calculadora de Plan de Reparto')

# Cargar archivo de Despacho
despacho_file = st.file_uploader("Adjuntar archivo de Despacho", type="xlsx")

if despacho_file:
    despacho = entrada(despacho_file)  # Procesar el archivo de despacho

    # Inputs adicionales
    id_camion = st.number_input("ID del Transporte", min_value=0, step=1)
    gasolina = st.number_input("Costo de Gasolina", min_value=0.0, step=0.1)
    peaje = st.number_input("Costo de Peaje", min_value=0.0, step=0.1)
    alimentos = st.number_input("Costo de Comida Personal", min_value=0.0, step=0.1)
    otros = gasolina + alimentos + peaje +156.3

    if st.button("Calcular Ganancia o Pérdida"):
        # Procesamiento de datos
        productos_macro = pd.merge(productos, macro, left_on='Referencia Interna', 
                                   right_on='Reglas de lista de precios/Producto/Referencia Interna')

        productos_macro['Beneficio Bruto'] = (productos_macro['Reglas de lista de precios/Precio Fijo'] - 
                                              (productos_macro['Proveedores/Precio'] / productos_macro['Productos/UoM de compra/Mayor ratio']))

        despacho = despacho.rename(columns={'ID PRODUCTO': 'Referencia Interna'})
        despacho_beneficio = pd.merge(despacho, productos_macro, on='Referencia Interna')

        despacho_beneficio['Beneficio Total'] = despacho_beneficio['CANT.VTA'] * despacho_beneficio['Beneficio Bruto']
        beneficio_bruto_total = despacho_beneficio['Beneficio Total'].sum()

        costo_transporte = tarifa[tarifa['ID'] == id_camion]['Monto'].sum()

        ganancia_perdida_total = ((beneficio_bruto_total - costo_transporte) - (beneficio_bruto_total - costo_transporte) * 0.015) - otros

        st.write(f"Ganancia o Pérdida Total del Camión con ID {id_camion}: S/{ganancia_perdida_total}")
