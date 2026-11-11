# BharatGov Access Makefile

.PHONY: help install test test-unit test-safety test-auditors test-validator pilot run-docker stop-docker clean \
        dashboard-verify dashboard-shots paper deck package-test package-build assets

help:
	@echo "BharatGov Access Observatory commands:"
	@echo "  install          - Install local dependencies and Playwright browsers"
	@echo "  test             - Run full pytest test suite"
	@echo "  test-safety      - Run safety governor verification tests"
	@echo "  test-auditors    - Run deterministic auditors verification tests"
	@echo "  test-validator   - Run data schema and validation engine tests"
	@echo "  pilot            - Run 10-site heterogeneous pilot collection"
	@echo "  dashboard-verify - Verify dashboard layout, data, behaviour and a11y"
	@echo "  dashboard-shots  - Capture presentation screenshots"
	@echo "  paper            - Render the research paper to HTML and PDF"
	@echo "  deck             - Build the 5-slide final evaluation deck"
	@echo "  package-test     - Run the bharatgov-access package tests"
	@echo "  package-build    - Build the wheel and sdist"
	@echo "  assets           - Rebuild the India map and refresh fonts"
	@echo "  run-docker       - Start Docker Compose production stack"
	@echo "  stop-docker      - Stop Docker Compose services"
	@echo "  clean            - Clean temporary test artifacts"

install:
	pip install -r requirements.txt
	playwright install chromium

test:
	pytest tests/ -v

test-safety:
	pytest tests/test_safety_governor.py -v

test-auditors:
	pytest tests/test_auditors.py -v

test-validator:
	pytest tests/test_validator_engine.py -v

pilot:
	python scripts/run_pilot.py

dashboard-verify:
	python scripts/verify_dashboard.py

dashboard-shots:
	python scripts/capture_screenshots.py

paper:
	python scripts/render_paper.py

deck:
	python scripts/build_deck.py

package-test:
	cd packages/bharatgov-access && python -m pytest -q

package-build:
	cd packages/bharatgov-access && python -m build

assets:
	python scripts/build_india_map.py
	python scripts/fetch_fonts.py

run-docker:
	docker compose up -d

stop-docker:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
