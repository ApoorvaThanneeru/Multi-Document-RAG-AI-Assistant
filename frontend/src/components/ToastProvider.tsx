"use client";

import { Toaster } from "react-hot-toast";

export default function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          borderRadius: "10px",
          background: "#1e293b",
          color: "#f1f5f9",
          fontSize: "14px",
        },
      }}
    />
  );
}
