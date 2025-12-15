import streamlit as st
import pandas as pd
import io

# --- 1. Inicjalizacja Danych Magazynu ---
# Funkcja do wczytywania lub inicjalizacji DataFrame
def get_inventory_df():
    # Sprawdzenie, czy DataFrame magazynu jest już w pamięci sesji
    if 'inventory_df' not in st.session_state:
        # Jeśli nie, utwórz przykładowy DataFrame
        data = {
            'Nazwa Towaru': ['Laptop Business', 'Monitor 27"', 'Mysz Bezprzewodowa', 'Klawiatura Mechaniczna'],
            'Ilość': [15, 30, 50, 25],
            'Cena Jednostkowa (PLN)': [3500.00, 850.00, 75.00, 420.00]
        }
        df = pd.DataFrame(data)
        # Dodaj kolumnę 'Wartość', obliczaną jako Ilość * Cena
        df['Wartość (PLN)'] = df['Ilość'] * df['Cena Jednostkowa (PLN)']
        st.session_state['inventory_df'] = df
    return st.session_state['inventory_df']

# --- 2. Główne Funkcje Aplikacji ---

def add_item(name, quantity, price):
    """Dodaje nowy towar do magazynu."""
    df = get_inventory_df()
    
    # Utworzenie nowego wiersza
    new_data = {
        'Nazwa Towaru': [name],
        'Ilość': [quantity],
        'Cena Jednostkowa (PLN)': [price],
        'Wartość (PLN)': [quantity * price]
    }
    new_row = pd.DataFrame(new_data)
    
    # Dodanie nowego wiersza do istniejącego DataFrame
    st.session_state['inventory_df'] = pd.concat([df, new_row], ignore_index=True)
    st.success(f"Dodano towar: **{name}**")

def display_inventory():
    """Wyświetla tabelę magazynu oraz podsumowanie wartości."""
    df = get_inventory_df()
    
    st.subheader("Aktualny Stan Magazynu")
    
    # Wyświetlenie tabeli
    st.dataframe(df, use_container_width=True)
    
    # Podsumowanie
    total_value = df['Wartość (PLN)'].sum()
    st.markdown(f"### 💰 Całkowita Wartość Magazynu: **{total_value:,.2f} PLN**")

# --- 3. Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty System Zarządzania Magazynem")
st.caption("Aplikacja zbudowana w Streamlit i Pandas.")

# Utworzenie zakładek
tab_view, tab_add, tab_edit, tab_import_export = st.tabs(["📊 Przegląd Magazynu", "➕ Dodaj Towar", "✏️ Edytuj Towary", "💾 Import/Eksport"])

# --- Zakładka: Przegląd Magazynu ---
with tab_view:
    display_inventory()

# --- Zakładka: Dodaj Towar ---
with tab_add:
    st.subheader("Dodawanie Nowego Towaru")
    
    # Formularz dodawania
    with st.form("add_item_form"):
        new_name = st.text_input("Nazwa Towaru", max_chars=100)
        new_quantity = st.number_input("Ilość", min_value=1, value=1, step=1)
        new_price = st.number_input("Cena Jednostkowa (PLN)", min_value=0.01, value=10.00, step=0.01, format="%.2f")
        
        submitted = st.form_submit_button("Dodaj do Magazynu")
        
        if submitted and new_name:
            add_item(new_name, new_quantity, new_price)
            # Odświeżenie widoku po dodaniu
            st.session_state['inventory_df'] = get_inventory_df()

# --- Zakładka: Edytuj Towary ---
with tab_edit:
    st.subheader("Edycja Istniejących Wpisów")
    
    df_to_edit = get_inventory_df().copy()
    
    # Użycie st.data_editor do interaktywnej edycji danych
    edited_df = st.data_editor(
        df_to_edit,
        column_config={
            "Nazwa Towaru": st.column_config.TextColumn("Nazwa Towaru", required=True),
            "Ilość": st.column_config.NumberColumn("Ilość", min_value=0, step=1, required=True),
            "Cena Jednostkowa (PLN)": st.column_config.NumberColumn("Cena Jednostkowa (PLN)", min_value=0.01, format="%.2f PLN", required=True),
            # Kolumna 'Wartość' jest tylko do odczytu
            "Wartość (PLN)": st.column_config.NumberColumn("Wartość (PLN)", format="%.2f PLN", disabled=True) 
        },
        hide_index=True,
        num_rows="dynamic", # Pozwala na dodawanie/usuwanie wierszy bezpośrednio w edytorze
        use_container_width=True
    )
    
    # Logika aktualizacji DataFrame po edycji
    if not edited_df.equals(df_to_edit):
        # Ponowne przeliczenie kolumny Wartość (PLN)
        edited_df['Wartość (PLN)'] = edited_df['Ilość'] * edited_df['Cena Jednostkowa (PLN)']
        st.session_state['inventory_df'] = edited_df
        st.success("Zmiany w magazynie zostały zapisane!")

# --- Zakładka: Import/Eksport ---
with tab_import_export:
    st.subheader("Eksport i Import Danych")
    
    df_export = get_inventory_df()
    
    # 1. Eksport do CSV
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Eksportuj do CSV (Pobierz plik)",
        data=csv,
        file_name='magazyn_stan.csv',
        mime='text/csv',
        key='download_csv'
    )
    
    st.markdown("---")
    
    # 2. Import z CSV
    uploaded_file = st.file_uploader("Importuj z pliku CSV", type="csv")
    if uploaded_file is not None:
        try:
            # Wczytanie pliku do nowego DataFrame
            imported_df = pd.read_csv(uploaded_file)
            
            # Wymagane kolumny dla importu
            required_cols = ['Nazwa Towaru', 'Ilość', 'Cena Jednostkowa (PLN)']
            
            if all(col in imported_df.columns for col in required_cols):
                # Obliczenie Wartości dla importowanych danych
                imported_df['Wartość (PLN)'] = imported_df['Ilość'] * imported_df['Cena Jednostkowa (PLN)']
                
                # Zastąpienie obecnego stanu magazynu
                st.session_state['inventory_df'] = imported_df
                st.success("Pomyślnie zaimportowano dane z pliku CSV!")
                # Odświeżenie widoku
                st.rerun()
            else:
                st.error(f"Plik CSV musi zawierać kolumny: {', '.join(required_cols)}")
        except Exception as e:
            st.error(f"Wystąpił błąd podczas importu pliku: {e}")
