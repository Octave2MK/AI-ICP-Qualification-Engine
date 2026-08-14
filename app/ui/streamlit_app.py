import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st

from app.acquisition.acquisition_models import ICP
from app.ui.workflow_runner import run_workflow
from app.ui.prospect_view import (
    results_to_dataframe,
    summarize_results,
)


st.set_page_config(
    page_title="AI ICP Qualification Engine",
    layout="wide",
)

st.title("AI ICP Qualification Engine")
st.header(
    "Recherche et qualification automatique de prospects B2B.",
    divider="rainbow",
)

st.subheader("Configuration ICP (Ideal Customer Profile)")

job_title = st.text_input(
    "Métier cible",
    value="Business Coach",
)

country = st.text_input(
    "Pays cible",
    value="France",
)

sector = st.text_input(
    "Secteur / domaine",
    value="Coaching",
)

max_prospects = st.number_input(
    "Nombre de prospects souhaités",
    min_value=1,
    max_value=100,
    value=20,
    step=1,
    help="Nombre maximal de profils à conserver après filtrage et déduplication.",
)

required_keywords_text = st.text_input(
    "Mots-clés obligatoires",
    value="",
    help="Séparez les mots-clés par des virgules.",
)

forbidden_keywords_text = st.text_input(
    "Mots-clés interdits",
    value="étudiant, stage, stagiaire, student, internship",
    help="Les profils contenant ces termes seront exclus.",
)

if st.button("Lancer la recherche"):
    required_keywords = [
        item.strip()
        for item in required_keywords_text.split(",")
        if item.strip()
    ]

    forbidden_keywords = [
        item.strip()
        for item in forbidden_keywords_text.split(",")
        if item.strip()
    ]

    icp = ICP(
        job_titles=[job_title.strip()] if job_title.strip() else [],
        countries=[country.strip()] if country.strip() else [],
        sectors=[sector.strip()] if sector.strip() else [],
        keywords=required_keywords,
        required_keywords=required_keywords,
        forbidden_keywords=forbidden_keywords,
        max_prospects=int(max_prospects),
    )

    progress = st.progress(0, text="Initialisation...")

    def update_progress(percent, text):
        progress.progress(percent, text=text)

    try:
        results = run_workflow(
            icp,
            progress_callback=update_progress,
        )
        st.session_state.results = results

        progress.empty()

        summary = summarize_results(results)

        st.success(
            f"{summary['successful']} réussis / "
            f"{summary['errors']} erreurs / "
            f"{summary['filtered']} filtrés"
        )

        st.subheader("Résultats")

        df = results_to_dataframe(results)
        st.dataframe(df, width="stretch")

    except Exception as exc:
        progress.empty()
        st.error(f"Erreur pendant le workflow : {exc}")
