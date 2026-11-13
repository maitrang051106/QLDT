import { lazy, Suspense, useState, type ReactNode } from "react";
import {
  AppstoreOutlined,
  BookOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import {
  App as AntdApp,
  Alert,
  Button,
  ConfigProvider,
  Form,
  Input,
  Layout,
  Menu,
  Spin,
  Typography,
} from "antd";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "../modules/auth/AuthContext";
import { readApiError, type UserRole } from "../shared/api/client";

const AdminCatalogPage = lazy(() => import("../modules/catalog/AdminCatalogPage"));
const AdminTimetablePage = lazy(() => import("../modules/timetable/AdminTimetablePage"));
const AdminTuitionPage = lazy(() => import("../modules/tuition/AdminTuitionPage"));
const CourseCatalogPage = lazy(() => import("../modules/catalog/CourseCatalogPage"));
const LecturerSectionsPage = lazy(() =>
  import("../modules/catalog/SectionAccessPages").then((module) => ({
    default: module.LecturerSectionsPage,
  })),
);
const SectionRosterPage = lazy(() =>
  import("../modules/catalog/SectionAccessPages").then((module) => ({
    default: module.SectionRosterPage,
  })),
);
const SectionCatalogPage = lazy(() => import("../modules/catalog/SectionCatalogPage"));
const MyRegistrationsPage = lazy(() => import("../modules/registration/MyRegistrationsPage"));
const StudentTuitionPage = lazy(() => import("../modules/tuition/StudentTuitionPage"));
const TimetablePage = lazy(() => import("../modules/timetable/TimetablePage"));

const { Content, Header, Sider } = Layout;

const roleNames: Record<UserRole, string> = {
  ADMIN: "Ban quản lý",
  LECTURER: "Giảng viên",
  STUDENT: "Sinh viên",
};

const navigation: Record<UserRole, Array<{ key: string; label: string; icon: ReactNode }>> = {
  STUDENT: [
    { key: "/app/sections", label: "Đăng ký lớp", icon: <BookOutlined /> },
    { key: "/app/registrations", label: "Lớp đã đăng ký", icon: <TeamOutlined /> },
    { key: "/app/timetable", label: "Thời khóa biểu", icon: <CalendarOutlined /> },
    { key: "/app/tuition", label: "Học phí & biên lai", icon: <DollarOutlined /> },
  ],
  LECTURER: [
    { key: "/app/timetable", label: "Lịch giảng dạy", icon: <CalendarOutlined /> },
    { key: "/app/sections", label: "Lớp phụ trách", icon: <TeamOutlined /> },
  ],
  ADMIN: [
    { key: "/app/subjects", label: "Môn học", icon: <BookOutlined /> },
    { key: "/app/sections", label: "Lớp học phần", icon: <AppstoreOutlined /> },
    { key: "/app/timetable/manage", label: "Xếp lịch & phân công", icon: <CalendarOutlined /> },
    { key: "/app/tuition/manage", label: "Quản lý học phí", icon: <DollarOutlined /> },
  ],
};

function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [errorText, setErrorText] = useState("");

  if (user) return <Navigate to="/app" replace />;

  async function onFinish(values: { username: string; password: string }) {
    setSubmitting(true);
    setErrorText("");
    try {
      await login(values.username, values.password);
      navigate("/app", { replace: true });
    } catch (error: unknown) {
      const body = readApiError(error);
      const messages: Record<string, string> = {
        INVALID_CREDENTIALS: "Tên đăng nhập hoặc mật khẩu chưa chính xác.",
        ACCOUNT_LOCKED: "Tài khoản đang bị khóa. Vui lòng liên hệ quản trị viên.",
      };
      setErrorText(messages[body?.error ?? ""] ?? "Không thể đăng nhập lúc này. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <header className="login-topbar">
        <div className="brand-lockup">
          <div className="brand-mark">B</div>
          <div>
            <strong>ĐẠI HỌC BÁCH KHOA HÀ NỘI</strong>
            <span>QUẢN LÝ ĐÀO TẠO</span>
          </div>
        </div>
        <span className="login-top-note">CỔNG HỌC VỤ TRỰC TUYẾN</span>
      </header>

      <section className="login-main">
        <div className="login-context">
          <p className="eyebrow">HỆ THỐNG ĐÀO TẠO</p>
          <h1>
            Quản lý &amp;
            <br />
            đăng ký lớp
          </h1>
          <p className="login-description">
            Truy cập không gian học vụ dành cho sinh viên, giảng viên và ban quản lý.
          </p>
          <div className="context-rule" />
          <div className="context-meta">
            <span>IT3180</span>
            <span>NHÓM 20</span>
          </div>
        </div>

        <section className="login-panel" aria-labelledby="login-title">
          <div className="panel-heading">
            <div className="panel-icon">
              <ClockCircleOutlined />
            </div>
            <div>
              <p className="eyebrow">TÀI KHOẢN ĐƯỢC CẤP</p>
              <h2 id="login-title">Đăng nhập</h2>
            </div>
          </div>
          {errorText && <Alert className="login-error" type="error" showIcon message={errorText} />}
          <Form layout="vertical" size="large" onFinish={onFinish} requiredMark={false}>
            <Form.Item
              label="Tên đăng nhập"
              name="username"
              rules={[{ required: true, message: "Vui lòng nhập tên đăng nhập." }]}
            >
              <Input autoComplete="username" placeholder="Nhập tên đăng nhập" />
            </Form.Item>
            <Form.Item
              label="Mật khẩu"
              name="password"
              rules={[{ required: true, message: "Vui lòng nhập mật khẩu." }]}
            >
              <Input.Password autoComplete="current-password" placeholder="Nhập mật khẩu" />
            </Form.Item>
            <Button type="primary" htmlType="submit" block loading={submitting}>
              Đăng nhập
            </Button>
          </Form>
          <p className="login-footnote">
            Tài khoản do nhà trường cấp. Hệ thống không hỗ trợ đăng ký mới.
          </p>
        </section>
      </section>

      <footer className="login-footer">
        <span>HỆ THỐNG QUẢN LÝ &amp; ĐĂNG KÝ HỌC PHẦN</span>
        <span>ĐẠI HỌC BÁCH KHOA HÀ NỘI</span>
      </footer>
    </main>
  );
}

function AccessDenied() {
  const navigate = useNavigate();

  return (
    <main className="access-denied">
      <p className="eyebrow">403 · KHÔNG CÓ QUYỀN TRUY CẬP</p>
      <h1>Phiên hiện tại không được phép truy cập khu vực này.</h1>
      <Button onClick={() => navigate(-1)}>Quay lại</Button>
    </main>
  );
}

function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <main className="not-found" role="alert">
      <p className="eyebrow">404 · KHÔNG TÌM THẤY TRANG</p>
      <h1>Đường dẫn bạn truy cập không tồn tại.</h1>
      <Button type="primary" onClick={() => navigate("/login")}>
        Về trang đăng nhập
      </Button>
    </main>
  );
}

function ProtectedApp() {
  const { user, loading, authError, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  if (loading)
    return (
      <div className="app-loading">
        <Spin size="large" />
      </div>
    );
  if (authError?.status === 403) return <AccessDenied />;
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;

  const menu = navigation[user.role];
  if (location.pathname === "/app" || location.pathname === "/app/") {
    return <Navigate to={menu[0].key} replace />;
  }

  const activeItem = menu.find(
    (item) => location.pathname === item.key || location.pathname.startsWith(`${item.key}/`),
  );
  if (!activeItem) {
    return (
      <main className="access-denied">
        <p className="eyebrow">403 · KHÔNG CÓ QUYỀN TRUY CẬP</p>
        <h1>Khu vực này không dành cho tài khoản của bạn.</h1>
        <Button onClick={() => navigate(menu[0].key)}>Về trang của tôi</Button>
      </main>
    );
  }

  const rosterMatch = location.pathname.match(/^\/app\/sections\/(\d+)\/students$/);
  let pageContent: ReactNode;
  if (rosterMatch) {
    pageContent = <SectionRosterPage sectionId={Number(rosterMatch[1])} />;
  } else if (user.role === "STUDENT" && location.pathname === "/app/sections") {
    pageContent = <SectionCatalogPage />;
  } else if (user.role === "STUDENT" && location.pathname === "/app/registrations") {
    pageContent = <MyRegistrationsPage />;
  } else if (user.role === "STUDENT" && location.pathname === "/app/tuition") {
    pageContent = <StudentTuitionPage />;
  } else if (location.pathname === "/app/timetable" && user.role !== "ADMIN") {
    pageContent = <TimetablePage role={user.role} />;
  } else if (user.role === "LECTURER" && location.pathname === "/app/sections") {
    pageContent = <LecturerSectionsPage />;
  } else if (user.role === "ADMIN" && location.pathname === "/app/timetable/manage") {
    pageContent = <AdminTimetablePage />;
  } else if (user.role === "ADMIN" && location.pathname === "/app/tuition/manage") {
    pageContent = <AdminTuitionPage />;
  } else if (user.role === "ADMIN" && location.pathname === "/app/subjects") {
    pageContent = <AdminCatalogPage resource="subjects" />;
  } else if (user.role === "ADMIN" && location.pathname === "/app/sections") {
    pageContent = <AdminCatalogPage resource="sections" />;
  } else {
    pageContent = <Alert type="info" showIcon message="Màn hình này chưa được triển khai." />;
  }

  return (
    <Layout className="portal-layout">
      <Sider
        className="portal-sider"
        width={248}
        collapsedWidth={72}
        collapsed={collapsed}
        breakpoint="lg"
        onBreakpoint={setCollapsed}
        trigger={null}
      >
        <div className="portal-brand">
          <div className="brand-mark">B</div>
          {!collapsed && (
            <div className="portal-brand-text">
              <strong>ĐẠI HỌC BÁCH KHOA HÀ NỘI</strong>
              <span>QUẢN LÝ ĐÀO TẠO</span>
            </div>
          )}
        </div>
        {!collapsed && (
          <div className="nav-caption">
            KHÔNG GIAN {roleNames[user.role].toLocaleUpperCase("vi-VN")}
          </div>
        )}
        <Menu
          mode="inline"
          selectedKeys={[activeItem.key]}
          items={menu}
          onClick={({ key }) => navigate(key)}
        />
        <div className="sider-bottom">
          <div className="role-indicator">
            <span />
            {!collapsed && roleNames[user.role]}
          </div>
          <Button
            type="text"
            icon={<LogoutOutlined />}
            onClick={() => {
              logout();
              navigate("/login", { replace: true });
            }}
            aria-label="Đăng xuất"
            title="Đăng xuất"
          >
            {!collapsed && "Đăng xuất"}
          </Button>
        </div>
      </Sider>

      <Layout>
        <Header className="portal-header">
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed((value) => !value)}
            aria-label={collapsed ? "Mở thanh điều hướng" : "Thu gọn thanh điều hướng"}
          />
          <div className="header-breadcrumb">
            HỌC VỤ <span>/</span> {activeItem.label.toLocaleUpperCase("vi-VN")}
          </div>
          <div className="header-role">{roleNames[user.role]}</div>
        </Header>
        <Content className="portal-content">
          <div className="page-kicker">CỔNG QUẢN LÝ ĐÀO TẠO</div>
          <Typography.Title level={2}>{activeItem.label}</Typography.Title>
          <div className="module-content">{pageContent}</div>
        </Content>
      </Layout>
    </Layout>
  );
}

function AppRoutes() {
  const { user, loading, authError } = useAuth();
  return (
    <Routes>
      <Route path="/timetable/manage" element={<Navigate to="/app/timetable/manage" replace />} />
      <Route path="/courses" element={<CourseCatalogPage />} />
      <Route
        path="/login"
        element={
          authError?.status === 403 ? (
            <AccessDenied />
          ) : loading ? (
            <div className="app-loading">
              <Spin size="large" />
            </div>
          ) : user ? (
            <Navigate to="/app" replace />
          ) : (
            <LoginPage />
          )
        }
      />
      <Route path="/app/*" element={<ProtectedApp />} />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#a6192e",
          colorText: "#24282b",
          colorTextSecondary: "#68727a",
          colorBorder: "#e1e5e8",
          borderRadius: 8,
          fontFamily: '"Segoe UI", Arial, "Noto Sans", sans-serif',
          fontSize: 14,
          controlHeight: 38,
          controlHeightLG: 46,
        },
      }}
    >
      <AntdApp>
        <BrowserRouter>
          <AuthProvider>
            <Suspense
              fallback={
                <div className="app-loading">
                  <Spin size="large" />
                </div>
              }
            >
              <AppRoutes />
            </Suspense>
          </AuthProvider>
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
}
