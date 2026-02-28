lint:
	ruff check server simulation_core
	cd frontend && npm run lint

format:
	ruff format server simulation_core
	cd frontend && npm run format