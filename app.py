import streamlit as st
import re
from spellchecker import SpellChecker

# Configuración de la página
st.set_page_config(page_title="Standards QA Auditor", page_icon="🔍", layout="wide")

st.title("🔍 Auditor de Estructura de Estándares")
st.write("Pega el texto codificado en Sublime Text para verificar errores de formato antes de subirlo.")

# Entrada de texto
texto_input = st.text_area("Pega tus estándares aquí:", height=300)

if st.button("Auditar Estándares", type="primary"):
    if not texto_input.strip():
        st.warning("Por favor, pega algún texto para analizar.")
    else:
        # Inicializar corrector para palabras pegadas
        spell = SpellChecker()
        
        # Separar el texto por líneas
        lineas = texto_input.split('\n')
        
        errores_encontrados = False
        reporte_simbolos = []
        reporte_hard_returns = []
        reporte_espacios = []
        reporte_palabras_pegadas = []

        # Lista estricta de símbolos válidos basados en tu tabla de Sublime
        simbolos_validos = [
            r'^\{\{', r'^%%', r'^\?\?', r'^\$\$', r'^<<', r'^##', 
            r'^!!', r'^\[\[', r'^@@', r'^&&', r'^<br/>', r'^\*\*'
        ]

        # Función de validación estricta de inicio
        def tiene_simbolo_valido(texto):
            texto_limpio = texto.strip()
            if not texto_limpio:
                return True
            for patron in simbolos_validos:
                if re.match(patron, texto_limpio):
                    return True
            return False

        for i, linea in enumerate(lineas):
            num_linea = i + 1
            linea_strip = linea.strip()
            
            if not linea_strip:
                continue
            
            # 1. VALIDACIÓN ESTRICTA DE SÍMOLO INICIAL
            if not tiene_simbolo_valido(linea_strip):
                # Si no tiene símbolo válido, determinamos si es una línea cortada (Hard Return)
                if i > 0 and lineas[i-1].strip() and (linea_strip[0].islower() or not tiene_simbolo_valido(lineas[i-1])):
                    reporte_hard_returns.append({
                        "linea": num_linea,
                        "texto": linea_strip
                    })
                else:
                    reporte_simbolos.append({
                        "linea": num_linea,
                        "texto": linea_strip
                    })

            # 2. VALIDACIÓN DE ESPACIOS
            if "  " in linea or linea.endswith(" ") or linea.startswith(" "):
                detalles = []
                if "  " in linea: detalles.append("espacios dobles")
                if linea.startswith(" ") or linea.endswith(" "): detalles.append("espacios huérfanos al inicio/final")
                
                reporte_espacios.append({
                    "linea": num_linea,
                    "texto": linea,
                    "detalle": " y ".join(detalles)
                })

            # 3. VALIDACIÓN DE PALABRAS PEGADAS
            palabras = re.findall(r'[a-zA-Z]+', linea_strip)
            for palabra in palabras:
                if len(palabra) > 12 and spell.unknown([palabra]):
                    reporte_palabras_pegadas.append({
                        "linea": num_linea,
                        "palabra": palabra,
                        "texto": linea_strip
                    })

        # MOSTRAR RESULTADOS EN LA INTERFAZ
        st.subheader("📋 Reporte de Auditoría")
        
        # --- CATEGORÍA 1: SÍMBOLOS FALTANTES O INCORRECTOS ---
        if reporte_simbolos:
            errores_encontrados = True
            with st.expander("🔴 Estándares sin Símbolo Autorizado (¡Alerta Crítica!)", expanded=True):
                st.markdown("### El texto real de tus líneas con error:")
                for item in reporte_simbolos:
                    # Usamos st.error para que resalte visualmente en rojo la línea completa de tu trabajo
                    st.error(f"**Línea {item['linea']}:** `{item['texto']}`")

        # --- CATEGORÍA 2: HARD RETURNS ---
        if reporte_hard_returns:
            errores_encontrados = True
            with st.expander("⚠️ Líneas Cortadas / Saltos de línea huérfanos (Hard Returns)", expanded=True):
                st.markdown("### El texto real de tus líneas cortadas:")
                for item in reporte_hard_returns:
                    st.warning(f"**Línea {item['linea']}:** `{item['texto']}`")

        # --- CATEGORÍA 3: ERRORES DE ESPACIADO ---
        if reporte_espacios:
            errores_encontrados = True
            with st.expander("🔵 Errores de Espaciado (Dobles o Huérfanos)", expanded=True):
                st.markdown("### Líneas con problemas de espacios:")
                for item in reporte_espacios:
                    # Reemplazamos espacios dobles visualmente para que sepas dónde están
                    texto_visible = item['texto'].replace("  ", " [ESPACIO_DOBLE] ")
                    st.info(f"**Línea {item['linea']}:** `{texto_visible}` *({item['detalle']})*")

        # --- CATEGORÍA 4: PALABRAS PEGADAS ---
        if reporte_palabras_pegadas:
            errores_encontrados = True
            with st.expander("🟡 Posibles Palabras Pegadas", expanded=True):
                st.markdown("### Palabras sospechosas encontradas:")
                for item in reporte_palabras_pegadas:
                    st.write(f"❌ **Línea {item['linea']}:** Se detectó '**{item['palabra']}**' en el texto: *\"{item['texto']}\"*")

        if not errores_encontrados:
            st.success("🎉 ¡Auditoría limpia! Toda la estructura coincide perfectamente con tus símbolos obligatorios de Sublime.")
