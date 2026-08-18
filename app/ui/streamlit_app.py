import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st

from app.acquisition.acquisition_models import ICP
from app.core.logging import get_logger, setup_logging
from app.core.settings import settings
from app.ui.workflow_runner import run_workflow
from app.ui.prospect_view import results_to_dataframe

setup_logging()
logger = get_logger(__name__)


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

if "workflow_run_count" not in st.session_state:
    st.session_state.workflow_run_count = 0

if "last_workflow_run_at" not in st.session_state:
    st.session_state.last_workflow_run_at = 0.0

if st.button("Lancer la recherche"):
    now = time.time()
    elapsed_since_last_run = now - st.session_state.last_workflow_run_at
    remaining_cooldown = settings.WORKFLOW_COOLDOWN_SECONDS - elapsed_since_last_run

    if remaining_cooldown > 0:
        st.warning(
            "Veuillez patienter encore "
            f"{remaining_cooldown:.0f} s avant de relancer une recherche."
        )
    elif st.session_state.workflow_run_count >= settings.MAX_WORKFLOW_RUNS_PER_SESSION:
        st.warning(
            "Nombre maximal de recherches atteint pour cette session "
            f"({settings.MAX_WORKFLOW_RUNS_PER_SESSION}). "
            "Rechargez la page pour réinitialiser."
        )
    else:
        st.session_state.last_workflow_run_at = now
        st.session_state.workflow_run_count += 1

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

            st.success(
                f"{len(results)} prospects traités"
            )

            st.subheader("Résultats")

            df = results_to_dataframe(results)
            st.dataframe(
                df,
                column_config={
                    "Profil LinkedIn": st.column_config.LinkColumn(
                        "Profil LinkedIn",
                        display_text="Ouvrir le profil",
                    ),
                },
                width="stretch",
                hide_index=True,
            )

        except Exception:
            progress.empty()
            logger.exception("Le workflow a échoué pendant l'exécution.")
            st.error(
                "Une erreur est survenue pendant le traitement. "
                "Consultez les journaux serveur pour plus de détails."
            )
