import { useState } from "react";
import { CalendarOutlined, PlusOutlined, SyncOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert,
  App,
  Button,
  Card,
  Empty,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Spin,
  Statistic,
  Table,
  Tabs,
  Tag,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import type {
  InvoiceStatus,
  TuitionInstallment,
  TuitionInvoice,
  TuitionRate,
  TuitionRateCreateRequest,
} from "../../shared/api/api-types";
import { readApiError } from "../../shared/api/client";
import { fetchCurrentSemester } from "../catalog/catalogApi";
import {
  createTuitionRate,
  deleteTuitionRate,
  fetchAdminTuitionInvoices,
  fetchTuitionInstallments,
  fetchTuitionRates,
  fetchTuitionSummary,
  generateTuitionInvoices,
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

export default function AdminTuitionPage() {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [invoicePage, setInvoicePage] = useState(1);
  const [studentCode, setStudentCode] = useState("");
  const [statusFilter, setStatusFilter] = useState<InvoiceStatus>();
  const [rateModalOpen, setRateModalOpen] = useState(false);

  const semesterQuery = useQuery({
    queryKey: ["semesters", "current"],
    queryFn: fetchCurrentSemester,
  });
  const semesterId = semesterQuery.data?.id;

  const summaryQuery = useQuery({
    queryKey: ["tuition", "summary", semesterId],
    enabled: semesterId !== undefined,
    queryFn: () => fetchTuitionSummary(semesterId!),
  });

  const invoicesQuery = useQuery({
    queryKey: ["tuition", "invoices", semesterId, invoicePage, statusFilter, studentCode],
    enabled: semesterId !== undefined,
    queryFn: () =>
      fetchAdminTuitionInvoices({
        semesterId: semesterId!,
        status: statusFilter,
        studentCode: studentCode.trim() || undefined,
        page: invoicePage,
        size: 10,
      }),
  });

  const ratesQuery = useQuery({
    queryKey: ["tuition", "rates", semesterId],
    enabled: semesterId !== undefined,
    queryFn: () => fetchTuitionRates(semesterId),
  });

  const installmentsQuery = useQuery({
    queryKey: ["tuition", "installments", semesterId],
    enabled: semesterId !== undefined,
    queryFn: () => fetchTuitionInstallments(semesterId!),
  });

  const generateMutation = useMutation({
    mutationFn: () => generateTuitionInvoices({ semesterId: semesterId! }),
    onSuccess: async (result) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["tuition", "summary"] }),
        queryClient.invalidateQueries({ queryKey: ["tuition", "invoices"] }),
      ]);
      message.success(result.message);
    },
    onError: (error: unknown) => message.error(errorText(error)),
  });

  const createRateMutation = useMutation({
    mutationFn: (values: Omit<TuitionRateCreateRequest, "semesterId">) =>
      createTuitionRate({ ...values, semesterId: semesterId! }),
    onSuccess: async () => {
      setRateModalOpen(false);
      await queryClient.invalidateQueries({ queryKey: ["tuition", "rates"] });
      message.success("Đã thêm đơn giá học phí.");
    },
    onError: (error: unknown) => message.error(errorText(error)),
  });

  const deleteRateMutation = useMutation({
    mutationFn: deleteTuitionRate,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["tuition", "rates"] });
      message.success("Đã xóa đơn giá học phí.");
    },
    onError: (error: unknown) => message.error(errorText(error)),
  });

  if (semesterQuery.isLoading) {
    return (
      <div className="feature-loading">
        <Spin />
      </div>
    );
  }

  if (semesterQuery.isError) {
    return (
      <Alert
        type="error"
        showIcon
        message="Không tải được thông tin học kỳ."
        action={
          <Button size="small" onClick={() => void semesterQuery.refetch()}>
            Thử lại
          </Button>
        }
      />
    );
  }

  const summary = summaryQuery.data;

  const invoiceColumns: ColumnsType<TuitionInvoice> = [
    {
      title: "MSSV",
      dataIndex: "studentCode",
      key: "studentCode",
      width: 120,
      render: (value: string | null) => <strong>{value ?? "—"}</strong>,
    },
    { title: "Họ và tên", dataIndex: "studentName", key: "studentName" },
    { title: "Khóa", dataIndex: "cohort", key: "cohort", width: 80 },
    { title: "Ngành", dataIndex: "major", key: "major", width: 170 },
    {
      title: "Tổng học phí",
      dataIndex: "totalTuition",
      key: "totalTuition",
      width: 150,
      align: "right",
      render: (val: number) => formatVnd(val),
    },
    {
      title: "Phải nộp",
      dataIndex: "amountDue",
      key: "amountDue",
      width: 150,
      align: "right",
      render: (val: number) => <strong>{formatVnd(val)}</strong>,
    },
    {
      title: "Đã nộp",
      dataIndex: "amountPaid",
      key: "amountPaid",
      width: 150,
      align: "right",
      render: (val: number) => formatVnd(val),
    },
    {
      title: "Còn nợ",
      dataIndex: "balance",
      key: "balance",
      width: 150,
      align: "right",
      render: (val: number) => <strong>{formatVnd(val)}</strong>,
    },
    {
      title: "Trạng thái",
      dataIndex: "status",
      key: "status",
      width: 130,
      render: (status: InvoiceStatus, row) => (
        <Space size={4}>
          <Tag color={statusLabels[status]?.color}>{statusLabels[status]?.label ?? status}</Tag>
          {row.isStale && <Tag color="orange">Cần tính lại</Tag>}
        </Space>
      ),
    },
  ];

  const rateColumns: ColumnsType<TuitionRate> = [
    {
      title: "Đối tượng Khóa",
      dataIndex: "cohort",
      key: "cohort",
      width: 130,
      render: (val: string | null) => val || <Tag>Mọi khóa</Tag>,
    },
    {
      title: "Ngành áp dụng",
      dataIndex: "major",
      key: "major",
      render: (val: string | null) => val || <Tag>Mọi ngành</Tag>,
    },
    {
      title: "Đơn giá / TCHP",
      dataIndex: "pricePerCredit",
      key: "pricePerCredit",
      width: 160,
      align: "right",
      render: (val: number) => <strong>{formatVnd(val)}</strong>,
    },
    {
      title: "Hiệu lực",
      key: "effective",
      width: 210,
      render: (_, row) => `${row.effectiveFrom} → ${row.effectiveTo ?? "Không giới hạn"}`,
    },
    { title: "Mô tả", dataIndex: "description", key: "description" },
    {
      title: "Thao tác",
      key: "actions",
      width: 100,
      render: (_, row) => (
        <Popconfirm
          title="Xóa đơn giá này?"
          okText="Xóa"
          cancelText="Hủy"
          onConfirm={() => deleteRateMutation.mutateAsync(row.id)}
        >
          <Button danger size="small">
            Xóa
          </Button>
        </Popconfirm>
      ),
    },
  ];

  const installmentColumns: ColumnsType<TuitionInstallment> = [
    { title: "Đợt", dataIndex: "installmentOrder", key: "installmentOrder", width: 80, align: "center" },
    { title: "Tên đợt nộp", dataIndex: "name", key: "name" },
    { title: "Hạn nộp", dataIndex: "dueDate", key: "dueDate", width: 150 },
    {
      title: "Tỷ lệ / Mức thu",
      key: "basis",
      width: 160,
      render: (_, row) =>
        row.percentage != null ? `${row.percentage}%` : formatVnd(row.fixedAmount ?? 0),
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
        <Button
          type="primary"
          icon={<SyncOutlined />}
          loading={generateMutation.isPending}
          onClick={() => generateMutation.mutate()}
        >
          Tính / cập nhật hóa đơn toàn kỳ
        </Button>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 12,
        }}
      >
        <Card>
          <Statistic title="Tổng số hóa đơn" value={summary?.totalInvoices ?? 0} />
        </Card>
        <Card>
          <Statistic title="Tổng phải thu" value={formatVnd(summary?.totalAmountDue ?? 0)} />
        </Card>
        <Card>
          <Statistic title="Tổng đã thu" value={formatVnd(summary?.totalAmountPaid ?? 0)} />
        </Card>
        <Card>
          <Statistic
            title="Tổng còn nợ"
            value={formatVnd(summary?.totalBalance ?? 0)}
            valueStyle={{ color: (summary?.totalBalance ?? 0) > 0 ? "#a6192e" : "#38745e" }}
          />
        </Card>
      </div>

      <Tabs
        items={[
          {
            key: "invoices",
            label: "Hóa đơn sinh viên",
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <div style={{ padding: 16, display: "flex", gap: 12, flexWrap: "wrap" }}>
                  <Input.Search
                    allowClear
                    placeholder="Tìm theo MSSV"
                    style={{ maxWidth: 260 }}
                    value={studentCode}
                    onChange={(event) => {
                      setStudentCode(event.target.value);
                      setInvoicePage(1);
                    }}
                  />
                  <Select
                    allowClear
                    placeholder="Lọc trạng thái"
                    style={{ minWidth: 180 }}
                    value={statusFilter}
                    options={Object.entries(statusLabels).map(([value, meta]) => ({
                      value,
                      label: meta.label,
                    }))}
                    onChange={(value) => {
                      setStatusFilter(value);
                      setInvoicePage(1);
                    }}
                  />
                </div>
                <Table<TuitionInvoice>
                  rowKey="id"
                  size="small"
                  loading={invoicesQuery.isLoading}
                  columns={invoiceColumns}
                  dataSource={invoicesQuery.data?.items ?? []}
                  scroll={{ x: 1000 }}
                  pagination={{
                    current: invoicePage,
                    pageSize: 10,
                    total: invoicesQuery.data?.totalItems ?? 0,
                    showSizeChanger: false,
                  }}
                  onChange={(pagination) => setInvoicePage(pagination.current ?? 1)}
                  locale={{ emptyText: <Empty description="Chưa có hóa đơn học phí." /> }}
                />
              </Card>
            ),
          },
          {
            key: "rates",
            label: `Đơn giá học phí (${ratesQuery.data?.length ?? 0})`,
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <div style={{ padding: 16, display: "flex", justifyContent: "flex-end" }}>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => setRateModalOpen(true)}
                  >
                    Thêm đơn giá
                  </Button>
                </div>
                <Table<TuitionRate>
                  rowKey="id"
                  size="small"
                  loading={ratesQuery.isLoading}
                  columns={rateColumns}
                  dataSource={ratesQuery.data ?? []}
                  pagination={false}
                  scroll={{ x: 860 }}
                />
              </Card>
            ),
          },
          {
            key: "installments",
            label: `Đợt nộp (${installmentsQuery.data?.length ?? 0})`,
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <Table<TuitionInstallment>
                  rowKey="id"
                  size="small"
                  loading={installmentsQuery.isLoading}
                  columns={installmentColumns}
                  dataSource={installmentsQuery.data ?? []}
                  pagination={false}
                />
              </Card>
            ),
          },
        ]}
      />

      <Modal
        title="Thêm đơn giá học phí"
        open={rateModalOpen}
        onCancel={() => setRateModalOpen(false)}
        footer={null}
        destroyOnHidden
      >
        <Form<Omit<TuitionRateCreateRequest, "semesterId">>
          layout="vertical"
          onFinish={(values) => createRateMutation.mutate(values)}
        >
          <Form.Item label="Khóa áp dụng (bỏ trống = mọi khóa)" name="cohort">
            <Input placeholder="Ví dụ: K66" />
          </Form.Item>
          <Form.Item label="Ngành áp dụng (bỏ trống = mọi ngành)" name="major">
            <Input placeholder="Ví dụ: Công nghệ thông tin" />
          </Form.Item>
          <Form.Item
            label="Đơn giá 1 TCHP (VND)"
            name="pricePerCredit"
            rules={[{ required: true, message: "Nhập đơn giá" }]}
          >
            <InputNumber min={1000} step={50000} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Mô tả" name="description">
            <Input />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={createRateMutation.isPending}>
            Lưu đơn giá
          </Button>
        </Form>
      </Modal>
    </div>
  );
}
