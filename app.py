import streamlit as st

from battlewords.ui import run_app
def main():
    st.set_page_config(page_title="Battlewords (POC)", layout="wide")
    run_app()


if __name__ == "__main__":
    main()