import argparse
import sys
from pathlib import Path

from storage.data_manager import DataManager
from services.treatment_service import TreatmentService
from services.adherence_service import AdherenceService
from services.symptom_service import SymptomService
from services.followup_service import FollowUpService
from services.refill_service import RefillService
from app.refills import RefillManager
from cli.main_menu import main_menu


def _build_services(data_manager):
    """
    Instantiate all service objects and return them
    as a dict keyed by name.

    This is the single place where the entire dependency
    graph is wired together.
    """
    services = {}

    # Services that use DataManager for JSON persistence
    services["treatment"] = TreatmentService(data_manager)
    services["adherence"] = AdherenceService(data_manager)

    # Services that are currently in-memory only
    services["symptom"] = SymptomService()
    services["followup"] = FollowUpService()

    # RefillService requires a RefillManager per patient+medication.
    # We create a default/placeholder one here; the CLI menus
    # will create specific RefillManagers when needed.
    # For now, we create a manager for the default test patient.
    medications = data_manager.load_data("medications.json") or []
    if medications:
        first_med = medications[0]
        refill_manager = RefillManager(
            patient_id=first_med.get("medication_id", 1),
            medication_id=first_med.get("medication_id", 1),
            quantity=first_med.get("quantity", 180),
            frequency=first_med.get("frequency", 1),
            start_date="2026-09-10"
        )
    else:
        refill_manager = RefillManager(
            patient_id=1,
            medication_id=1,
            quantity=180,
            frequency=1,
            start_date="2026-09-10"
        )

    services["refill"] = RefillService(refill_manager)

    return services


def main():
    """
    Entry point for the Smart TB Aftercare System CLI.

    Usage:
        python main.py                    # interactive mode
        python main.py --data-dir ./data   # specify data directory
        python main.py --help              # show help
    """
    parser = argparse.ArgumentParser(
        description="Smart TB Aftercare System — "
                    "CLI for TB treatment monitoring"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(Path(__file__).parent / "data"),
        help="Path to the directory containing JSON data files "
             "(default: ./data)"
    )

    args = parser.parse_args()

    # Initialize the data layer
    data_manager = DataManager(args.data_dir)

    # Wire up all services
    services = _build_services(data_manager)

    # Launch the interactive main menu
    print("\nStarting Smart TB Aftercare System...")
    print(f"Data directory: {args.data_dir}")

    main_menu(data_manager, services)


if __name__ == "__main__":
    main()
