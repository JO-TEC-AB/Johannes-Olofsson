
import streamlit as st
import json
from datetime import date
import fitz  # PyMuPDF

st.set_page_config(page_title="Offertkalkyl", layout="wide")

st.title("📄 Offertkalkyl")

# Kundinformation
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("Kundnamn", "")
with col2:
    offer_date = st.date_input("Datum", value=date.today())

# Artikelinmatning
st.subheader("🧾 Artiklar")
if "rows" not in st.session_state:
    st.session_state.rows = [{"Artikel": "", "A-pris": 0.0, "Antal": 0}]

def add_row():
    st.session_state.rows.append({"Artikel": "", "A-pris": 0.0, "Antal": 0})

for i, row in enumerate(st.session_state.rows):
    cols = st.columns([4, 2, 2, 2])
    row["Artikel"] = cols[0].text_input("Artikel", value=row["Artikel"], key=f"artikel_{i}")
    row["A-pris"] = cols[1].number_input("A-pris", value=row["A-pris"], key=f"apris_{i}")
    row["Antal"] = cols[2].number_input("Antal", value=row["Antal"], key=f"antal_{i}", step=1)
    row["Summa"] = row["A-pris"] * row["Antal"]
    cols[3].write(f"{row['Summa']:.2f} kr")

st.button("➕ Lägg till rad", on_click=add_row)

# Beräkningar
st.subheader("📊 Kalkyl")
markup = st.number_input("Påslag (%)", value=35.0)
total_cost = sum(row["Summa"] for row in st.session_state.rows)
offer_cost = total_cost * (1 + markup / 100)
profit = offer_cost - total_cost

col1, col2, col3 = st.columns(3)
col1.metric("Total kostnad", f"{total_cost:.2f} kr")
col2.metric("Kostnad offert", f"{offer_cost:.2f} kr")
col3.metric("Vinst", f"{profit:.2f} kr")

# Spara offert
def save_offer():
    data = {
        "kundnamn": customer_name,
        "datum": str(offer_date),
        "påslag_procent": markup,
        "total_kostnad": f"{total_cost:.2f} kr",
        "kostnad_offert": f"{offer_cost:.2f} kr",
        "vinst": f"{profit:.2f} kr",
        "artiklar": st.session_state.rows
    }
    json_str = json.dumps(data, indent=4)
    st.download_button("💾 Ladda ner offert (.json)", data=json_str, file_name="offert.json", mime="application/json")

# Ladda offert
uploaded_file = st.file_uploader("📂 Öppna offert (.json)", type="json")
if uploaded_file:
    loaded_data = json.load(uploaded_file)
    customer_name = loaded_data.get("kundnamn", "")
    offer_date = date.fromisoformat(loaded_data.get("datum", str(date.today())))
    markup = float(loaded_data.get("påslag_procent", 35))
    st.session_state.rows = loaded_data.get("artiklar", [])

# Exportera till PDF
def export_pdf():
    doc = fitz.open()
    page = doc.new_page()
    y = 50
    page.insert_text((50, y), "Offertkalkyl", fontsize=16)
    y += 30
    page.insert_text((50, y), f"Kundnamn: {customer_name}", fontsize=12)
    y += 20
    page.insert_text((50, y), f"Datum: {offer_date}", fontsize=12)
    y += 30
    page.insert_text((50, y), "Artikel       A-pris     Antal     Summa", fontsize=12)
    y += 15
    for row in st.session_state.rows:
        line = f"{row['Artikel']:<12} {row['A-pris']:<9.2f} {row['Antal']:<8} {row['Summa']:.2f} kr"
        page.insert_text((50, y), line, fontsize=11)
        y += 15
    y += 20
    page.insert_text((50, y), f"Påslag: {markup:.2f}%", fontsize=12)
    y += 15
    page.insert_text((50, y), f"Total kostnad: {total_cost:.2f} kr", fontsize=12)
    y += 15
    page.insert_text((50, y), f"Kostnad offert: {offer_cost:.2f} kr", fontsize=12)
    y += 15
    page.insert_text((50, y), f"Vinst: {profit:.2f} kr", fontsize=12)

    pdf_bytes = doc.write()
    st.download_button("📄 Exportera till PDF", data=pdf_bytes, file_name="offert.pdf", mime="application/pdf")

save_offer()
export_pdf()
