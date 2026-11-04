import { useState } from "react";
import { CalendarOutlined, DownloadOutlined, DollarOutlined, FileTextOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert,
  App,
  Button,
  Card,
  Empty,
  Form,
  InputNumber,
  Modal,
  Select,
  Space,
  Spin,
  Statistic,
  Table,
  Tabs,
  Tag,
  Typography,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import type {
  InvoiceStatus,
  Receipt,
  TuitionInstallment,
  TuitionInvoiceItem,
} from "../../shared/api/api-types";
import { readApiError } from "../../shared/api/client";
import { fetchCurrentSemester } from "../catalog/catalogApi";
import {
  downloadReceiptPdf,
  fetchMyReceipts,
  fetchMyTuition,
  submitTuitionPayment,
} from "./tuitionApi";

const statusLabels: Record<InvoiceStatus, { label: string; color: string }> = {
  UNPAID: { label: "Chưa nộp", color: "warning" },
  PARTIALLY_PAID: { label: "Nộp một phần", color: "processing" },
  PAID: { label: "Đã hoàn tất", color: "success" },
  CANCELLED: { label: "Đã hủy", color: "default" },
};

function formatVnd(amount: number): string {
  return `${amount.toLocaleString("vi-VN")} ₫`;
}

function errorText(error: unknown): string {
  const body = readApiError(error);
  const details = body?.details?.map((item) => item.message).filter(Boolean).join("; ");
  return details || body?.message || "Thao tác chưa thành công. Vui lòng thử lại.";
}

export default function StudentTuitionPage() {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [payModalOpen, setPayModalOpen] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt>();

  const semesterQuery = useQuery({
    queryKey: ["semesters", "current"],
    queryFn: fetchCurrentSemester,
  });
  const semesterId = semesterQuery.data?.id;

  const tuitionQuery = useQuery({
    queryKey: ["tuition", "me", semesterId],
    enabled: semesterId !== undefined,
    queryFn: () => fetchMyTuition(semesterId),
  });

  const receiptsQuery = useQuery({
    queryKey: ["receipts", "me", semesterId],
    enabled: semesterId !== undefined,
    queryFn: () => fetchMyReceipts(semesterId),
  });

  const paymentMutation = useMutation({
    mutationFn: (values: { amount: number; installmentId?: number | null }) =>
      submitTuitionPayment({
        amount: values.amount,
        installmentId: values.installmentId ?? null,
        idempotencyKey:
          typeof crypto !== "undefined" && "randomUUID" in crypto
            ? crypto.randomUUID()
            : `pay-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
      }),
    onSuccess: async (receipt) => {
      setPayModalOpen(false);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["tuition", "me"] }),
        queryClient.invalidateQueries({ queryKey: ["receipts", "me"] }),
      ]);
      setSelectedReceipt(receipt);
      message.success(`Nộp học phí thành công. Đã phát hành biên lai ${receipt.receiptNo}.`);
    },
    onError: (error: unknown) => message.error(errorText(error)),
  });

  const pdfMutation = useMutation({
    mutationFn: ({ id, receiptNo }: { id: number; receiptNo: string }) =>
      downloadReceiptPdf(id, receiptNo),
    onError: (error: unknown) => message.error(errorText(error)),
  });

  if (semesterQuery.isLoading || tuitionQuery.isLoading) {
    return (
      <div className="feature-loading">
        <Spin />
      </div>
    );
  }

  if (semesterQuery.isError || tuitionQuery.isError) {
    return (
      <Alert
        type="error"
        showIcon
        message="Không tải được thông tin học phí."
        description={errorText(tuitionQuery.error ?? semesterQuery.error)}
        action={
          <Button size="small" onClick={() => void tuitionQuery.refetch()}>
            Thử lại
          </Button>
        }
      />
    );
  }

  const invoice = tuitionQuery.data;
  const receipts = receiptsQuery.data ?? [];
  const statusMeta = invoice ? statusLabels[invoice.status] : statusLabels.UNPAID;

  const itemColumns: ColumnsType<TuitionInvoiceItem> = [
    {
      title: "Mã môn",
      dataIndex: "subjectCode",
      key: "subjectCode",
      width: 130,
      render: (code: string) => <strong>{code}</strong>,
    },
    { title: "Tên môn học", dataIndex: "subjectName", key: "subjectName" },
    { title: "Số TC", dataIndex: "credits", key: "credits", width: 85, align: "center" },
    {
      title: "TCHP",
      dataIndex: "tuitionCredits",
      key: "tuitionCredits",
      width: 90,
      align: "center",
    },
    {
      title: "Đơn giá / TCHP",
      dataIndex: "pricePerCredit",
      key: "pricePerCredit",
      width: 150,
      align: "right",
      render: (value: number) => formatVnd(value),
    },
    {
      title: "Thành tiền",
      dataIndex: "amount",
      key: "amount",
      width: 160,
      align: "right",
      render: (value: number) => <strong>{formatVnd(value)}</strong>,
    },
  ];

  const installmentColumns: ColumnsType<TuitionInstallment> = [
    { title: "Đợt", dataIndex: "installmentOrder", key: "installmentOrder", width: 70, align: "center" },
    { title: "Tên đợt nộp", dataIndex: "name", key: "name" },
    { title: "Hạn nộp", dataIndex: "dueDate", key: "dueDate", width: 130 },
    {
      title: "Mức phân bổ",
      key: "basis",
      width: 140,
      render: (_, row) =>
        row.percentage != null ? `${row.percentage}%` : formatVnd(row.fixedAmount ?? 0),
    },
    {
      title: "Số tiền đợt này",
      dataIndex: "allocatedAmount",
      key: "allocatedAmount",
      width: 160,
      align: "right",
      render: (value: number | null | undefined) => formatVnd(value ?? 0),
    },
    {
      title: "Trạng thái",
      dataIndex: "status",
      key: "status",
      width: 130,
      render: (status: TuitionInstallment["status"]) => {
        if (status === "PAID") return <Tag color="success">Đã nộp đủ</Tag>;
        if (status === "OVERDUE") return <Tag color="error">Quá hạn</Tag>;
        return <Tag color="processing">Đang chờ nộp</Tag>;
      },
    },
  ];

  const receiptColumns: ColumnsType<Receipt> = [
    {
      title: "Số biên lai",
      dataIndex: "receiptNo",
      key: "receiptNo",
      width: 170,
      render: (no: string) => <strong>{no}</strong>,
    },
    {
      title: "Số tiền thu",
      dataIndex: "amount",
      key: "amount",
      width: 160,
      align: "right",
      render: (value: number) => <strong>{formatVnd(value)}</strong>,
    },
    { title: "Bằng chữ", dataIndex: "amountInWords", key: "amountInWords" },
    { title: "Thời điểm cấp", dataIndex: "issuedAt", key: "issuedAt", width: 190 },
    {
      title: "Thao tác",
      key: "actions",
      width: 210,
      render: (_, row) => (
        <Space>
          <Button
            size="small"
            icon={<FileTextOutlined />}
            onClick={() => setSelectedReceipt(row)}
          >
            Xem
          </Button>
          <Button
            size="small"
            type="primary"
            icon={<DownloadOutlined />}
            loading={pdfMutation.isPending && pdfMutation.variables?.id === row.id}
            onClick={() => pdfMutation.mutate({ id: row.id, receiptNo: row.receiptNo })}
          >
            Tải PDF
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <div className="feature-toolbar" style={{ justifyContent: "space-between" }}>
        <Tag icon={<CalendarOutlined />} color="processing">
          Học kỳ hiện tại:{" "}
          {semesterQuery.data
            ? `${semesterQuery.data.semesterCode} · ${semesterQuery.data.name}`
            : "2026.1"}
        </Tag>
        <Space>
          <Tag color={statusMeta.color}>{statusMeta.label}</Tag>
          <Button
            type="primary"
            icon={<DollarOutlined />}
            disabled={!invoice || invoice.balance <= 0}
            onClick={() => setPayModalOpen(true)}
          >
            Nộp học phí
          </Button>
        </Space>
      </div>

      {invoice?.isStale && (
        <Alert
          type="warning"
          showIcon
          message="Danh sách lớp đăng ký của bạn đã thay đổi sau khi đã phát sinh giao dịch nộp tiền."
          description="Liên hệ Phòng Đào tạo để quyết toán lại hóa đơn nếu có chênh lệch tín chỉ."
        />
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 12,
        }}
      >
        <Card>
          <Statistic title="Tổng học phí" value={formatVnd(invoice?.totalTuition ?? 0)} />
        </Card>
        <Card>
          <Statistic title="Phải nộp" value={formatVnd(invoice?.amountDue ?? 0)} />
        </Card>
        <Card>
          <Statistic title="Đã nộp" value={formatVnd(invoice?.amountPaid ?? 0)} />
        </Card>
        <Card>
          <Statistic
            title="Còn nợ"
            value={formatVnd(invoice?.balance ?? 0)}
            valueStyle={{ color: (invoice?.balance ?? 0) > 0 ? "#a6192e" : "#38745e" }}
          />
        </Card>
      </div>

      <Tabs
        items={[
          {
            key: "items",
            label: `Chi tiết môn học (${invoice?.items?.length ?? 0})`,
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <Table<TuitionInvoiceItem>
                  rowKey="id"
                  size="small"
                  columns={itemColumns}
                  dataSource={invoice?.items ?? []}
                  pagination={false}
                  scroll={{ x: 760 }}
                  locale={{
                    emptyText: (
                      <Empty description="Chưa có môn học phát sinh học phí trong học kỳ này." />
                    ),
                  }}
                />
              </Card>
            ),
          },
          {
            key: "installments",
            label: `Đợt nộp (${invoice?.installments?.length ?? 0})`,
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <Table<TuitionInstallment>
                  rowKey="id"
                  size="small"
                  columns={installmentColumns}
                  dataSource={invoice?.installments ?? []}
                  pagination={false}
                  scroll={{ x: 680 }}
                  locale={{ emptyText: <Empty description="Chưa cấu hình đợt nộp." /> }}
                />
              </Card>
            ),
          },
          {
            key: "receipts",
            label: `Biên lai điện tử (${receipts.length})`,
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <Table<Receipt>
                  rowKey="id"
                  size="small"
                  columns={receiptColumns}
                  dataSource={receipts}
                  pagination={{ pageSize: 10 }}
                  scroll={{ x: 760 }}
                  locale={{ emptyText: <Empty description="Chưa có biên lai thanh toán." /> }}
                />
              </Card>
            ),
          },
        ]}
      />

      <Modal
        title="Nộp học phí trực tuyến"
        open={payModalOpen}
        onCancel={() => setPayModalOpen(false)}
        footer={null}
        destroyOnHidden
      >
        <Form<{ amount: number; installmentId?: number | null }>
          layout="vertical"
          initialValues={{
            amount: invoice?.balance ?? 0,
            installmentId: invoice?.installments?.[0]?.id ?? null,
          }}
          onFinish={(values) => paymentMutation.mutate(values)}
        >
          <Form.Item label="Chọn đợt nộp (tùy chọn)" name="installmentId">
            <Select
              allowClear
              placeholder="Nộp chung vào số dư hóa đơn"
              options={(invoice?.installments ?? []).map((inst) => ({
                value: inst.id,
                label: `${inst.name} · ${formatVnd(inst.allocatedAmount ?? 0)}`,
              }))}
            />
          </Form.Item>
          <Form.Item
            label="Số tiền nộp (VND)"
            name="amount"
            rules={[{ required: true, message: "Nhập số tiền cần nộp" }]}
          >
            <InputNumber
              min={1}
              max={invoice?.balance ?? undefined}
              step={50000}
              style={{ width: "100%" }}
            />
          </Form.Item>
          <Alert
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
            message={`Số tiền còn phải nộp tối đa: ${formatVnd(invoice?.balance ?? 0)}`}
          />
          <Button type="primary" htmlType="submit" block loading={paymentMutation.isPending}>
            Xác nhận thanh toán &amp; xuất biên lai
          </Button>
        </Form>
      </Modal>

      <Modal
        title={selectedReceipt ? `Biên lai điện tử · ${selectedReceipt.receiptNo}` : "Chi tiết biên lai"}
        open={Boolean(selectedReceipt)}
        onCancel={() => setSelectedReceipt(undefined)}
        footer={
          selectedReceipt ? (
            <Space>
              <Button onClick={() => setSelectedReceipt(undefined)}>Đóng</Button>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                loading={pdfMutation.isPending}
                onClick={() =>
                  pdfMutation.mutate({
                    id: selectedReceipt.id,
                    receiptNo: selectedReceipt.receiptNo,
                  })
                }
              >
                Tải PDF biên lai
              </Button>
            </Space>
          ) : null
        }
      >
        {selectedReceipt && (
          <div style={{ display: "grid", gap: 8 }}>
            <Typography.Text>
              <strong>Số biên lai:</strong> {selectedReceipt.receiptNo}
            </Typography.Text>
            <Typography.Text>
              <strong>Sinh viên:</strong> {selectedReceipt.studentName} ({selectedReceipt.studentCode})
            </Typography.Text>
            <Typography.Text>
              <strong>Số tiền thu:</strong> {formatVnd(selectedReceipt.amount)}
            </Typography.Text>
            <Typography.Text>
              <strong>Viết bằng chữ:</strong> {selectedReceipt.amountInWords ?? "—"}
            </Typography.Text>
            <Typography.Text>
              <strong>Thời điểm phát hành:</strong> {selectedReceipt.issuedAt}
            </Typography.Text>
          </div>
        )}
      </Modal>
    </div>
  );
}
