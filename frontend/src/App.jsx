import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import RtlLayout from "layouts/rtl";
import AdminLayout from "layouts/admin";
import AuthLayout from "layouts/auth";
import AuthInitializer from "components/auth/AuthInitializer";
import AdminCompanyLayout from "layouts/admin-company";

const App = () => {
  return (
    <AuthInitializer>
      <Routes>
        <Route path="auth/*" element={<AuthLayout />} />
        <Route path="admin/*" element={<AdminLayout />} />
        <Route path="admin-company/*" element={<AdminCompanyLayout />} />
        <Route path="rtl/*" element={<RtlLayout />} />
        <Route path="/" element={<Navigate to="/admin" replace />} />
      </Routes>
    </AuthInitializer>
  );
};

export default App;
