export const handleError = (err: any, custom_error_msg: string): string => {
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join(", ");
  return custom_error_msg;
};
