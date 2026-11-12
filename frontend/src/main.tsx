import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "@ant-design/v5-patch-for-react-19";
import "antd/dist/reset.css";
import "./styles.css";
import App from "./app/App";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      // Dữ liệu sau thao tác ghi luôn được invalidate/refetch; staleTime chỉ tránh gọi lại khi chuyển trang.
      staleTime: 15_000,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);