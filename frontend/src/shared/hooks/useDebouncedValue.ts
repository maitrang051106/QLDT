import { useEffect, useState } from "react";

/** Trì hoãn giá trị thay đổi nhanh (ví dụ ô tìm kiếm) để giảm số request gọi API. */
export function useDebouncedValue<T>(value: T, delayMs = 350): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(timer);
  }, [value, delayMs]);
  return debounced;
}
