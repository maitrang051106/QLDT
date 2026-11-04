import api, { requireItems } from "../../shared/api/client";
import type {
  InvoiceGenerateRequest,
  InvoiceGenerateResult,
  InvoiceStatus,
  ItemList,
  Page,
  PaymentCreateRequest,
  Receipt,
  TuitionInstallment,
  TuitionInstallmentsPutRequest,
  TuitionInvoice,
  TuitionRate,
  TuitionRateCreateRequest,
  TuitionRateUpdateRequest,
  TuitionSummary,
} from "../../shared/api/api-types";

export async function fetchMyTuition(semesterId?: number): Promise<TuitionInvoice> {
  return (
    await api.get<TuitionInvoice>("/tuition/me", {
      params: semesterId ? { semesterId } : undefined,
    })
  ).data;
}

export async function submitTuitionPayment(request: PaymentCreateRequest): Promise<Receipt> {
  return (await api.post<Receipt>("/tuition/me/payments", request)).data;
}

export async function fetchMyReceipts(semesterId?: number): Promise<Receipt[]> {
  const response = await api.get<ItemList<Receipt>>("/receipts/me", {
    params: semesterId ? { semesterId } : undefined,
  });
  return requireItems<Receipt>(response.data);
}

export async function fetchReceiptDetail(receiptId: number): Promise<Receipt> {
  return (await api.get<Receipt>(`/receipts/${receiptId}`)).data;
}

export async function downloadReceiptPdf(receiptId: number, receiptNo: string): Promise<void> {
  const response = await api.get<Blob>(`/receipts/${receiptId}/pdf`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${receiptNo || `receipt-${receiptId}`}.pdf`;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

export async function fetchTuitionRates(semesterId?: number): Promise<TuitionRate[]> {
  const response = await api.get<ItemList<TuitionRate>>("/admin/tuition-rates", {
    params: semesterId ? { semesterId } : undefined,
  });
  return requireItems<TuitionRate>(response.data);
}

export async function createTuitionRate(request: TuitionRateCreateRequest): Promise<TuitionRate> {
  return (await api.post<TuitionRate>("/admin/tuition-rates", request)).data;
}

export async function updateTuitionRate(
  rateId: number,
  request: TuitionRateUpdateRequest,
): Promise<TuitionRate> {
  return (await api.put<TuitionRate>(`/admin/tuition-rates/${rateId}`, request)).data;
}

export async function deleteTuitionRate(rateId: number): Promise<void> {
  await api.delete(`/admin/tuition-rates/${rateId}`);
}

export async function fetchTuitionInstallments(semesterId: number): Promise<TuitionInstallment[]> {
  const response = await api.get<ItemList<TuitionInstallment>>("/admin/tuition/installments", {
    params: { semesterId },
  });
  return requireItems<TuitionInstallment>(response.data);
}

export async function configureTuitionInstallments(
  request: TuitionInstallmentsPutRequest,
): Promise<TuitionInstallment[]> {
  const response = await api.put<ItemList<TuitionInstallment>>(
    "/admin/tuition/installments",
    request,
  );
  return requireItems<TuitionInstallment>(response.data);
}

export async function generateTuitionInvoices(
  request: InvoiceGenerateRequest,
): Promise<InvoiceGenerateResult> {
  return (await api.post<InvoiceGenerateResult>("/admin/tuition/invoices/generate", request)).data;
}

export async function fetchAdminTuitionInvoices(params: {
  semesterId: number;
  status?: InvoiceStatus;
  studentCode?: string;
  page?: number;
  size?: number;
}): Promise<Page<TuitionInvoice>> {
  return (await api.get<Page<TuitionInvoice>>("/admin/tuition/invoices", { params })).data;
}

export async function fetchTuitionSummary(semesterId: number): Promise<TuitionSummary> {
  return (
    await api.get<TuitionSummary>("/admin/tuition/reports/summary", {
      params: { semesterId },
    })
  ).data;
}
