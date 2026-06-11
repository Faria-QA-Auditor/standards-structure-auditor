import streamlit as st
import re
from spellchecker import SpellChecker

# Configuración de la página
st.set_page_config(page_title="Standards QA Auditor", page_icon="🔍", layout="wide")

st.title("🔍 Auditor de Estructura de Estándares")
st.write("Pega el texto editado en Sublime Text para verificar errores de formato antes de subirlo.")

# Entrada de texto
texto_input = st.text_area("Pega tus estándares aquí:", height=300)

if st.button("Auditar Estándares", type="primary"):
    if not texto_input.strip():
        st.warning("Por favor, pega algún texto para analizar.")
    else:
        # Inicializar corrector para palabras pegadas (en inglés por defecto)
        spell = SpellChecker()
        
        # Separar el texto por líneas
        lineas = texto_input.split('\n')
        
        errores_encontrados = False
        reporte_hard_returns = []
        reporte_simbolos = []
        reporte_espacios = []
        reporte_palabras_pegadas = []

        for i, linea in enumerate(lineas):
            num_linea = i + 1
            linea_strip = linea.strip()
            
            # Saltar líneas vacías
            if not linea_strip:
                continue
            
            # 1. VALIDACIÓN DE SÍMBOLO / CÓDIGO INICIAL
            # Ejemplo: Busca si NO empieza con letras seguidas de punto y número (ej: MATH.1, EN.2)
            # O si no empieza con un patrón común. Ajusta el Regex según tus estándares reales.
            if not re.match(r'^[A-Za-z0-9]+[\.\-]', linea_strip):
                # Si no empieza con un código/símbolo, podría ser un estándar sin símbolo
                # O podría ser una línea cortada (Hard Return) de la línea anterior
                if i > 0 and lineas[i-1].strip() and not lineas[i-1].strip().endswith('.'):
                    reporte_hard_returns.append(f"Línea {num_linea}: Posible línea cortada (Hard Return). Viene de la línea anterior.")
                else:
                    reporte_simbolos.append(f"Línea {num_linea}: No se detecta un código o símbolo de estándar al inicio: '{linea_strip[:20]}...'")

            # 2. VALIDACIÓN DE ESPACIOS
            if "  " in linea:
                reporte_espacios.append(f"Línea {num_linea}: Contiene espacios dobles seguidos.")
            if linea.endswith(" ") or linea.startswith(" "):
                reporte_espacios.append(f"Línea {num_linea}: Contiene espacios innecesarios al inicio o al final.")

            # 3. VALIDACIÓN DE PALABRAS PEGADAS
            # Limpiamos puntuación básica para analizar palabras sueltas
            palabras = re.findall(r'[a-zA-Z]+', linea_strip)
            for palabra in palabras:
                # Si la palabra es muy larga (ej. ageappropriate) y no está en el diccionario
                if len(palabra) > 12 and spell.unknown([palabra]):
                    # Intentamos ver si contiene palabras comunes pegadas de forma rudimentaria
                    reporte_palabras_pegadas.append(f"Línea {num_linea}: Posible palabra pegada: '**{palabra}**'")

        # MOSTRAR RESULTADOS
        st.subheader("📋 Reporte de Auditoría")
        
        # Hard Returns
        if reporte_hard_returns:
            errores_encontrados = True
            with st.expander("⚠️ Líneas Cortadas / Saltos de línea huérfanos (Hard Returns)", expanded=True):
                for err in reporte_hard_returns:
                    st.warning(err)
                    
        # Símbolos Faltantes
        if reporte_simbolos:
            errores_encontrados = True
            with st.expander("🔴 Estándares sin Código o Símbolo Inicial", expanded=True):
                for err in reporte_simbolos:
                    st.error(err)

        # Espacios Incorrectos
        if reporte_espacios:
            errores_encontrados = True
            with st.expander("🔵 Errores de Espaciado", expanded=True):
                for err in reporte_espacios:
                    st.info(err)

        # Palabras Pegadas
        if reporte_palabras_pegadas:
            errores_encontrados = True
            with st.expander("🟡 Posibles Palabras Pegadas", expanded=True):
                for err in reporte_palabras_pegadas:
                    st.write(err)

        if not errores_encontrados:
            st.success("🎉 ¡Auditoría limpia! No se encontraron errores obvios de estructura. Listo para codificar/subir.")
