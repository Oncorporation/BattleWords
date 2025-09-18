import streamlit as st

from battlewords.ui import run_app


def _new_game() -> None:
    st.session_state.clear()
    _init_session()
    st.rerun()


def main():
    st.set_page_config(page_title="Battlewords (POC)", layout="wide")
    run_app()


if __name__ == "__main__":
    main()