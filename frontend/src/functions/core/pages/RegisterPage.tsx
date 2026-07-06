import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { isApiError, useAuth } from "../../../stores/AuthContext";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const mutation = useMutation({
    mutationFn: () => register(username, email, password),
    onSuccess: () => navigate("/creature", { replace: true }),
  });

  return (
    <main className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Bestiaux</h1>
        <p className="auth-subtitle">Créer un compte</p>

        <form
          className="auth-form"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}
        >
          <div className="form-group">
            <label htmlFor="username">Pseudo</label>
            <input
              id="username"
              className="form-input"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              className="form-input"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              className="form-input"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {mutation.error !== null && (
            <p className="form-error">
              {isApiError(mutation.error) ? mutation.error.detail : "Erreur inattendue"}
            </p>
          )}

          <button className="btn-primary" type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "Inscription…" : "S'inscrire"}
          </button>
        </form>

        <p className="auth-link">
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </p>
      </div>
    </main>
  );
}
