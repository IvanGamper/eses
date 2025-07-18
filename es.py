import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🛠️ Test-App ohne Datenbank")

# Dummy-Daten
dummy_tables = {
    "ticket": pd.DataFrame({
        "ID": [1, 2],
        "Titel": ["Login Problem", "Bug in UI"],
        "Status": ["Offen", "Geschlossen"],
        "Erstellt_am": [datetime.now(), datetime.now()]
    }),
    "kunde": pd.DataFrame({
        "ID": [100, 101],
        "Name": ["Müller GmbH", "Test AG"],
        "Email": ["mueller@example.com", "test@example.com"]
    })
}

tab1, tab2, tab3, tab4 = st.tabs(["📋 Anzeigen", "✏️ Bearbeiten", "➕ Einfügen", "❌ Löschen"])

# Tab 1: Anzeigen
with tab1:
    st.subheader("Tabelle anzeigen")
    table_choice = st.selectbox("Wähle eine Tabelle", list(dummy_tables.keys()))
    if st.button("🔄 Daten laden"):
        st.dataframe(dummy_tables[table_choice])

# Tab 2: Bearbeiten
with tab2:
    st.subheader("Bearbeiten (Simulation)")
    table_choice = st.selectbox("Tabelle wählen", list(dummy_tables.keys()), key="edit_table")
    df = dummy_tables[table_choice]
    edited_df = st.data_editor(df)
    if st.button("💾 Änderungen speichern", key="edit_save"):
        st.success("✅ Änderungen gespeichert (simuliert)")

# Tab 3: Einfügen
with tab3:
    st.subheader("Datensatz einfügen (Simulation)")
    table_choice = st.selectbox("Tabelle wählen", list(dummy_tables.keys()), key="insert_table")
    spalten = dummy_tables[table_choice].columns
    new_row = {spalte: st.text_input(f"{spalte}") for spalte in spalten}
    if st.button("➕ Hinzufügen"):
        st.success("✅ Datensatz eingefügt (simuliert)")

# Tab 4: Löschen
with tab4:
    st.subheader("Datensatz löschen (Simulation)")
    table_choice = st.selectbox("Tabelle wählen", list(dummy_tables.keys()), key="delete_table")
    df = dummy_tables[table_choice]
    row_id = st.selectbox("ID wählen", df["ID"])
    if st.button("🗑️ Löschen"):
        st.success(f"✅ Datensatz mit ID {row_id} gelöscht (simuliert)")
