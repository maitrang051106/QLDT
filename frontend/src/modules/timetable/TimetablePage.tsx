import { useEffect, useState } from "react";
import { CalendarOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Alert, Button, Empty, InputNumber, Spin, Tag } from "antd";
import api, { readApiError, requireItems, type UserRole } from "../../shared/api/client";
import type { CurrentSemester } from "../../shared/api/api-types";

interface TimetableEntry {
  date: string;
  dayOfWeek: number;
  startPeriod: number;
  endPeriod: number;
  sectionCode: string;
  subjectName?: string;
  roomCode?: string;
  lecturerName?: string;
  subject?: { name: string } | null;
  room?: { roomCode: string } | null;
  lecturer?: { fullName: string } | null;
}

interface ItemsResponse<T> {
  items: T[];
}

const dayColumns = [2, 3, 4, 5, 6, 7, 8];
const dayNames: Record<number, string> = {
  2: "Thứ hai",
  3: "Thứ ba",
  4: "Thứ tư",
  5: "Thứ năm",
  6: "Thứ sáu",
  7: "Thứ bảy",
  8: "Chủ nhật",
};

export default function TimetablePage({ role }: { role: UserRole }) {
  const [week, setWeek] = useState<number>();
  const isLecturer = role === "LECTURER";

  const currentSemesterQuery = useQuery({
    queryKey: ["current-semester"],
    queryFn: async () => (await api.get<CurrentSemester>("/semesters/current")).data,
  });
  const semesterId = currentSemesterQuery.data?.id;

  useEffect(() => {
    if (week === undefined && currentSemesterQuery.data?.currentWeek != null) {
      setWeek(currentSemesterQuery.data.currentWeek);
    }
  }, [currentSemesterQuery.data, week]);

  const timetableQuery = useQuery({
    queryKey: ["timetable", role, semesterId, week],
    enabled: semesterId !== undefined && week !== undefined,
    queryFn: async () => {
      const path = isLecturer ? "/lecturers/me/timetable" : "/students/me/timetable";
      const response = await api.get<ItemsResponse<TimetableEntry>>(path, {
        params: { semesterId, week },
      });
      return requireItems<TimetableEntry>(response.data);
    },
  });

  function changeWeek(nextWeek: number) {
    setWeek(Math.max(1, nextWeek));
  }

  const entries = timetableQuery.data ?? [];
  const timetableError = readApiError(timetableQuery.error);
  const dateByDay = new Map<number, string>();
  entries.forEach((entry) => dateByDay.set(entry.dayOfWeek, entry.date));

  return (
    <>
      <div className="feature-toolbar">
        <Tag icon={<CalendarOutlined />} color="processing">
          Học kỳ hiện tại:{" "}
          {currentSemesterQuery.data
            ? `${currentSemesterQuery.data.semesterCode} · ${currentSemesterQuery.data.name}`
            : "2026.1"}
        </Tag>
        <div className="week-control">
          <Button aria-label="Tuần trước" onClick={() => changeWeek((week ?? 1) - 1)}>
            ‹
          </Button>
          <InputNumber
            aria-label="Tuần"
            min={1}
            value={week}
            onChange={(value) => value && changeWeek(value)}
          />
          <Button aria-label="Tuần sau" onClick={() => changeWeek((week ?? 1) + 1)}>
            ›
          </Button>
          <Button onClick={() => setWeek(currentSemesterQuery.data?.currentWeek ?? 1)}>
            Tuần hiện tại
          </Button>
        </div>
      </div>

      {currentSemesterQuery.isError && (
        <Alert
          type="error"
          showIcon
          message="Không tải được thông tin học kỳ."
          description="Kiểm tra kết nối rồi tải lại trang."
        />
      )}
      {timetableQuery.isLoading && (
        <div className="feature-loading">
          <Spin />
        </div>
      )}
      {timetableQuery.isError && (
        <Alert
          type="error"
          showIcon
          message={
            timetableError?.error === "INVALID_WEEK"
              ? "Tuần được chọn không hợp lệ."
              : "Không tải được thời khóa biểu."
          }
          description={
            timetableError?.error === "INVALID_WEEK"
              ? "Đã chuyển về tuần hiện tại để tải lại."
              : undefined
          }
          action={
            <Button
              size="small"
              onClick={() =>
                timetableError?.error === "INVALID_WEEK"
                  ? setWeek(currentSemesterQuery.data?.currentWeek ?? 1)
                  : void timetableQuery.refetch()
              }
            >
              Thử lại
            </Button>
          }
        />
      )}
      {!timetableQuery.isLoading && !timetableQuery.isError && entries.length === 0 && (
        <div className="feature-empty">
          <Empty description="Không có lịch học trong tuần này." />
        </div>
      )}
      {entries.length > 0 && (
        <div className="timetable-scroll">
          <div className="timetable-grid">
            <div className="timetable-corner">Tiết</div>
            {dayColumns.map((day) => (
              <div className="timetable-day" key={day}>
                <strong>{dayNames[day]}</strong>
                <span>{dateByDay.get(day) ?? ""}</span>
              </div>
            ))}
            {Array.from({ length: 12 }, (_, index) => (
              <div
                className="timetable-period"
                key={index + 1}
                style={{ gridColumn: 1, gridRow: index + 2 }}
              >
                {index + 1}
              </div>
            ))}
            {entries.map((entry, index) => (
              <article
                className="timetable-event"
                key={`${entry.sectionCode}-${entry.date}-${entry.startPeriod}-${index}`}
                style={{
                  gridColumn: dayColumns.indexOf(entry.dayOfWeek) + 2,
                  gridRow: `${entry.startPeriod + 1} / span ${entry.endPeriod - entry.startPeriod + 1}`,
                }}
              >
                <strong>{entry.sectionCode}</strong>
                {(entry.subjectName ?? entry.subject?.name) && (
                  <span>{entry.subjectName ?? entry.subject?.name}</span>
                )}
                <span>
                  Tiết {entry.startPeriod}-{entry.endPeriod}
                </span>
                {(entry.roomCode ?? entry.room?.roomCode) && (
                  <span>{entry.roomCode ?? entry.room?.roomCode}</span>
                )}
                {isLecturer && (entry.lecturerName ?? entry.lecturer?.fullName) && (
                  <span>{entry.lecturerName ?? entry.lecturer?.fullName}</span>
                )}
              </article>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
