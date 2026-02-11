import React from "react";
import { Navigate } from "react-router-dom";
import { useAppSelector } from "../hooks";

interface PrivateRouteProps {
  children: React.ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { userInfo } = useAppSelector((state) => state.auth);
  return userInfo ? <>{children}</> : <Navigate to="/login" replace />;
};

export default PrivateRoute;
