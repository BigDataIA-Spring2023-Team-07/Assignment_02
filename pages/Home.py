import streamlit as st
from PIL import Image

st.title("Are you looking for SEVIR data?")
st.text("Team07-Assignment1")
st.text("Let us fetch that for you!")
image = Image.open('image.png')
st.image(image, caption='four humans working to fetch satelite data')