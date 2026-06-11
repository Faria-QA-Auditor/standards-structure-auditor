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
            
            # Revisa si cumple estrictamente con alguno de los patrones de la lista
            for patron in simbolos_validos:
                if re.match(patron, texto_limpio):
                    return True
            return False

        for i, linea in enumerate(lineas):
            num_linea = i + 1
            linea_strip = linea.strip()
            
            if not linea_strip:
                continue
            
            # 1. VALIDACIÓN ESTRICTA DE SÍMBOLO INICIAL
            if not tiene_simbolo_valido(linea_strip):
                # Si no tiene símbolo válido, determinamos si es una línea cortada (Hard Return)
                # o un error directo de símbolo ausente/incorrecto al inicio del bloque.
                if i > 0 and lineas[i-1].strip() and (linea_strip[0].islower() or not tiene_simbolo_valido(lineas[i-1])):
                    reporte_hard_returns.append(
                        f"📍 **Línea {num_linea}:** '{linea_strip[:50]}...'"
                    )
                else:
                    reporte_simbolos.append(
                        f"📍 **Línea {num_linea}:** Inicia de forma incorrecta con '{linea_strip[:30]}...'"
                    )

            # 2. VALIDACIÓN DE ESPACIOS
            if "  " in linea:
                reporte_espacios.append(f"📍 **Línea {num_linea}:** Contiene espacios dobles seguidos.")
            if linea.endswith(" ") or linea.startswith(" "):
                reporte_espacios.append(f"📍 **Línea {num_linea}:** Contiene espacios invisibles/sueltos al inicio o al final.")

            # 3. VALIDACIÓN DE PALABRAS PEGADAS
            palabras = re.findall(r'[a-zA-Z]+', linea_strip)
            for palabra in palabras:
                if len(palabra) > 12 and spell.unknown([palabra]):
                    reporte_palabras_pegadas.append(f"📍 **Línea {num_linea}:** Detectada la palabra '**{palabra}**'")

        # MOSTRAR RESULTADOS EN LA INTERFAZ
        st.subheader("📋 Reporte de Auditoría")
        
        # --- CATEGORÍA 1: SÍMBOLOS FALTANTES O INCORRECTOS (ESTRICTO) ---
        if reporte_simbolos:
            errores_encontrados = True
            with st.expander("🔴 Estándares sin Símbolo Autorizado (¡Alerta Crítica!)", expanded=True):
                st.info("""
                💡 **¿Por qué se marca?** La línea comenzó con letras, números, paréntesis sueltos `()` o un carácter no autorizado. **OBLIGATORIAMENTE** debe empezar con uno de tus 12 símbolos de Sublime.
                * ❌ **Ejemplo de Error:** `(a) Understand and apply properties...` *(Falta el símbolo antes del paréntesis)*
                * ❌ **Ejemplo de Error:** `Grade 4 standard content...` *(Texto plano sin codificar)*
                * ✔️ **Cómo debería verse:** `## (a) Understand and apply properties...` o `%%Grade 4 standard content...`
                """)
                st.markdown("---")
                for err in reporte_simbolos:
                    st.error(err)

        # --- CATEGORÍA 2: HARD RETURNS ---
        if reporte_hard_returns:
            errores_encontrados = True
            with st.expander("⚠️ Líneas Cortadas / Saltos de línea huérfanos (Hard Returns)", expanded=True):
                st.info("""
                💡 **¿Por qué se marca?** Esta línea no tiene un símbolo válido y parece ser la continuación que se quebró de la frase anterior en Sublime Text.
                * ❌ **Ejemplo de Error:** `## Analyze informational text`
                    `and its main structural elements.` *(Línea cortada)*
                * ✔️ **Cómo debería verse:** `## Analyze informational text and its main structural elements.`
                """)
                st.markdown("---")
                for err in reporte_hard_returns:
                    st.warning(err)

        # --- CATEGORÍA 3: ERRORES DE ESPACIADO ---
        if reporte_espacios:
            errores_encontrados = True
            with st.expander("🔵 Errores de Espaciado (Dobles o Huérfanos)", expanded=True):
                st.info("""
                💡 **¿Por qué se marca?** Se detectaron espacios dobles (`  `) dentro del texto, o espacios fantasma al inicio o al final de la línea.
                * ❌ **Ejemplo de Error:** `$$  Identify theme` o `%% Describe character `
                * ✔️ **Cómo debería verse:** `$$ Identify theme` o `%% Describe character`
                """)
                st.markdown("---")
                for err in reporte_espacios:
                    st.info(err)

        # --- CATEGORÍA 4: PALABRAS PEGADAS ---
        if reporte_palabras_pegadas:
            errores_encontrados = True
            with st.expander("🟡 Posibles Palabras Pegadas", expanded=True):
                st.info("""
                💡 **¿Por qué se marca?** Una palabra larga no coincide con el diccionario. Verifica si se pegaron caracteres por error.
                * ❌ **Ejemplo de Error:** `!! Use ageappropriate learning models.`
                * ✔️ **Cómo debería verse:** `!! Use age-appropriate learning models.`
                """)
                st.markdown("---")
                for err in reporte_palabras_pegadas:
                    st.write(err)

        if not errores_encontrados:
            st.success("🎉 ¡Auditoría limpia! Toda la estructura coincide perfectamente con tus símbolos obligatorios de Sublime.")
