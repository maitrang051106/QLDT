import { useState } from "react";
import { CalendarOutlined, SearchOutlined } from "@ant-design/icons";
import {
  Alert,
  App,
  Button,
  Card,
  Empty,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Spin,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";
import type { ColumnsType, TablePaginationConfig } from "antd/es/table";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Section, SectionUpdateRequest } from "../../shared/api/api-types";
import { readApiError } from "../../shared/api/client";
import {
  fetchCurrentSemester,
  fetchLookups,
  fetchSections,
  updateSection,
} from "../catalog/catalogApi";

const PAGE_SIZE = 10;
const DAY_OPTIONS = [2, 3, 4, 5, 6, 7, 8].map((value) => ({
  value,
  label: value === 8 ? "Chủ nhật" : `Thứ ${value}`,
}));

function scheduleLabel(section: Section) {
  const day =
    DAY_OPTIONS.find((option) => option.value === section.dayOfWeek)?.label ??
    `Thứ ${section.dayOfWeek}`;
  return `${day} · Tiết ${section.startPeriod}-${section.endPeriod} · Tuần ${section.startWeek}-${section.endWeek}`;
}

function updateErrorMessage(error: unknown) {
  const body = readApiError(error);
  if (body?.error === "SCHEDULE_CONFLICT") {
    const reasons = body.details.map((detail) => detail.message).filter(Boolean).join("; ");
    return reasons || "Giảng viên hoặc phòng đã được phân công trong khung giờ này.";
  }
  if (body?.details?.length)
    return body.details.map((detail) => detail.message).filter(Boolean).join("; ");
  return body?.message || "Không thể lưu thay đổi. Vui lòng thử lại.";
}

export default function AdminTimetablePage() {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<number>();
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState("");
  const lookupsQuery = useQuery({ queryKey: ["catalog", "lookups"], queryFn: fetchLookups });
  const semesterQuery = useQuery({ queryKey: ["semesters", "current"], queryFn: fetchCurrentSemester });
  const semesterId = semesterQuery.data?.id;
  const sectionsQuery = useQuery({
    queryKey: ["sections", "admin", semesterId, page, keyword],
    enabled: semesterId !== undefined,
    queryFn: () =>
      fetchSections({
        semesterId: semesterId!,
        page,
        size: PAGE_SIZE,
        keyword: keyword || undefined,
      }),
  });
  const sections = sectionsQuery.data?.items ?? [];
  const selected = sections.find((section) => section.id === selectedId) ?? sections[0];

  const saveMutation = useMutation({
    mutationFn: ({ id, body }: { id: number; body: SectionUpdateRequest }) =>
      updateSection(id, body),
    onSuccess: async (updated) => {
      await queryClient.invalidateQueries({ queryKey: ["sections"] });
      setSelectedId(updated.id);
      message.success("Lịch học và phân công đã được cập nhật.");
    },
    onError: (error: unknown) => message.error(updateErrorMessage(error)),
  });

  const columns: ColumnsType<Section> = [
    {
      title: "Lớp học phần",
      dataIndex: "sectionCode",
      key: "sectionCode",
      width: 150,
      render: (code: string, record) => (
        <Typography.Link onClick={() => setSelectedId(record.id)}>{code}</Typography.Link>
      ),
    },
    {
      title: "Môn học",
      key: "subject",
      width: 260,
      render: (_, record) => (
        <Space direction="vertical" size={0} style={{ width: "100%", minWidth: 0 }}>
          <Typography.Text strong ellipsis={{ tooltip: record.subject.name }}>
            {record.subject.name}
          </Typography.Text>
          <Typography.Text type="secondary">{record.subject.subjectCode}</Typography.Text>
        </Space>
      ),
    },
    { title: "Giảng viên", key: "lecturer", render: (_, record) => record.lecturer.fullName, width: 180 },
    {
      title: "Phòng",
      key: "room",
      render: (_, record) => <Tag color="blue">{record.room.roomCode}</Tag>,
      width: 120,
    },
    { title: "Lịch học", key: "schedule", render: (_, record) => scheduleLabel(record), width: 230 },
    {
      title: "Sĩ số",
      key: "capacity",
      render: (_, record) => `${record.currentEnrollment}/${record.maxCapacity}`,
      width: 85,
    },
  ];

  const onPageChange = (pagination: TablePaginationConfig) => setPage(pagination.current ?? 1);

  return (
    <div className="admin-timetable-page">
      <style>{`
        .admin-timetable-page { display: grid; gap: 18px; }
        .admin-timetable-heading { align-items: flex-end; display: flex; justify-content: space-between; gap: 16px; }
        .admin-timetable-heading h2 { margin: 0 0 6px !important; }
        .admin-timetable-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
        .admin-timetable-layout { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 18px; align-items: start; }
        .admin-timetable-toolbar { display: flex; justify-content: space-between; padding: 16px 16px 0; gap: 12px; }
        .admin-timetable-toolbar .ant-input-affix-wrapper { max-width: 360px; }
        .admin-timetable-form .ant-form-item { margin-bottom: 14px; }
        .admin-timetable-form .ant-form-item-label { padding-bottom: 4px; }
        .admin-timetable-mobile-note { display: none; }
        @media (max-width: 1100px) { .admin-timetable-layout { grid-template-columns: 1fr; } }
        @media (max-width: 640px) { .admin-timetable-heading { align-items: flex-start; flex-direction: column; } .admin-timetable-stats { grid-template-columns: 1fr; gap: 10px; } .admin-timetable-toolbar { flex-direction: column; } .admin-timetable-toolbar .ant-input-affix-wrapper { max-width: none; width: 100%; } .admin-timetable-mobile-note { display: block; } }
      `}</style>

      <header className="admin-timetable-heading">
        <div>
          <Typography.Text type="secondary">
            Chỉnh sửa lịch lớp, phòng và giảng viên. Backend kiểm tra xung đột trước khi lưu.
          </Typography.Text>
        </div>
        <Tag icon={<CalendarOutlined />} color="processing">
          {semesterQuery.data
            ? `${semesterQuery.data.semesterCode} · ${semesterQuery.data.name}`
            : "Đang tải học kỳ"}
        </Tag>
      </header>

      {(semesterQuery.isError || lookupsQuery.isError) && (
        <Alert
          type="error"
          showIcon
          message="Không tải được dữ liệu quản trị"
          description="Kiểm tra kết nối hoặc quyền ADMIN rồi thử lại."
          action={
            <Button
              size="small"
              onClick={() => {
                void semesterQuery.refetch();
                void lookupsQuery.refetch();
              }}
            >
              Thử lại
            </Button>
          }
        />
      )}

      <div className="admin-timetable-stats">
        <Card>
          <Statistic
            title="Lớp trong học kỳ"
            value={sectionsQuery.data?.totalItems ?? 0}
            loading={sectionsQuery.isLoading}
          />
        </Card>
        <Card>
          <Statistic title="Đang chọn" value={selected?.sectionCode ?? "—"} />
        </Card>
        <Card>
          <Statistic
            title="Sĩ số lớp"
            value={selected ? `${selected.currentEnrollment}/${selected.maxCapacity}` : "—"}
          />
        </Card>
      </div>

      <div className="admin-timetable-layout">
        <Card title="Danh sách lớp học phần" styles={{ body: { padding: 0 } }}>
          <div className="admin-timetable-toolbar">
            <Input
              allowClear
              value={keyword}
              prefix={<SearchOutlined />}
              placeholder="Tìm mã lớp hoặc môn học"
              aria-label="Tìm lớp học phần"
              onChange={(event) => {
                setKeyword(event.target.value);
                setPage(1);
              }}
            />
            <Typography.Text type="secondary">
              {sectionsQuery.data?.totalItems ?? 0} lớp
            </Typography.Text>
          </div>
          {sectionsQuery.isLoading && (
            <div style={{ padding: 36, textAlign: "center" }}>
              <Spin />
            </div>
          )}
          {sectionsQuery.isError && (
            <Alert
              style={{ margin: 16 }}
              type="error"
              showIcon
              message="Không tải được danh sách lớp"
              action={
                <Button size="small" onClick={() => void sectionsQuery.refetch()}>
                  Thử lại
                </Button>
              }
            />
          )}
          {sectionsQuery.isSuccess && sections.length === 0 && (
            <Empty style={{ padding: 32 }} description="Không tìm thấy lớp phù hợp." />
          )}
          {sectionsQuery.isSuccess && sections.length > 0 && (
            <Table<Section>
              rowKey="id"
              size="middle"
              columns={columns}
              dataSource={sections}
              scroll={{ x: 1050 }}
              rowSelection={{
                type: "radio",
                selectedRowKeys: selected ? [selected.id] : [],
                onChange: (keys) => setSelectedId(Number(keys[0])),
              }}
              onRow={(record) => ({ onClick: () => setSelectedId(record.id) })}
              pagination={{
                current: page,
                pageSize: PAGE_SIZE,
                total: sectionsQuery.data.totalItems,
                showSizeChanger: false,
                showTotal: (total) => `Tổng ${total} lớp`,
              }}
              onChange={onPageChange}
            />
          )}
        </Card>

        <Card title={selected ? `Điều chỉnh ${selected.sectionCode}` : "Thông tin phân công"}>
          {selected ? (
            <>
              <Typography.Paragraph type="secondary">
                {selected.subject.name} · {selected.subject.credits} tín chỉ
              </Typography.Paragraph>
              <Form<SectionUpdateRequest>
                key={selected.id}
                className="admin-timetable-form"
                layout="vertical"
                initialValues={{
                  subjectId: selected.subject.id,
                  semesterId: selected.semester.id,
                  lecturerId: selected.lecturer.id,
                  roomId: selected.room.id,
                  dayOfWeek: selected.dayOfWeek,
                  startPeriod: selected.startPeriod,
                  endPeriod: selected.endPeriod,
                  startWeek: selected.startWeek,
                  endWeek: selected.endWeek,
                  maxCapacity: selected.maxCapacity,
                }}
                onFinish={(body) => saveMutation.mutate({ id: selected.id, body })}
              >
                <Form.Item label="Môn học" name="subjectId" rules={[{ required: true }]}>
                  <Select
                    showSearch
                    optionFilterProp="label"
                    disabled={selected.currentEnrollment > 0}
                    options={(lookupsQuery.data?.subjects ?? []).map((item) => ({
                      value: item.id,
                      label: `${item.subjectCode} · ${item.name}`,
                    }))}
                  />
                </Form.Item>
                <Form.Item label="Học kỳ" name="semesterId" rules={[{ required: true }]}>
                  <Select
                    disabled
                    options={(lookupsQuery.data?.semesters ?? []).map((item) => ({
                      value: item.id,
                      label: `${item.semesterCode} · ${item.name}`,
                    }))}
                  />
                </Form.Item>
                {selected.currentEnrollment > 0 && (
                  <Typography.Text className="admin-timetable-mobile-note" type="warning">
                    Không thể đổi môn khi lớp đã có sinh viên đăng ký.
                  </Typography.Text>
                )}
                <Form.Item label="Giảng viên" name="lecturerId" rules={[{ required: true }]}>
                  <Select
                    showSearch
                    optionFilterProp="label"
                    options={(lookupsQuery.data?.lecturers ?? []).map((item) => ({
                      value: item.id,
                      label: `${item.lecturerCode} · ${item.fullName}`,
                    }))}
                  />
                </Form.Item>
                <Form.Item label="Phòng học" name="roomId" rules={[{ required: true }]}>
                  <Select
                    showSearch
                    optionFilterProp="label"
                    options={(lookupsQuery.data?.rooms ?? []).map((item) => ({
                      value: item.id,
                      label: `${item.roomCode} · ${item.building ?? ""} · ${item.capacity} chỗ`,
                    }))}
                  />
                </Form.Item>
                <Form.Item label="Thứ trong tuần" name="dayOfWeek" rules={[{ required: true }]}>
                  <Select options={DAY_OPTIONS} />
                </Form.Item>
                <Space size={12} style={{ display: "flex" }}>
                  <Form.Item label="Tiết bắt đầu" name="startPeriod" rules={[{ required: true }]}>
                    <InputNumber min={1} max={12} style={{ width: "100%" }} />
                  </Form.Item>
                  <Form.Item label="Tiết kết thúc" name="endPeriod" rules={[{ required: true }]}>
                    <InputNumber min={1} max={12} style={{ width: "100%" }} />
                  </Form.Item>
                </Space>
                <Space size={12} style={{ display: "flex" }}>
                  <Form.Item label="Tuần bắt đầu" name="startWeek" rules={[{ required: true }]}>
                    <InputNumber
                      min={1}
                      max={
                        lookupsQuery.data?.semesters.find((item) => item.id === selected.semester.id)
                          ?.numWeeks ?? 30
                      }
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                  <Form.Item label="Tuần kết thúc" name="endWeek" rules={[{ required: true }]}>
                    <InputNumber
                      min={1}
                      max={
                        lookupsQuery.data?.semesters.find((item) => item.id === selected.semester.id)
                          ?.numWeeks ?? 30
                      }
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                </Space>
                <Form.Item label="Sĩ số tối đa" name="maxCapacity" rules={[{ required: true }]}>
                  <InputNumber
                    min={Math.max(selected.currentEnrollment, 1)}
                    max={selected.room.capacity}
                    style={{ width: "100%" }}
                  />
                </Form.Item>
                <Alert
                  type="info"
                  showIcon
                  message="Kiểm tra lịch phía máy chủ"
                  description="Hệ thống sẽ từ chối nếu phòng hoặc giảng viên bị trùng lịch, sức chứa không hợp lệ hoặc lớp có ràng buộc đăng ký."
                />
                <Button
                  type="primary"
                  htmlType="submit"
                  block
                  loading={saveMutation.isPending}
                  style={{ marginTop: 16 }}
                >
                  Lưu phân công
                </Button>
              </Form>
            </>
          ) : (
            <Empty description="Chọn lớp học phần để chỉnh sửa lịch." />
          )}
        </Card>
      </div>
    </div>
  );
}
