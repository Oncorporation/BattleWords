# file: D:/Projects/Battlewords/tests/test_apptest.py
from streamlit.testing.v1 import AppTest

def test_app_runs():
    at = AppTest.from_file("app.py")
    at.run()
    assert not at.exception