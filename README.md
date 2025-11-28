# 💸 Expense Tracker – Finanzas Personales

**Expense Tracker** es una aplicación web construida con **Streamlit** para ayudarte a gestionar tus finanzas personales de forma visual e interactiva. Con esta app puedes registrar tus gastos, administrar presupuestos por categoría, analizar tus hábitos de consumo y exportar tus datos, todo desde una interfaz intuitiva y responsiva.

---

## 🖼️ Vistas Previas

| Dashboard 📊 | Agregar Gasto ➕ | Presupuesto 💰 |
|-------------|------------------|----------------|
| ![Dashboard](https://github.com/frontenddeveloper2025dev/GastoTrack/blob/main/Expense%20Tracker%20%201.png) | ![Add Expense](https://github.com/frontenddeveloper2025dev/GastoTrack/blob/main/Expense%20Tracker%20%202.png) | ![Budget](https://github.com/frontenddeveloper2025dev/GastoTrack/blob/main/Expense%20Tracker%20%203.png) |

| Análisis 📈 | Exportar Datos 📥 |
|-------------|-------------------|
| ![Analytics](https://github.com/frontenddeveloper2025dev/GastoTrack/blob/main/Expense%20Tracker%204%20.png) | ![Export](https://github.com/frontenddeveloper2025dev/GastoTrack/blob/main/Expense%20Tracker%20%205.png) |

---

## 🚀 Características Principales

- Registro rápido de gastos
- Presupuestos mensuales por categoría
- Análisis visual de tus gastos (gráficas interactivas)
- Filtros por fecha, categoría y monto
- Exportación de datos en CSV
- Interfaz intuitiva con navegación lateral

---

## 🧠 Arquitectura del Proyecto

### 🔹 Frontend (UI)

- **Framework:** [Streamlit](https://streamlit.io/)
- **Diseño:** Layout amplio con navegación lateral
- **Visualizaciones:** Plotly Express, Plotly Graph Objects y Matplotlib
- **Páginas:** 
  - Dashboard
  - Agregar Gasto
  - Gestionar Gastos
  - Presupuestos
  - Análisis
  - Exportar Datos

### 🔹 Backend (Lógica y Datos)

- **Base de datos:** SQLite (`expenses.db`)
- **Tablas:**
  - `expenses`: descripción, monto, categoría, fecha, notas
  - `budgets`: categoría, límite, período (por defecto mensual)
- **Gestión de estado:** `st.session_state` para sincronización de datos
- **Procesamiento:** `pandas` para manipulación de datos

---

## 🧱 Patrón de Diseño

- Arquitectura modular: componentes separados por lógica, visualización y base de datos
- Manejo de errores y validaciones
- Estilos y configuración centralizados
- Flujo de estado consistente y reactivo

---

## 🧩 Dependencias

Instálalas con `pip install -r requirements.txt`:

```text
streamlit
pandas
matplotlib
plotly
numpy
