import streamlit as st
import re
from spellchecker import SpellChecker

# Configuración de la página
st.set_page_config(page_title="Standards QA Auditor", page_icon="🔍", layout="wide")

st.title("🔍 Auditor de Estructura de Estándares")
st.write("Pega el texto codificado en Sublime Text para verificar errores de formato antes de subirlo.")

# Usamos un formulario para agrupar la entrada y el botón de borrado de forma eficiente
with st.form("auditor_form", clear_on_submit=False):
    # Entrada de texto con una clave única
    texto_input = st.text_area(
        "Pega tus estándares aquí:", 
        key="texto_estandares_key",
        height=300
    )
    
    # Botones dentro del formulario
    col1, col2, _ = st.columns([2, 2, 6])
    with col1:
        bot_auditar = st.form_submit_button("Auditar Estándares", type="primary")
    with col2:
        # Este botón especial limpia automáticamente TODO el formulario de golpe
        bot_limpiar = st.form_submit_button("Borrar todo 🗑️")

# Si el usuario hace clic en borrar, forzamos el refresco instantáneo de la página para limpiar todo
if bot_limpiar:
    st.session_state["texto_estandares_key"] = ""
    st.rerun()

# 4. EJECUCIÓN DE LA AUDITORÍA (Solo si se presionó Auditar y hay texto)
if bot_auditar:
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
            
            # Validación estricta de símbolo inicial
            if not tiene_simbolo_valido(linea_strip):
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

            # Validación de espacios
            if "  " in linea or linea.endswith(" ") or linea.startswith(" "):
                detalles = []
                if "  " in linea: detalles.append("espacios dobles")
                if linea.startswith(" ") or linea.endswith(" "): detalles.append("espacios huérfanos al inicio/final")
                
                reporte_espacios.append({
                    "linea": num_linea,
                    "texto": linea,
                    "detalle": " y ".join(detalles)
                })

            # Validación de palabras pegadas
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
