
import streamlit as st

# Display a title
st.title("Välkommen till min Streamlit-app!")

# Display a button and show a message when clicked
if st.button("Klicka här"):
    st.success("Du klickade på knappen! 🎉")
