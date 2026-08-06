import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st

from app.acquisition.acquisition_models import ICP
from app.ui.workflow_runner import run_workflow
from app.ui.prospect_view import results_to_dataframe


st.set_page_config(
    page_title="AI ICP Qualification Engine",
    layout="wide",
)


st.title(
    "AI ICP Qualification Engine"
)


st.header(
    "Recherche et qualification automatique de prospects B2B.",
    divider='rainbow'
)


st.subheader(
    "Configuration ICP (Ideal Customer Profile)"
)


job_title = st.text_input(
    "Métier cible",
    value="Business Coach",
)


country = st.text_input(
    "Pays",
    value="France",
)


if st.button("Lancer la recherche"):

    icp = ICP(
        job_titles=[
            job_title
        ],
        countries=[
            country
        ],
    )


    progress = st.progress(
        0,
        text="Initialisation..."
    )

    def update_progress(
        percent,
        text,
    ):
        progress.progress(
            percent,
            text=text,
        )

    try:

        results = run_workflow(
            icp,
            progress_callback=update_progress,
        )

        st.session_state.results = results

        progress.empty()
            
        st.success(
            f"{len(results)} prospects traités"
        )

        st.subheader(
            "Résultats"
        )


        df = results_to_dataframe(
            results
        )


        st.dataframe(
            df,
            width="stretch"
        )


    except Exception as exc:

        st.error(
            f"Erreur pendant le workflow : {exc}"
        )