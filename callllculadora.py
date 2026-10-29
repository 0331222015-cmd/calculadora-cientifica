
import ast
import math
import statistics
import operator

import numpy as np
import streamlit as st


# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Calculadora Científica",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Calculadora Científica y Estadística")
st.caption("Herramienta interactiva para cálculos matemáticos y análisis estadístico.")


# ---------------- FUNCIONES MATEMÁTICAS ----------------
FUNCIONES = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
}

CONSTANTES = {
    "pi": math.pi,
    "e": math.e,
}

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluar_nodo(nodo):
    """Evalúa únicamente operaciones matemáticas permitidas."""

    if isinstance(nodo, ast.Constant):
        if type(nodo.value) not in (int, float):
            raise ValueError("Solo se permiten números.")
        return nodo.value

    if isinstance(nodo, ast.Name):
        if nodo.id in CONSTANTES:
            return CONSTANTES[nodo.id]
        raise ValueError(f"Nombre no permitido: {nodo.id}")

    if isinstance(nodo, ast.BinOp):
        tipo = type(nodo.op)
        if tipo not in OPERADORES:
            raise ValueError("Operador no permitido.")

        izquierda = evaluar_nodo(nodo.left)
        derecha = evaluar_nodo(nodo.right)

        if tipo == ast.Pow and abs(derecha) > 1000:
            raise ValueError("El exponente es demasiado grande.")

        resultado = OPERADORES[tipo](izquierda, derecha)

        if isinstance(resultado, complex):
            raise ValueError("El resultado no es un número real.")

        if not math.isfinite(resultado):
            raise ValueError("El resultado no es finito.")

        return resultado

    if isinstance(nodo, ast.UnaryOp):
        tipo = type(nodo.op)
        if tipo not in OPERADORES:
            raise ValueError("Operador no permitido.")
        return OPERADORES[tipo](evaluar_nodo(nodo.operand))

    if isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name):
            raise ValueError("Función no permitida.")

        nombre = nodo.func.id

        if nombre not in FUNCIONES:
            raise ValueError(f"Función no permitida: {nombre}")

        if nodo.keywords:
            raise ValueError("No se permiten argumentos con nombre.")

        argumentos = [evaluar_nodo(arg) for arg in nodo.args]
        resultado = FUNCIONES[nombre](*argumentos)

        if isinstance(resultado, complex) or not math.isfinite(resultado):
            raise ValueError("El resultado no es un número real finito.")

        return resultado

    raise ValueError("Expresión matemática no permitida.")


def evaluar_expresion(expresion):
    arbol = ast.parse(expresion, mode="eval")
    return evaluar_nodo(arbol.body)


def convertir_datos(texto):
    """Acepta números separados por comas, espacios o saltos de línea."""
    texto = texto.replace(",", " ").replace(";", " ")
    datos = [float(x) for x in texto.split()]

    if not datos:
        raise ValueError("Ingresa al menos un número.")

    if not all(math.isfinite(x) for x in datos):
        raise ValueError("Todos los valores deben ser finitos.")

    return datos


# ---------------- PESTAÑAS ----------------
tab1, tab2 = st.tabs([
    "🔢 Calculadora científica",
    "📊 Estadística descriptiva"
])


# ==================================================
# CALCULADORA CIENTÍFICA
# ==================================================
with tab1:
    st.subheader("Calculadora matemática")

    st.info(
        "Usa radianes en las funciones trigonométricas. "
        "Ejemplo: sin(pi/2), sqrt(25), log(100)."
    )

    if "expresion" not in st.session_state:
        st.session_state.expresion = ""

    def agregar_texto(texto):
        st.session_state.expresion += texto

    st.text_input(
        "Expresión matemática",
        key="expresion",
        placeholder="Ejemplo: sqrt(25) + 3^2"
    )

    botones = [
        [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/"), ("√", "sqrt(")],
        [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("x²", "**2")],
        [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-"), ("π", "pi")],
        [("0", "0"), (".", "."), ("(", "("), (")", ")"), ("+", "+")],
    ]

    for fila in botones:
        columnas = st.columns(len(fila))
        for columna, (etiqueta, valor) in zip(columnas, fila):
            columna.button(
                etiqueta,
                key=f"calc_{etiqueta}",
                use_container_width=True,
                on_click=agregar_texto,
                args=(valor,)
            )

    c1, c2, c3, c4 = st.columns(4)

    c1.button(
        "sin", use_container_width=True,
        on_click=agregar_texto, args=("sin(",)
    )
    c2.button(
        "cos", use_container_width=True,
        on_click=agregar_texto, args=("cos(",)
    )
    c3.button(
        "tan", use_container_width=True,
        on_click=agregar_texto, args=("tan(",)
    )
    c4.button(
        "ln", use_container_width=True,
        on_click=agregar_texto, args=("ln(",)
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.button(
        "log", use_container_width=True,
        on_click=agregar_texto, args=("log(",)
    )
    c6.button(
        "Factorial", use_container_width=True,
        on_click=agregar_texto, args=("factorial(",)
    )
    c7.button(
        "e", use_container_width=True,
        on_click=agregar_texto, args=("e",)
    )

    def limpiar():
        st.session_state.expresion = ""

    c8.button(
        "Limpiar", use_container_width=True,
        on_click=limpiar
    )

    if st.button("Calcular resultado", type="primary"):
        try:
            expresion = st.session_state.expresion.replace("^", "**")
            resultado = evaluar_expresion(expresion)
            st.success(f"Resultado: {resultado:.12g}")
        except Exception as error:
            st.error(f"No se pudo calcular: {error}")


# ==================================================
# MÓDULO ESTADÍSTICO
# ==================================================
with tab2:
    st.subheader("Análisis estadístico")

    st.write(
        "Ingresa los datos de tu problema. Puedes separarlos por comas, "
        "espacios o saltos de línea."
    )

    datos_texto = st.text_area(
        "Datos estadísticos",
        value="18, 20, 22, 22, 24, 25, 25, 25, 27, 28, 30, 32",
        height=120,
        placeholder="Ejemplo: 10, 12, 15, 18, 20"
    )

    tipo_varianza = st.radio(
        "Tipo de análisis de varianza y desviación estándar",
        ["Poblacional", "Muestral"],
        horizontal=True
    )

    if st.button("Calcular estadísticas", type="primary"):
        try:
            datos = convertir_datos(datos_texto)
            n = len(datos)
            media = statistics.mean(datos)
            mediana = statistics.median(datos)
            moda = statistics.multimode(datos)

            varianza = (
                statistics.pvariance(datos)
                if tipo_varianza == "Poblacional"
                else statistics.variance(datos)
                if n >= 2
                else None
            )

            desviacion = (
                math.sqrt(varianza)
                if varianza is not None
                else None
            )

            ordenados = sorted(datos)

            # Cuartiles por método exclusivo, cuando n >= 2
            cuartiles = (
                statistics.quantiles(
                    ordenados, n=4, method="exclusive"
                )
                if n >= 2
                else None
            )

            st.markdown("### Resultados principales")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Cantidad de datos", n)
            m2.metric("Suma", f"{sum(datos):.4f}")
            m3.metric("Media", f"{media:.4f}")
            m4.metric("Mediana", f"{mediana:.4f}")

            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Mínimo", f"{min(datos):.4f}")
            m6.metric("Máximo", f"{max(datos):.4f}")
            m7.metric("Rango", f"{max(datos) - min(datos):.4f}")
            m8.metric(
                "Moda",
                ", ".join(f"{x:g}" for x in moda)
            )

            st.markdown("### Varianza y desviación estándar")

            v1, v2 = st.columns(2)
            v1.metric(
                f"Varianza ({tipo_varianza.lower()})",
                f"{varianza:.4f}" if varianza is not None else "No disponible"
            )
            v2.metric(
                f"Desviación estándar ({tipo_varianza.lower()})",
                f"{desviacion:.4f}" if desviacion is not None else "No disponible"
            )

            st.markdown("### Cuartiles")

            if cuartiles is not None:
                q1, q2, q3 = st.columns(3)
                q1.metric("Q1", f"{cuartiles[0]:.4f}")
                q2.metric("Q2", f"{mediana:.4f}")
                q3.metric("Q3", f"{cuartiles[2]:.4f}")
            else:
                st.info("Se necesitan al menos dos datos para calcular los cuartiles.")

            st.markdown("### Gráfico de los datos")
            st.bar_chart(
                {
                    "Valor": datos
                },
                x_label="Posición del dato",
                y_label="Valor"
            )

            st.markdown("### Datos ordenados")
            st.write(ordenados)

        except Exception as error:
            st.error(f"Revisa los datos ingresados: {error}")
