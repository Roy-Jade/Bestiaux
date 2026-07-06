import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { isApiError, useAuth } from "../../../stores/AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const mutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: () => navigate("/creature", { replace: true }),
  });

  return (
    <main className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Bestiaux</h1>
        <p className="auth-subtitle">Connexion</p>

        <form
          className="auth-form"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}
        >
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
              autoComplete="current-password"
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
            {mutation.isPending ? "Connexion…" : "Se connecter"}
          </button>
        </form>

        <p className="auth-link">
          Pas encore de compte ? <Link to="/register">S&apos;inscrire</Link>
        </p>
      </div>
    </main>
  );
}
