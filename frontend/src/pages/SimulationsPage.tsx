import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createSimulation, getSimulations } from "../api/simulations";

const USER_ID = 1;

export function SimulationsPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");

  const simulationsQuery = useQuery({
    queryKey: ["simulations", USER_ID],
    queryFn: () => getSimulations(USER_ID),
  });

  const createMutation = useMutation({
    mutationFn: (simulationName: string) => createSimulation(USER_ID, simulationName),
    onSuccess: () => {
      setName("");
      queryClient.invalidateQueries({ queryKey: ["simulations", USER_ID] });
    },
  });

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <Link to="/genome-templates">Перейти к шаблонам генома</Link>
      </div>
      
      <h1>Симуляции</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Название симуляции"
        />
        <button
          onClick={() => {
            if (!name.trim()) return;
            createMutation.mutate(name.trim());
          }}
        >
          Создать
        </button>
      </div>

      {simulationsQuery.isLoading && <p>Загрузка...</p>}
      {simulationsQuery.isError && <p>Ошибка загрузки симуляций</p>}

      <ul>
        {simulationsQuery.data?.map((simulation) => (
          <li key={simulation.id}>
            <Link to={`/simulations/${simulation.id}`}>
              {simulation.name}
            </Link>{" "}
            — статус: {simulation.status}, tick: {simulation.tick}
          </li>
        ))}
      </ul>
    </div>
  );
}