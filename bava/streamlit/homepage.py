"""
    This module displays the home page of the Brain Artery Visualization and Analysis app.
"""
import streamlit as st

def home_page():
    st.title(":brain: Brain Artery Network Visualization and Analysis (BAVA)")
    st.subheader("BAVA is a cutting-edge online platform designed for medical researchers focusing on neurology," 
             "particularly in the study of brain artery networks. It integrates powerful visualization tools "
             "with statistical analysis and artificial intelligence (AI) capabilities to facilitate the exploration"
             " and analysis of vascular diseases.")

if __name__ == "__main__":
    home_page()