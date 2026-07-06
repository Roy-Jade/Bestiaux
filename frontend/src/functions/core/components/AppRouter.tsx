import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "../../../stores/AuthContext";
import { BreedingPage } from "../../breeding/pages/BreedingPage";
import { CompendiumPage } from "../../compendium/pages/CompendiumPage";
import { CreaturePage } from "../../creature/pages/CreaturePage";
import { TrainingPage } from "../../training/pages/TrainingPage";
import { AppLayout } from "./AppLayout";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";
import { RequireAuth } from "./RequireAuth";

export function AppRouter() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="loading-screen">Chargement…</div>;
  }

  return (
    <Routes>
      {/* Routes publiques */}
      <Route path="/login" element={user ? <Navigate to="/creature" replace /> : <LoginPage />} />
      <Route
        path="/register"
        element={user ? <Navigate to="/creature" replace /> : <RegisterPage />}
      />

      {/* Routes privées — avec layout + tab bar */}
      <Route
        path="/"
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/creature" replace />} />
        <Route path="creature" element={<CreaturePage />} />
        <Route path="training" element={<TrainingPage />} />
        <Route path="breeding" element={<BreedingPage />} />
        <Route path="compendium" element={<CompendiumPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/creature" replace />} />
    </Routes>
  );
}
