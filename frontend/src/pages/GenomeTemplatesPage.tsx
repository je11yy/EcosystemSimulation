import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createGenomeTemplate, getGenomeTemplates } from "../api/genomeTemplates";

const USER_ID = 1;

export function GenomeTemplatesPage() {
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [speciesGroup, setSpeciesGroup] = useState("default_species");

  const templatesQuery = useQuery({
    queryKey: ["genome-templates", USER_ID],
    queryFn: () => getGenomeTemplates(USER_ID),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createGenomeTemplate(USER_ID, {
        name: name.trim(),
        description: description.trim() || null,
        species_group: speciesGroup.trim(),
      }),
    onSuccess: async () => {
      setName("");
      setDescription("");
      setSpeciesGroup("default_species");
      await queryClient.invalidateQueries({ queryKey: ["genome-templates", USER_ID] });
    },
  });

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <Link to="/">← К симуляциям</Link>
      </div>

      <h1>Шаблоны генома</h1>

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 16,
          background: "#fff",
          marginBottom: 24,
          display: "grid",
          gap: 8,
          maxWidth: 500,
        }}
      >
        <h3 style={{ marginTop: 0 }}>Создать шаблон</h3>

        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Название"
        />
        <input
          value={speciesGroup}
          onChange={(e) => setSpeciesGroup(e.target.value)}
          placeholder="Species group"
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Описание"
          rows={4}
        />

        <button
          disabled={createMutation.isPending || !name.trim() || !speciesGroup.trim()}
          onClick={() => createMutation.mutate()}
        >
          Создать шаблон
        </button>
      </div>

      {templatesQuery.isLoading && <p>Загрузка...</p>}
      {templatesQuery.isError && <p>Ошибка загрузки шаблонов.</p>}

      <div style={{ display: "grid", gap: 12 }}>
        {templatesQuery.data?.map((template) => (
          <div
            key={template.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: 16,
              background: "#fff",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
              <div>
                <div>
                  <b>{template.name}</b>{" "}
                  {template.is_builtin && (
                    <span style={{ color: "#1d4ed8" }}>(built-in)</span>
                  )}
                </div>
                <div>species group: {template.species_group}</div>
                {template.description && <div>{template.description}</div>}
              </div>

              <div>
                <Link to={`/genome-templates/${template.id}`}>Открыть</Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}