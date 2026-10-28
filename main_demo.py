import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from data.repositories.file_result_repository import FileResultRepository
from demo.demo_data import (
    DEMO_BADGE_TEXT,
    DEMO_CORPUS_BLEU_SCORE,
    DEMO_DATASET_NAME,
    DEMO_ENDPOINT,
    DEMO_ENTRIES,
)
from demo.demo_question_repository import DemoQuestionRepository
from demo.demo_run_evaluation import DemoRunEvaluation
from demo.demo_scoring_method import DemoScoringMethod
from domain.scoring.scoring_method import ScoringMethod
from domain.usecases.build_metric_overview import BuildMetricOverview
from domain.usecases.export_result import ExportResult
from domain.usecases.load_questions import LoadQuestions
from domain.usecases.prepare_scoring_methods import PrepareScoringMethods
from domain.usecases.rescore_result import RescoreResult
from main import build_scoring_methods
from presentation.controllers.evaluation_controller import EvaluationController, EvaluationUseCases
from presentation.controllers.startup_controller import StartupController
from presentation.views.main_window import MainWindow, MainWindowOptions
from presentation.views.splash_screen import SplashScreen

DEMO_DATASET_PATH = Path(DEMO_DATASET_NAME)
SPLASH_STATUS = "Loading demo data…"
BLEU_IDENTIFIER = "bleu"
STARTUP_FAILURE_EXIT_CODE = 1


def build_demo_methods() -> list[ScoringMethod]:
    return [
        DemoScoringMethod(
            reference,
            {
                (entry.expected_answer, entry.given_answer): entry.scores[reference.identifier]
                for entry in DEMO_ENTRIES
            },
            corpus_value=DEMO_CORPUS_BLEU_SCORE if reference.identifier == BLEU_IDENTIFIER else None,
        )
        for reference in build_scoring_methods()
    ]


def build_controllers() -> tuple[StartupController, EvaluationController]:
    demo_methods = build_demo_methods()
    use_cases = EvaluationUseCases(
        load_questions=LoadQuestions(DemoQuestionRepository(DEMO_ENTRIES)),
        run_evaluation=DemoRunEvaluation(DEMO_ENTRIES),
        rescore_result=RescoreResult(),
        build_overview=BuildMetricOverview(),
        export_result=ExportResult(FileResultRepository()),
    )
    startup_controller = StartupController(PrepareScoringMethods(demo_methods))
    return startup_controller, EvaluationController(use_cases, demo_methods)


def main() -> int:
    application = QApplication(sys.argv)
    startup_controller, evaluation_controller = build_controllers()
    splash = SplashScreen(SPLASH_STATUS)
    options = MainWindowOptions(
        dataset_picker=lambda: DEMO_DATASET_PATH,
        initial_endpoint=DEMO_ENDPOINT,
        badge_text=DEMO_BADGE_TEXT,
    )
    window = MainWindow(evaluation_controller, options)

    def open_main_window() -> None:
        window.show()
        splash.close()
        evaluation_controller.load_dataset(DEMO_DATASET_PATH)
        evaluation_controller.start_evaluation(DEMO_ENDPOINT, "", "")

    def abort_startup(message: str) -> None:
        splash.show_failure(message)
        application.exit(STARTUP_FAILURE_EXIT_CODE)

    startup_controller.ready.connect(open_main_window)
    startup_controller.failed.connect(abort_startup)
    application.aboutToQuit.connect(evaluation_controller.shutdown)
    splash.show()
    startup_controller.start()
    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
