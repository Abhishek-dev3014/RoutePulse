"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="error-state">
      <h1>Something interrupted the workspace.</h1>
      <p>Your saved experiments are still in the database.</p>
      <button onClick={reset}>Try again</button>
    </main>
  );
}
