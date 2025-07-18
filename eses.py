import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from datetime import datetime

# DB-Konfiguration
DB_USER = "root"
DB_PASSWORD = "Xyz1343!!!"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "ticketsystemabkoo_copy1"

# SQLAlchemy Engine
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

inspector = inspect(engine)

st.title("🛠️ Datenbankverwaltung")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Anzeigen", "✏️ Bearbeiten", "➕ Einfügen", "❌ Löschen"])

# Hilfsfunktion: Spaltennamen einer Tabelle
def get_columns(table):
  try:
    return [col["name"] for col in inspector.get_columns(table)]
  except:
    return []

# -----------------------------
# 📋 Tab 1: Anzeigen
# -----------------------------
with tab1:
  st.subheader("Tabelle anzeigen")
  try:
    tabellen = inspector.get_table_names()
    table_choice = st.selectbox("Wähle eine Tabelle", tabellen)
    if st.button("🔄 Daten laden"):
      df = pd.read_sql(f"SELECT * FROM {table_choice}", con=engine)
      st.dataframe(df)
  except Exception as e:
    st.error("❌ Fehler beim Laden:")
    st.exception(e)

# -----------------------------
# ✏️ Tab 2: Bearbeiten (Minimale Version)
# -----------------------------
with tab2:
  st.subheader("Datensätze bearbeiten (Minimale Version)")
  try:
    tabellen = inspector.get_table_names()
    table_choice_edit = st.selectbox("Tabelle wählen (Bearbeiten)", tabellen, key="edit_table")

    spalten_edit = get_columns(table_choice_edit)

    if not spalten_edit:
      st.warning("Keine Spalten gefunden.")
    else:
      # Wähle eine Primärspalte für die Identifikation der Datensätze
      id_spalte_edit = st.selectbox("Primärspalte wählen (z. B. ID)", spalten_edit, key="edit_id_spalte")

      # Lade die Daten aus der Datenbank
      if st.button("🔄 Daten zum Bearbeiten laden", key="load_edit_data"):
        try:
          # Lade die Daten
          df_edit = pd.read_sql(f"SELECT * FROM {table_choice_edit}", con=engine)

          if df_edit.empty:
            st.info(f"Tabelle '{table_choice_edit}' enthält keine Daten.")
          else:
            # Speichere die ursprünglichen Daten im Session State für späteren Vergleich
            st.session_state.original_data = df_edit.copy()

            # Minimale Konfiguration für den data_editor
            # Keine column_config, keine speziellen Parameter
            edited_df = st.data_editor(df_edit)

            # Button zum Speichern der Änderungen
            if st.button("💾 Änderungen speichern", key="save_changes"):
              changes_made = False

              # Vergleiche die ursprünglichen mit den bearbeiteten Daten
              for index, row in st.session_state.original_data.iterrows():
                original_id = row[id_spalte_edit]
                edited_row_df = edited_df[edited_df[id_spalte_edit] == original_id]

                if not edited_row_df.empty:
                  edited_row = edited_row_df.iloc[0]

                  # Prüfe, ob Änderungen vorgenommen wurden
                  changes = {}
                  for col in spalten_edit:
                    # Überspringe ID-Spalte
                    if col == id_spalte_edit:
                      continue

                    # Vergleiche Werte
                    if str(row[col]) != str(edited_row[col]):
                      changes[col] = edited_row[col]
                      st.write(f"Änderung in Spalte {col}: '{row[col]}' -> '{edited_row[col]}'")

                  # Wenn Änderungen vorhanden sind, führe ein UPDATE durch
                  if changes:
                    try:
                      set_clause = ", ".join([f"{col} = :{col}" for col in changes.keys()])
                      query = text(f"UPDATE {table_choice_edit} SET {set_clause} WHERE {id_spalte_edit} = :id")

                      # Füge die ID zum Dictionary hinzu
                      changes["id"] = original_id

                      with engine.begin() as conn:
                        conn.execute(query, changes)

                      changes_made = True
                      st.write(f"Datensatz mit ID {original_id} aktualisiert.")
                    except Exception as e:
                      st.error(f"❌ Fehler beim Aktualisieren des Datensatzes mit {id_spalte_edit} = {original_id}:")
                      st.exception(e)

              if changes_made:
                st.success("✅ Änderungen erfolgreich gespeichert!")
                # Lade die aktualisierten Daten neu
                df_edit = pd.read_sql(f"SELECT * FROM {table_choice_edit}", con=engine)
                st.session_state.original_data = df_edit.copy()
                st.rerun()
              else:
                st.info("ℹ️ Keine Änderungen zum Speichern gefunden.")

        except Exception as e:
          st.error("❌ Fehler beim Laden oder Bearbeiten der Daten:")
          st.exception(e)
  except Exception as e:
    st.error("❌ Fehler bei der Tabellenauswahl für die Bearbeitung:")
    st.exception(e)

# -----------------------------
# ➕ Tab 3: Einfügen
# -----------------------------
with tab3:
  st.subheader("Datensatz einfügen")
  try:
    tabellen = inspector.get_table_names()
    table_choice = st.selectbox("Tabelle wählen (Einfügen)", tabellen, key="insert_table")
    spalten = get_columns(table_choice)

    inputs = {}
    for spalte in spalten:
      # Spezielle Behandlung für Datum/Zeit-Spalten
      if 'date' in spalte.lower() or 'time' in spalte.lower() or 'erstellt' in spalte.lower():
        # Aktuelles Datum als Standardwert für Datum/Zeit-Spalten
        default_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inputs[spalte] = st.text_input(f"{spalte}", value=default_value, key=f"insert_{spalte}")
      else:
        inputs[spalte] = st.text_input(f"{spalte}", key=f"insert_{spalte}")

    if st.button("💾 Einfügen"):
      try:
        with engine.begin() as conn:
          placeholders = ", ".join([f":{col}" for col in spalten])
          query = text(f"INSERT INTO {table_choice} ({', '.join(spalten)}) VALUES ({placeholders})")
          conn.execute(query, {col: inputs[col] for col in spalten})
        st.success(f"✅ Datensatz in '{table_choice}' eingefügt!")
      except Exception as e:
        st.error("❌ Fehler beim Einfügen:")
        st.exception(e)
  except Exception as e:
    st.error("❌ Fehler bei der Tabellenauswahl:")
    st.exception(e)

# -----------------------------
# ❌ Tab 4: Löschen
# -----------------------------
with tab4:
  st.subheader("Datensatz löschen")
  try:
    tabellen = inspector.get_table_names()
    table_choice = st.selectbox("Tabelle wählen (Löschen)", tabellen, key="delete_table")
    spalten = get_columns(table_choice)

    if not spalten:
      st.warning("Keine Spalten gefunden.")
    else:
      id_spalte = st.selectbox("Primärspalte wählen (z. B. ID)", spalten)
      df = pd.read_sql(f"SELECT * FROM {table_choice}", con=engine)
      df["Anzeigen"] = df[id_spalte].astype(str)
      selected_row = st.selectbox("Datensatz wählen", df["Anzeigen"])

      if st.button("🗑️ Löschen"):
        try:
          with engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {table_choice} WHERE {id_spalte} = :value"),
                         {"value": selected_row})
          st.success(f"✅ Datensatz mit {id_spalte} = {selected_row} gelöscht.")
        except Exception as e:
          st.error("❌ Fehler beim Löschen:")
          st.exception(e)
  except Exception as e:
    st.error("❌ Fehler beim Laden:")
    st.exception(e)