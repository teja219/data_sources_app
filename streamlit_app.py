import inspect
import textwrap
import streamlit as st
from pathlib import Path

import data_sources
from data_sources import big_query

from utils import ui, intro

DATA_SOURCES = {
    intro.INTRO_IDENTIFIER: {
        "module": intro,
        "secret_key": None,
        "docs_url": None,
        "get_connector": None,
    },
    "🔎  BigQuery": {
        "module": data_sources.big_query,
        "secret_key": "bigquery",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/bigquery.html",
        "get_connector": data_sources.big_query.get_connector,
        "tutorial": data_sources.big_query.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-bigquery",
        "secrets_template": data_sources.big_query.TOML_SERVICE_ACCOUNT,
    },
    #
    # (Currently disregarding other data sources)
    #
    # "❄️ Snowflake": {
    #     "app": ds.snowflake_app.main,
    #     "secret_key": "snowflake",
    #     "docs_url": "https://docs.streamlit.io/en/latest/tutorial/snowflake.html",
    #     "get_connector": ds.snowflake_app.get_connector,
    # },
    # "📝 Public Google Sheet": {
    #     "app": google_sheet_app,
    #     "secret_key": "gsheets",
    #     "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
    #     "get_connector": ds.google_sheet_app.get_connector,
    # },
}

NO_CREDENTIALS_FOUND = """❌ **No credentials were found for '`{}`' in your Streamlit Secrets.**   
Please follow our [tutorial]({}) or make sure that your secrets look like the following:
```toml
{}
```"""

CREDENTIALS_FOUND_BUT_ERROR = """**❌ Credentials were found but there is an error.**  
While you have successfully filled in Streamlit secrets for the key `{}`,
we have not been able to connect to the data source. You might have forgotten some fields.  
            
Check the exception below 👇  
"""

WHAT_NEXT = """## What next?

Kick-off your own app now! 🚀 

Above, we provided you with sufficient code to create an app that can take 
advantage of your data. Paste it into a new Python script and use it as a starter! 

🤔 Stuck? Check out our docs on [creating](https://docs.streamlit.io/library/get-started/create-an-app) 
and [deploying](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app) an app or reach out to 
support@streamlit.io!
"""


def has_data_source_key_in_secrets(data_source: str) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def show_success(data_source: str):
    st.success(
        f"""👏 Congrats! You have successfully filled in your Streamlit secrets..  
    Below, you'll find a sample app that connects to {data_source} and its associated [source code](#code)."""
    )


def show_error_when_not_connected(data_source: str):

    st.error(
        NO_CREDENTIALS_FOUND.format(
            DATA_SOURCES[data_source]["tutorial_anchor"],
            DATA_SOURCES[data_source]["secret_key"],
            DATA_SOURCES[data_source]["secrets_template"],
        )
    )

    st.write(f"### Tutorial: connecting to {data_source}")
    ui.load_keyboard_class()
    DATA_SOURCES[data_source]["tutorial"]()


def what_next():
    st.write(WHAT_NEXT)


def code(app):
    st.markdown("## Code")
    sourcelines, _ = inspect.getsourcelines(app)
    st.code(textwrap.dedent("".join(sourcelines[1:])), "python")


def connect(data_source):
    """Try connecting to data source.
    Print exception should something wrong happen."""

    try:
        get_connector = DATA_SOURCES[data_source]["get_connector"]
        connector = get_connector()
        return connector

    except Exception as e:

        st.sidebar.error("❌ Could not connect.")

        st.error(
            CREDENTIALS_FOUND_BUT_ERROR.format(DATA_SOURCES[data_source]["secret_key"])
        )

        st.exception(e)

        st.stop()


if __name__ == "__main__":

    st.set_page_config(layout="centered")

    data_source = st.sidebar.selectbox(
        "Choose a data source",
        list(DATA_SOURCES.keys()),
        index=0,
    )

    st.session_state.active_page = data_source
    if "data_sources_already_connected" not in st.session_state:
        st.session_state.data_sources_already_connected = list()

    if data_source == intro.INTRO_IDENTIFIER:
        show_code = False
        show_balloons = False

    else:
        show_code = True
        show_balloons = True

        # First, look for credentials in the secrets
        data_source_key_in_secrets = has_data_source_key_in_secrets(data_source)

        if data_source_key_in_secrets:
            connect(data_source)
            st.sidebar.success("✔ Connected!")
            show_success(data_source)
        else:
            st.sidebar.error("❌ Could not connect.")
            show_error_when_not_connected(data_source)
            st.stop()

    # Release balloons to celebrate (only upon first success)
    if (
        show_balloons
        and data_source not in st.session_state.data_sources_already_connected
    ):
        st.session_state.data_sources_already_connected.append(data_source)
        show_balloons = False
        st.balloons()

    # Display data source app
    data_source_app = DATA_SOURCES[st.session_state["active_page"]]["module"].app
    data_source_app()

    # Show source code and what next
    if show_code:
        code(data_source_app)
        what_next()