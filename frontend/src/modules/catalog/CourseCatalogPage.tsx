import { useState } from "react";
import { BookOutlined, CloseOutlined, InfoCircleOutlined, SearchOutlined } from "@ant-design/icons";
import { Alert, Button, Empty, Input, Modal, Spin, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import type { Subject } from "../../shared/api/api-types";
import { useDebouncedValue } from "../../shared/hooks/useDebouncedValue";
import { fetchSubjects } from "./catalogApi";

export default function CourseCatalogPage() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const [page, setPage] = useState(1);
  const [selectedCourse, setSelectedCourse] = useState<Subject | null>(null);
  const subjectsQuery = useQuery({
    queryKey: ["catalog", "subjects", page, debouncedSearch],
    placeholderData: keepPreviousData,
    queryFn: () => fetchSubjects({ page, size: 10, keyword: debouncedSearch.trim() || undefined }),
  });

  const columns: ColumnsType<Subject> = [
    { title: "Mã học phần", dataIndex: "subjectCode", key: "subjectCode", width: 140, render: (code: string) => <span className="course-catalog-code">{code}</span> },
    { title: "Tên học phần", dataIndex: "name", key: "name", render: (name: string) => <strong>{name}</strong> },
    { title: "TC", dataIndex: "credits", key: "credits", width: 80, align: "center" },
    { title: "Mô tả học phần", dataIndex: "description", key: "description", render: (description: string | null) => <span className="course-catalog-muted">{description || "Chưa có mô tả"}</span> },
  ];

  return (
    <div className="course-catalog-page">
      <style>{`
        .course-catalog-page { color: #263238; }
        .course-catalog-intro { display: flex; justify-content: space-between; gap: 24px; align-items: flex-start; margin-bottom: 20px; }
        .course-catalog-eyebrow { color: #a6192e; font-size: 11px; font-weight: 700; letter-spacing: .14em; margin: 0 0 8px; }
        .course-catalog-heading { margin: 0 !important; color: #20272b !important; }
        .course-catalog-subtitle { color: #6c757d; margin: 8px 0 0; max-width: 700px; }
        .course-catalog-program { border-left: 3px solid #a6192e; color: #626b70; font-size: 12px; padding: 8px 0 8px 12px; white-space: nowrap; }
        .course-catalog-toolbar { background: #fff; border: 1px solid #e2e5e7; display: flex; gap: 12px; padding: 14px; margin-bottom: 12px; }
        .course-catalog-search { max-width: 560px; }
        .course-catalog-summary { align-items: center; color: #6c757d; display: flex; font-size: 12px; gap: 8px; margin: 0 0 8px; }
        .course-catalog-summary strong { color: #a6192e; }
        .course-catalog-table .ant-table { border: 1px solid #e2e5e7; border-radius: 2px; }
        .course-catalog-table .ant-table-thead > tr > th { background: #f5f6f7; color: #525b60; font-size: 11px; letter-spacing: .04em; text-transform: uppercase; }
        .course-catalog-table .ant-table-tbody > tr { cursor: pointer; }
        .course-catalog-table .ant-table-tbody > tr:hover > td { background: #fff8f8 !important; }
        .course-catalog-code { color: #a6192e; font-family: Consolas, monospace; font-weight: 700; }
        .course-catalog-muted { color: #8a9398; font-size: 12px; }
        .course-catalog-legend { display: flex; gap: 14px; margin-top: 10px; color: #798388; font-size: 11px; }
        .course-catalog-detail { border-top: 1px solid #edf0f1; margin-top: 4px; padding-top: 16px; }
        .course-catalog-detail-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 18px; }
        .course-catalog-detail-card { background: #f7f8f8; padding: 12px; }
        .course-catalog-detail-card span { color: #778187; display: block; font-size: 11px; margin-bottom: 5px; text-transform: uppercase; }
        .course-catalog-detail-card strong { color: #273238; font-size: 16px; }
        .course-catalog-description { color: #566168; line-height: 1.65; margin-bottom: 0; }
        @media (max-width: 640px) { .course-catalog-intro { flex-direction: column; gap: 12px; } .course-catalog-toolbar { flex-direction: column; } .course-catalog-search { max-width: none; width: 100%; } }
      `}</style>

      <div className="course-catalog-intro">
        <div>
          <p className="course-catalog-eyebrow">TRA CỨU HỌC VỤ · CTĐT</p>
          <Typography.Title className="course-catalog-heading" level={2}>Danh mục học phần</Typography.Title>
          <p className="course-catalog-subtitle">Tra cứu thông tin học phần được đồng bộ từ danh mục môn học của hệ thống.</p>
        </div>
        <div className="course-catalog-program">DỮ LIỆU TỪ HỆ THỐNG ĐÀO TẠO</div>
      </div>

      <div className="course-catalog-toolbar">
        <Input allowClear className="course-catalog-search" aria-label="Tìm học phần" placeholder="Tìm theo mã hoặc tên học phần" prefix={<SearchOutlined />} value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} />
        <Button aria-label="Xóa bộ lọc" icon={<CloseOutlined />} onClick={() => { setSearch(""); setPage(1); }} disabled={!search}>Xóa lọc</Button>
      </div>

      {subjectsQuery.isLoading && <Spin />}
      {subjectsQuery.isError && <Alert type="error" showIcon message="Không thể tải danh mục học phần" description="Vui lòng thử lại sau." />}
      {subjectsQuery.isSuccess && (
        <>
          <div className="course-catalog-summary"><BookOutlined /> Có <strong>{subjectsQuery.data.totalItems}</strong> học phần · Bấm vào một dòng để xem chi tiết</div>
          <div className="course-catalog-table">
            <Table<Subject> rowKey="id" size="small" columns={columns} dataSource={subjectsQuery.data.items} pagination={{ current: page, pageSize: 10, total: subjectsQuery.data.totalItems, showSizeChanger: false, showTotal: (total) => `Tổng ${total} học phần` }} onChange={(pagination) => setPage(pagination.current ?? 1)} locale={{ emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Không tìm thấy học phần phù hợp." /> }} scroll={{ x: 760 }} onRow={(course) => ({ onClick: () => setSelectedCourse(course) })} />
          </div>
          <div className="course-catalog-legend"><span><InfoCircleOutlined /> Dữ liệu hiển thị theo danh mục môn học do hệ thống quản lý.</span></div>
        </>
      )}

      <Modal open={selectedCourse !== null} onCancel={() => setSelectedCourse(null)} footer={null} title={selectedCourse ? `${selectedCourse.subjectCode} · ${selectedCourse.name}` : undefined} width={620}>
        {selectedCourse && (
          <div className="course-catalog-detail">
            <div className="course-catalog-detail-grid">
              <div className="course-catalog-detail-card"><span>Số tín chỉ</span><strong>{selectedCourse.credits} tín chỉ</strong></div>
              <div className="course-catalog-detail-card"><span>Mã học phần</span><strong>{selectedCourse.subjectCode}</strong></div>
            </div>
            <Typography.Paragraph className="course-catalog-description"><Typography.Text strong>Mô tả học phần: </Typography.Text>{selectedCourse.description || "Chưa có mô tả."}</Typography.Paragraph>
          </div>
        )}
      </Modal>
    </div>
  );
}
