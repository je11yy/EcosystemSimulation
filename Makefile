lint:
	ruff check simulation_service api_server simulation_core
	cd frontend && npm run lint

format:
	ruff format simulation_service api_server simulation_core
	cd frontend && npm run format