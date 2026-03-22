type Props = {
  onStart: () => void;
  onStep: () => void;
  onRun: () => void;
  onPause: () => void;
  onStop: () => void;
  isBusy?: boolean;
};

export function SimulationControls({
  onStart,
  onStep,
  onRun,
  onPause,
  onStop,
  isBusy = false,
}: Props) {
  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
      <button onClick={onStart} disabled={isBusy}>Start</button>
      <button onClick={onStep} disabled={isBusy}>Step</button>
      <button onClick={onRun} disabled={isBusy}>Run</button>
      <button onClick={onPause} disabled={isBusy}>Pause</button>
      <button onClick={onStop} disabled={isBusy}>Stop</button>
    </div>
  );
}