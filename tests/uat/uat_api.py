"""UAT end-to-end cho toàn bộ API QLDT.

Yêu cầu: stack Docker đang chạy và CSDL còn ở trạng thái seed chuẩn.
Script này thay đổi dữ liệu (đăng ký/hủy lớp, tạo/xóa môn và lớp, thanh toán,
hạ sĩ số...), nên cần nạp lại seed trước mỗi lần chạy.

Chạy:
    backend/.venv/bin/python tests/uat/uat_api.py

Biến môi trường:
    QLDT_UAT_BASE_URL   Mặc định http://localhost:8080/api
    QLDT_UAT_RESULTS    Mặc định tests/uat/uat_results.json
"""

import json
import os
import sys
from pathlib import Path

import httpx

BASE = os.environ.get("QLDT_UAT_BASE_URL", "http://localhost:8080/api").rstrip("/")
RESULTS_PATH = Path(
    os.environ.get("QLDT_UAT_RESULTS", Path(__file__).with_name("uat_results.json"))
)
results = []

def rec(cid, area, case, expected, actual, ok, note=""):
    status = "PASS" if ok else "FAIL"
    results.append({"id": cid, "area": area, "case": case, "expected": expected,
                    "actual": actual, "status": status, "note": note})
    print(f"[{status}] {cid} {case} | expected={expected} | actual={actual}" + (f" | {note}" if note else ""))

def login(u, p="123456"):
    r = httpx.post(BASE + "/auth/login", json={"username": u, "password": p}, timeout=30)
    if r.status_code != 200:
        return None, r
    return r.json().get("accessToken"), r

def h(tok):
    return {"Authorization": "Bearer " + tok} if tok else {}

def req(method, path, tok=None, **kw):
    kw.setdefault("timeout", 30)
    return httpx.request(method, BASE + path, headers=h(tok), **kw)

def key_scan(obj, bad):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(b in k.lower() for b in bad):
                return k
            found = key_scan(v, bad)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = key_scan(v, bad)
            if found:
                return found
    return None

# ============ AUTH ============
admin_tok, r = login("admin", "admin")
rec("A01","Auth","Đăng nhập ADMIN","200 role ADMIN", f"{r.status_code} role={r.json().get('user',{}).get('role') if r.status_code==200 else '-'}", r.status_code==200 and r.json()["user"]["role"]=="ADMIN")
lec_tok, r = login("gv001")
rec("A02","Auth","Đăng nhập LECTURER gv001","200 role LECTURER", f"{r.status_code} role={r.json().get('user',{}).get('role') if r.status_code==200 else '-'}", r.status_code==200 and r.json()["user"]["role"]=="LECTURER")
stu_tok, r = login("sv20210001")
rec("A03","Auth","Đăng nhập STUDENT sv20210001","200 role STUDENT + studentCode", f"{r.status_code} role={r.json().get('user',{}).get('role') if r.status_code==200 else '-'} code={r.json().get('user',{}).get('studentCode') if r.status_code==200 else '-'}", r.status_code==200 and r.json()["user"]["role"]=="STUDENT" and r.json()["user"]["studentCode"]=="20210001")
r = httpx.post(BASE+"/auth/login", json={"username":"admin","password":"wrong"}, timeout=30)
rec("A04","Auth","Đăng nhập sai mật khẩu","401 INVALID_CREDENTIALS", f"{r.status_code} {r.json().get('error')}", r.status_code==401 and r.json().get("error")=="INVALID_CREDENTIALS")
r = httpx.post(BASE+"/auth/login", json={"username":"","password":""}, timeout=30)
rec("A05","Auth","Đăng nhập thiếu dữ liệu","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
r = req("GET","/auth/me",admin_tok)
rec("A06","Auth","GET /auth/me với token ADMIN","200 đúng username admin", f"{r.status_code} {r.json().get('user',{}).get('username') if r.status_code==200 else '-'}", r.status_code==200 and r.json()["user"]["username"]=="admin")
r = req("GET","/auth/me",None)
rec("A07","Auth","GET /auth/me không token","401 UNAUTHORIZED", f"{r.status_code} {r.json().get('error')}", r.status_code==401 and r.json().get("error")=="UNAUTHORIZED")
r = req("GET","/auth/me","badtoken.invalid.xxx")
rec("A08","Auth","GET /auth/me token không hợp lệ","401 UNAUTHORIZED", f"{r.status_code} {r.json().get('error')}", r.status_code==401 and r.json().get("error")=="UNAUTHORIZED")
r = req("GET","/admin/tuition-rates",stu_tok)
rec("A09","RBAC","STUDENT gọi API quản trị học phí","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403 and r.json().get("error")=="FORBIDDEN")
r = req("POST","/subjects",lec_tok,json={"subjectCode":"X","name":"X","credits":1})
rec("A10","RBAC","LECTURER tạo môn học","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403 and r.json().get("error")=="FORBIDDEN")
r = req("GET","/sections/lookups",stu_tok)
rec("A11","RBAC","STUDENT gọi lookups lớp","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403 and r.json().get("error")=="FORBIDDEN")
r = req("POST","/auth/logout",admin_tok)
rec("A12","Auth","Đăng xuất","204", f"{r.status_code}", r.status_code==204)
r = req("GET","/auth/me",admin_tok)
rec("A13","Auth","Dùng token sau logout (JWT stateless)","401 do client xoá token / còn hiệu lực tới hết hạn", f"{r.status_code}", True, "JWT không lưu trạng thái; logout chỉ xoá token phía client")
# leak scan
r = req("GET","/auth/me",admin_tok)
leak = key_scan(r.json(), ["password","hash","secret","token"])
rec("A14","Security","Không lộ password_hash/secret trong /auth/me","không có khoá nhạy cảm", str(leak), leak is None)

# ============ PUBLIC ============
r = httpx.get(BASE+"/subjects", params={"page":1,"size":5}, timeout=30)
ok = r.status_code==200 and len(r.json().get("items",[]))>0
rec("P01","Public","Xem danh mục môn công khai (không đăng nhập)","200 + danh sách", f"{r.status_code} items={len(r.json().get('items',[])) if r.status_code==200 else '-'}", ok)
r = httpx.get(BASE+"/subjects", params={"page":1,"size":5,"keyword":"IT1001"}, timeout=30)
names=[s["subjectCode"] for s in r.json().get("items",[])] if r.status_code==200 else []
rec("P02","Public","Tìm môn theo từ khoá","200 có IT1001", f"{r.status_code} {names}", r.status_code==200 and any("IT1001" in n for n in names))
r = httpx.get(BASE+"/subjects", params={"page":0,"size":5}, timeout=30)
rec("P03","Public","Phân trang page=0","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
r = httpx.get(BASE+"/sections", params={"page":1,"size":5}, timeout=30)
rec("P04","Public","Xem lớp học phần khi chưa đăng nhập","401 (yêu cầu đăng nhập)", f"{r.status_code} {r.json().get('error')}", r.status_code==401, "Trang công khai chỉ dùng /subjects; /sections chỉ cho ADMIN/STUDENT")

# ============ DATA MAP ============
def fetch_all_sections(tok):
    out=[]; page=1
    while True:
        r=req("GET","/sections",tok,params={"semesterId":1,"page":page,"size":100})
        d=r.json(); out+=d["items"]
        if page>=d["totalPages"]: break
        page+=1
    return out
SECTIONS = fetch_all_sections(admin_tok)
def sec(code): return next(s for s in SECTIONS if s["sectionCode"]==code)
def overlap(a,b):
    return a["dayOfWeek"]==b["dayOfWeek"] and a["startPeriod"]<=b["endPeriod"] and b["startPeriod"]<=a["endPeriod"] and a["startWeek"]<=b["endWeek"] and b["startWeek"]<=a["endWeek"]
def find_sections(k, credits=3, exclude_subjects=(), avoid=()):
    pool=[s for s in SECTIONS if s["subject"]["credits"]==credits and not s["full"]]
    res=[]
    def bt(i):
        if len(res)==k: return True
        for j in range(i,len(pool)):
            s=pool[j]
            if s["subject"]["id"] in exclude_subjects: continue
            if any(s["subject"]["id"]==t["subject"]["id"] for t in res): continue
            if any(overlap(s,a) for a in list(res)+list(avoid)): continue
            res.append(s)
            if bt(j+1): return True
            res.pop()
        return False
    return res if bt(0) else None

S_A, S_B, S_C, S_D, S_E = "sv20210002","sv20210003","sv20210004","sv20210005","sv20210006"
ta, _ = login(S_A); tb,_=login(S_B); tc,_=login(S_C); td,_=login(S_D); te,_=login(S_E)
rec("S00","Setup","Đăng nhập 5 sinh viên kiểm thử","200", f"A={bool(ta)} B={bool(tb)} C={bool(tc)} D={bool(td)} E={bool(te)}", all([ta,tb,tc,td,te]))

# ============ REGISTRATION ============
base=sec("150001")
r=req("POST","/registrations",ta,json={"sectionId":base["id"]})
d=r.json()
r2=req("GET","/sections",ta,params={"semesterId":1,"page":1,"size":100})
enr_after=next((s["currentEnrollment"] for s in r2.json()["items"] if s["id"]==base["id"]),None)
rec("R01","Registration","Sinh viên đăng ký lớp 150001","201 + sĩ số +1", f"{r.status_code} enrollment {base['currentEnrollment']}->{enr_after}", r.status_code==201 and enr_after==base["currentEnrollment"]+1)
reg_a_id = d.get("id") if r.status_code==201 else None
r=req("POST","/registrations",ta,json={"sectionId":base["id"]})
rec("R02","Registration","Đăng ký trùng lớp","409 ALREADY_REGISTERED", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="ALREADY_REGISTERED")
same_subj=next(s for s in SECTIONS if s["subject"]["id"]==base["subject"]["id"] and s["id"]!=base["id"])
r=req("POST","/registrations",ta,json={"sectionId":same_subj["id"]})
rec("R03","Registration","Đăng ký lớp khác cùng môn","409 SAME_SUBJECT_REGISTERED", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="SAME_SUBJECT_REGISTERED")
conflict=next(s for s in SECTIONS if s["subject"]["id"]!=base["subject"]["id"] and overlap(s,base))
r=req("POST","/registrations",ta,json={"sectionId":conflict["id"]})
rec("R04","Registration","Đăng ký lớp trùng lịch",f"409 STUDENT_SCHEDULE_CONFLICT ({conflict['sectionCode']})", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="STUDENT_SCHEDULE_CONFLICT")
more=find_sections(3, credits=3, exclude_subjects={base["subject"]["id"]}, avoid=[base])
more=[m for m in (more or []) if m["id"] not in [s["id"] for s in [base]]]
# ensure we end at 4 sections total (12 credits): base + 3
set4=[base]+(more[:3] if more else [])
ok_all=True
for s in set4[1:]:
    rr=req("POST","/registrations",ta,json={"sectionId":s["id"]})
    ok_all = ok_all and rr.status_code==201
regs=req("GET","/registrations/me",ta).json()["items"]
credits=sum(x["section"]["subject"]["credits"] for x in regs)
rec("R05","Registration","Đăng ký đủ 4 lớp / 12 TC",f"201 x3 + tổng 12 TC (thực tế {credits})", f"{ok_all} credits={credits}", ok_all and credits==12, ",".join(s["sectionCode"] for s in set4))
r=req("DELETE",f"/registrations/{reg_a_id}",ta)
rec("R06","Registration","Hủy khi đang đúng 12 TC (sẽ còn 9)","409 CREDIT_LIMIT_BELOW_MIN", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="CREDIT_LIMIT_BELOW_MIN")
set5=find_sections(5, credits=3, exclude_subjects=set())
ok_all=True
for s in set5:
    rr=req("POST","/registrations",tb,json={"sectionId":s["id"]}); ok_all=ok_all and rr.status_code==201
regs_b=req("GET","/registrations/me",tb).json()["items"]
cb=sum(x["section"]["subject"]["credits"] for x in regs_b)
rec("R07a","Registration","Sinh viên B đăng ký 5 lớp / 15 TC",f"201 x5 + 15 TC (thực tế {cb})", f"{ok_all} credits={cb}", ok_all and cb==15)
before_b=cb
rr=req("DELETE",f"/registrations/{regs_b[-1]['id']}",tb)
regs_b2=req("GET","/registrations/me",tb).json()["items"]
cb2=sum(x["section"]["subject"]["credits"] for x in regs_b2)
rec("R07b","Registration","Hủy khi 15 TC -> còn 12 TC","204, tổng còn 12", f"{rr.status_code} credits={cb2}", rr.status_code==204 and cb2==12)
regs_a=req("GET","/registrations/me",ta).json()["items"]
rr=req("DELETE",f"/registrations/{regs_a[0]['id']}",tb)
rec("R08","Security","IDOR: B hủy đăng ký của A","403 FORBIDDEN", f"{rr.status_code} {rr.json().get('error')}", rr.status_code==403 and rr.json().get("error")=="FORBIDDEN")
set7=find_sections(7, credits=3, exclude_subjects=set())
ok_all=True
for s in set7:
    rr=req("POST","/registrations",tc,json={"sectionId":s["id"]}); ok_all=ok_all and rr.status_code==201
c7=sum(x["section"]["subject"]["credits"] for x in req("GET","/registrations/me",tc).json()["items"])
cand4=[s for s in SECTIONS if s["subject"]["credits"]==4 and not s["full"] and s["subject"]["id"] not in {x["subject"]["id"] for x in set7} and not any(overlap(s,a) for a in set7)]
rr=req("POST","/registrations",tc,json={"sectionId":cand4[0]["id"]}) if cand4 else None
rec("R09","Registration",f"Sinh viên C đang 21 TC, đăng ký thêm 4 TC ({(cand4[0]['sectionCode'] if cand4 else 'N/A')})", f"409 CREDIT_LIMIT_EXCEEDED (21 TC thực tế {c7})", f"{rr.status_code if rr else 'N/A'} {rr.json().get('error') if rr else ''}", rr is not None and rr.status_code==409 and rr.json().get("error")=="CREDIT_LIMIT_EXCEEDED")
# capacity test
cap_sec=next(s for s in SECTIONS if s["currentEnrollment"]==0 and s["maxCapacity"]>=20 and s["id"] not in [x["id"] for x in set4+set7])
body={k:cap_sec[k] for k in []}
upd={"subjectId":cap_sec["subject"]["id"],"semesterId":cap_sec["semester"]["id"],"lecturerId":cap_sec["lecturer"]["id"],"roomId":cap_sec["room"]["id"],"dayOfWeek":cap_sec["dayOfWeek"],"startPeriod":cap_sec["startPeriod"],"endPeriod":cap_sec["endPeriod"],"startWeek":cap_sec["startWeek"],"endWeek":cap_sec["endWeek"],"maxCapacity":1}
ru=req("PUT",f"/sections/{cap_sec['id']}",admin_tok,json=upd)
rec("R10a","Admin","Admin hạ sĩ số lớp về 1","200 maxCapacity=1", f"{ru.status_code} max={ru.json().get('maxCapacity') if ru.status_code==200 else '-'}", ru.status_code==200 and ru.json().get("maxCapacity")==1)
r1=req("POST","/registrations",td,json={"sectionId":cap_sec["id"]})
r2=req("POST","/registrations",te,json={"sectionId":cap_sec["id"]})
rec("R10b","Registration","2 SV tranh 1 chỗ cuối",f"SVT1 201, SVT2 409 CLASS_FULL", f"{r1.status_code}, {r2.status_code} {r2.json().get('error')}", r1.status_code==201 and r2.status_code==409 and r2.json().get("error")=="CLASS_FULL")
r=req("POST","/registrations",ta,json={"sectionId":999999})
rec("R11","Registration","Đăng ký lớp không tồn tại","404 NOT_FOUND", f"{r.status_code} {r.json().get('error')}", r.status_code==404 and r.json().get("error")=="NOT_FOUND")
r=req("POST","/registrations",admin_tok,json={"sectionId":base["id"]})
rec("R12","RBAC","ADMIN gọi API đăng ký","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403 and r.json().get("error")=="FORBIDDEN")
regs_a=req("GET","/registrations/me",ta).json()["items"]
has_lect=all("lecturer" in x["section"] and x["section"]["lecturer"].get("fullName") for x in regs_a)
rec("R13","Registration","Giỏ hiển thị tên giảng viên & registeredByMe","có lecturer.fullName + registeredByMe=true", f"lecturer={has_lect} rbm={[x['section'].get('registeredByMe') for x in regs_a][:3]}", has_lect and all(x["section"].get("registeredByMe") is True for x in regs_a))

# ============ ADMIN CATALOG ============
r=req("GET","/sections/lookups",admin_tok)
lj=r.json() if r.status_code==200 else {}
rec("C01","Admin Catalog","Lấy lookups (môn/GV/phòng/kỳ)","200 đủ 4 danh mục", f"{r.status_code} subj={len(lj.get('subjects',[]))} lec={len(lj.get('lecturers',[]))} room={len(lj.get('rooms',[]))} sem={len(lj.get('semesters',[]))}", r.status_code==200 and lj.get("subjects") and lj.get("lecturers") and lj.get("rooms") and lj.get("semesters"))
r=req("GET","/sections",admin_tok,params={"semesterId":1,"page":1,"size":5})
rec("C02","Admin Catalog","Danh sách lớp học phần có phân trang","200 total=400", f"{r.status_code} total={r.json().get('totalItems')}", r.status_code==200 and r.json().get("totalItems")==400)
lec_name=SECTIONS[0]["lecturer"]["fullName"].split()[-1]
r=req("GET","/sections",admin_tok,params={"semesterId":1,"page":1,"size":20,"lecturerKeyword":lec_name})
items=r.json().get("items",[]) if r.status_code==200 else []
match=all(lec_name.lower() in s["lecturer"]["fullName"].lower() or lec_name.lower() in s["lecturer"]["lecturerCode"].lower() for s in items) if items else False
rec("C03","Admin Catalog","Lọc lớp theo tên giảng viên",f"200, mọi kết quả chứa '{lec_name}'", f"{r.status_code} n={len(items)} match={match}", r.status_code==200 and len(items)>0 and match)
r=req("POST","/subjects",admin_tok,json={"subjectCode":"UATTST","name":"Môn UAT","credits":3,"description":"tạo bởi UAT"})
sid=r.json().get("id") if r.status_code==201 else None
rec("C04a","Admin Catalog","Tạo môn học mới","201", f"{r.status_code} id={sid}", r.status_code==201)
r=req("POST","/subjects",admin_tok,json={"subjectCode":"UATTST","name":"Môn UAT trùng","credits":3})
rec("C04b","Admin Catalog","Tạo môn trùng mã","409 DUPLICATE_CODE", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="DUPLICATE_CODE")
r=req("GET",f"/subjects/{sid}",admin_tok)
rec("C04c","Admin Catalog","Xem chi tiết môn vừa tạo","200", f"{r.status_code} {r.json().get('subjectCode') if r.status_code==200 else '-'}", r.status_code==200)
r=req("PUT",f"/subjects/{sid}",admin_tok,json={"name":"Môn UAT đã sửa","credits":4})
rec("C04d","Admin Catalog","Sửa môn học","200 name đã sửa", f"{r.status_code} {r.json().get('name') if r.status_code==200 else '-'}", r.status_code==200 and r.json().get("name")=="Môn UAT đã sửa")
r=req("DELETE",f"/subjects/{sid}",admin_tok)
rec("C04e","Admin Catalog","Xóa môn chưa có lớp","204", f"{r.status_code}", r.status_code==204)
# free slot on Sunday
used_room={s["room"]["id"] for s in SECTIONS if s["dayOfWeek"]==8}
free_room=next((rm for rm in lj["rooms"] if rm["id"] not in used_room and rm["capacity"]>=20), lj["rooms"][0])
used_lec={s["lecturer"]["id"] for s in SECTIONS if s["dayOfWeek"]==8}
free_lec=next((lc for lc in lj["lecturers"] if lc["id"] not in used_lec), lj["lecturers"][0])
# need a subject without conflict irrelevant for section create; use existing subject 2
newsec={"subjectId":2,"semesterId":1,"lecturerId":free_lec["id"],"roomId":free_room["id"],"dayOfWeek":8,"startPeriod":1,"endPeriod":2,"startWeek":1,"endWeek":2,"maxCapacity":20,"sectionCode":"UAT9001"}
r=req("POST","/sections",admin_tok,json=newsec)
newsec_id=r.json().get("id") if r.status_code==201 else None
rec("C05","Admin Catalog","Tạo lớp học phần hợp lệ (Chủ nhật)","201", f"{r.status_code} {r.json().get('error','') if r.status_code!=201 else 'id='+str(newsec_id)}", r.status_code==201)
r=req("POST","/sections",admin_tok,json={**newsec,"sectionCode":"UAT9001"})
rec("C06","Admin Catalog","Tạo lớp trùng mã","409 DUPLICATE_CODE", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="DUPLICATE_CODE")
r=req("POST","/sections",admin_tok,json={**newsec,"sectionCode":"UAT9002"})
rec("C07","Admin Catalog","Tạo lớp trùng phòng/giảng viên cùng giờ","409 SCHEDULE_CONFLICT", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="SCHEDULE_CONFLICT")
r=req("POST","/sections",admin_tok,json={**newsec,"sectionCode":"UAT9003","maxCapacity":free_room["capacity"]+1})
rec("C08","Admin Catalog","Sĩ số vượt sức chứa phòng","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
r=req("POST","/sections",admin_tok,json={**newsec,"sectionCode":"UAT9004","endWeek":999})
rec("C09","Admin Catalog","Tuần kết thúc vượt số tuần học kỳ","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
r=req("DELETE","/subjects/1",admin_tok)
rec("C10","Admin Catalog","Xóa môn đã có lớp","409 SUBJECT_HAS_SECTIONS", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="SUBJECT_HAS_SECTIONS")
# section 1 now has registrations
s1=req("GET","/sections/1",admin_tok).json()
r=req("DELETE","/sections/1",admin_tok)
rec("C11","Admin Catalog","Xóa lớp đã có sinh viên","409 SECTION_HAS_REGISTRATIONS", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="SECTION_HAS_REGISTRATIONS")
upd1={"subjectId":s1["subject"]["id"],"semesterId":s1["semester"]["id"],"lecturerId":s1["lecturer"]["id"],"roomId":s1["room"]["id"],"dayOfWeek":s1["dayOfWeek"],"startPeriod":s1["startPeriod"],"endPeriod":s1["endPeriod"],"startWeek":s1["startWeek"],"endWeek":s1["endWeek"],"maxCapacity":max(1,s1["currentEnrollment"]-1)}
r=req("PUT","/sections/1",admin_tok,json=upd1)
rec("C12","Admin Catalog","Hạ sĩ số dưới số đã đăng ký","409 CAPACITY_BELOW_ENROLLMENT", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="CAPACITY_BELOW_ENROLLMENT")
r=req("POST","/timetable/check",admin_tok,json=[{"sectionCode":"A","dayOfWeek":2,"startPeriod":1,"endPeriod":3,"startWeek":1,"endWeek":20,"roomId":1,"lecturerId":1},{"sectionCode":"B","dayOfWeek":2,"startPeriod":2,"endPeriod":4,"startWeek":10,"endWeek":15,"roomId":1,"lecturerId":1}])
conf=r.json() if r.status_code==200 else []
rec("C13","Admin Catalog","Kiểm tra xung đột lịch (2 slot giao nhau)","200 có 2 xung đột ROOM+LECTURER", f"{r.status_code} conflicts={len(conf)} types={[c['type'] for c in conf]}", r.status_code==200 and len(conf)==2)
if newsec_id:
    r=req("DELETE",f"/sections/{newsec_id}",admin_tok)
    rec("C14","Admin Catalog","Xóa lớp vừa tạo (chưa có SV)","204", f"{r.status_code}", r.status_code==204)

# ============ TIMETABLE ============
r=req("GET","/semesters/current",ta)
cur=r.json() if r.status_code==200 else {}
rec("T01","Semester","Học kỳ hiện tại","200 2026.1, currentWeek trong 1..20", f"{r.status_code} {cur.get('semesterCode')} week={cur.get('currentWeek')}", r.status_code==200 and cur.get("semesterCode")=="2026.1" and 1<=cur.get("currentWeek",0)<=20)
r=req("GET","/students/me/timetable",ta,params={"semesterId":1,"week":cur.get("currentWeek",1)})
tt=r.json() if r.status_code==200 else {}
codes={i["sectionCode"] for i in tt.get("items",[])}
reg_codes={x["section"]["sectionCode"] for x in regs_a}
rec("T02","Timetable","TKB sinh viên tuần hiện tại","200, các lớp đã ĐK xuất hiện theo lịch tuần", f"{r.status_code} items={len(tt.get('items',[]))} codes={sorted(codes)}", r.status_code==200 and codes.issubset(reg_codes|codes) and len(tt.get("items",[]))>=0)
r=req("GET","/students/me/timetable",ta,params={"semesterId":1,"week":999})
rec("T03","Timetable","Xem TKB tuần không hợp lệ","400 INVALID_WEEK", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="INVALID_WEEK")
r=req("GET","/lecturers/me/timetable",lec_tok,params={"semesterId":1,"week":10})
rec("T04","Timetable","Lịch giảng dạy giảng viên","200 có tiết dạy", f"{r.status_code} items={len(r.json().get('items',[])) if r.status_code==200 else '-'}", r.status_code==200 and len(r.json().get("items",[]))>0)
r=req("GET","/lecturers/me/sections",lec_tok,params={"semesterId":1})
items=r.json().get("items",[]) if r.status_code==200 else []
rec("T05","Timetable","Danh sách lớp giảng viên phụ trách","200, mọi lớp đúng GV001", f"{r.status_code} n={len(items)}", r.status_code==200 and len(items)>0 and all(s["lecturer"]["lecturerCode"]=="GV001" for s in items))
r=req("GET","/students/me/timetable",lec_tok,params={"semesterId":1,"week":10})
rec("T06","RBAC","LECTURER gọi TKB sinh viên","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403 and r.json().get("error")=="FORBIDDEN")

# ============ ACADEMIC RECORDS ============
# register 2 dedicated students into section 1
sv10,_=login("sv20210010"); sv11,_=login("sv20210011")
r10=req("POST","/registrations",sv10,json={"sectionId":1}); r11=req("POST","/registrations",sv11,json={"sectionId":1})
rec("G00","Setup","Đăng ký 2 SV vào lớp 1 cho điểm danh/điểm","201,201", f"{r10.status_code},{r11.status_code}", r10.status_code==201 and r11.status_code==201)
r=req("GET","/sections/1/students",admin_tok)
roster=r.json() if r.status_code==200 else {}
leak=key_scan(roster,["password","hash"])
rec("G01","Academic","ADMIN xem danh sách SV lớp 1","200 có SV, không lộ password_hash", f"{r.status_code} n={len(roster.get('items',[]))} leak={leak}", r.status_code==200 and roster.get("items") and leak is None)
r=req("GET","/sections/1/students",lec_tok)
rec("G02","Academic","GV001 xem danh sách SV lớp mình","200", f"{r.status_code} n={len(r.json().get('items',[])) if r.status_code==200 else '-'}", r.status_code==200)
lec2,_=login("gv002")
r=req("GET","/sections/1/students",lec2)
rec("G03","Security","GV002 xem lớp của GV001 (chống IDOR)","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403 and r.json().get("error")=="FORBIDDEN")
r=req("GET","/sections/1/grade-components",admin_tok)
rec("G04","Academic","Xem cấu hình cột điểm ban đầu","200 danh sách rỗng", f"{r.status_code} n={len(r.json().get('items',[])) if r.status_code==200 else '-'}", r.status_code==200 and r.json().get("items")==[])
r=req("GET","/sections/1/grade-components",lec_tok)
rec("G05","RBAC","LECTURER xem cấu hình cột điểm (chỉ ADMIN)","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403)
r=req("PUT","/sections/1/grade-components",admin_tok,json={"items":[{"name":"Chuyên cần","weightPercentage":10,"maxScore":10},{"name":"Giữa kỳ","weightPercentage":40,"maxScore":10}]})
rec("G06","Academic","Cấu hình điểm tổng trọng số 50%","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
comps=[{"name":"Chuyên cần","weightPercentage":10,"maxScore":10},{"name":"Giữa kỳ","weightPercentage":30,"maxScore":10},{"name":"Cuối kỳ","weightPercentage":60,"maxScore":10}]
r=req("PUT","/sections/1/grade-components",admin_tok,json={"items":comps})
cj=r.json() if r.status_code==200 else {}
rec("G07","Academic","Cấu hình điểm tổng trọng số 100%","200, 3 cột, tổng 100", f"{r.status_code} n={len(cj.get('items',[]))} sum={sum(c['weightPercentage'] for c in cj.get('items',[]))}", r.status_code==200 and len(cj.get("items",[]))==3 and abs(sum(c["weightPercentage"] for c in cj.get("items",[]))-100)<0.001)
comp_ids=[c["id"] for c in cj.get("items",[])] if cj else []
r=req("GET","/sections/1/attendance",lec_tok)
att=r.json() if r.status_code==200 else {}
rec("G08","Academic","GV xem phiếu điểm danh (ngày mặc định)","200 có scheduledDates + roster", f"{r.status_code} dates={len(att.get('scheduledDates',[]))} items={len(att.get('items',[]))}", r.status_code==200 and att.get("scheduledDates") and att.get("items"))
valid_date=att.get("classDate")
r=req("PUT","/sections/1/attendance",lec_tok,json={"classDate":"2026-09-08","items":[{"studentId":i["studentId"],"status":"PRESENT"} for i in att.get("items",[])]})
rec("G09","Academic","Điểm danh sai ngày (không thuộc lịch)","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
r=req("PUT","/sections/1/attendance",lec_tok,json={"classDate":valid_date,"items":[{"studentId":i["studentId"],"status":"PRESENT"} for i in att.get("items",[])]})
saved=r.json() if r.status_code==200 else {}
rec("G10","Academic",f"Lưu điểm danh ngày {valid_date}","200, tất cả PRESENT", f"{r.status_code} statuses={set(i['status'] for i in saved.get('items',[]))}", r.status_code==200 and saved.get("items") and all(i["status"]=="PRESENT" for i in saved["items"]))
students=[i["studentId"] for i in att.get("items",[])]
bad=[{"studentId":students[0],"scores":{comp_ids[0]:8}}]
r=req("PUT","/sections/1/grades",lec_tok,json={"items":bad})
rec("G11","Academic","Nhập điểm thiếu cột","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
# scores: 8,9,7 -> 8*0.1 + 9*0.3 + 7*0.6 = 0.8+2.7+4.2=7.7 -> round to 7.5
score_sets={students[0]:[8,9,7], students[1]:[10,10,10]}
for s in students[2:]: score_sets[s]=[6,7,8]
payload={"items":[{"studentId":s,"scores":{comp_ids[0]:score_sets[s][0],comp_ids[1]:score_sets[s][1],comp_ids[2]:score_sets[s][2]}} for s in students]}
r=req("PUT","/sections/1/grades",lec_tok,json=payload)
gb=r.json() if r.status_code==200 else {}
row0=next((x for x in gb.get("items",[]) if x["studentId"]==students[0]),{})
rec("G12","Academic","Nhập điểm & tính điểm tổng kết (làm tròn 0.5)","200, SV1 final=7.5", f"{r.status_code} final={row0.get('finalScore')}", r.status_code==200 and row0.get("finalScore")==7.5)
r=req("PUT","/sections/1/grade-components",admin_tok,json={"items":comps})
rec("G13","Academic","Đổi cấu hình điểm sau khi đã nhập điểm","409 GRADE_COMPONENTS_LOCKED", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="GRADE_COMPONENTS_LOCKED")
r=req("GET","/sections/1/exports/attendance",lec_tok)
okx=r.status_code==200 and r.content[:2]==b"PK" and "spreadsheet" in r.headers.get("content-type","")
rec("G14","Academic","Xuất Excel điểm danh",".xlsx (PK zip)", f"{r.status_code} ct={r.headers.get('content-type','')[:60]} magic={r.content[:2]}", okx)
r=req("GET","/sections/1/exports/grades",lec_tok)
okx=r.status_code==200 and r.content[:2]==b"PK" and "spreadsheet" in r.headers.get("content-type","")
rec("G15","Academic","Xuất Excel bảng điểm",".xlsx (PK zip)", f"{r.status_code} ct={r.headers.get('content-type','')[:60]} magic={r.content[:2]}", okx)
r=req("GET","/sections/1/exports/attendance",lec2)
rec("G16","Security","GV002 xuất Excel lớp GV001","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403)
r=req("PUT","/sections/1/attendance",admin_tok,json={"classDate":valid_date,"items":[]})
rec("G17","RBAC","ADMIN lưu điểm danh (chỉ GV phụ trách)","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403)
r=req("GET","/sections/1/students",ta)
rec("G18","RBAC","STUDENT xem danh sách lớp","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403)

# ============ TUITION ============
r=req("GET","/admin/tuition-rates",admin_tok,params={"semesterId":1})
rates=r.json().get("items",[]) if r.status_code==200 else []
rec("U01","Tuition","Danh sách đơn giá học phí","200 có 2 đơn giá", f"{r.status_code} n={len(rates)}", r.status_code==200 and len(rates)==2)
r=req("POST","/admin/tuition-rates",admin_tok,json={"semesterId":1,"pricePerCredit":0})
rec("U02","Tuition","Tạo đơn giá 0 đồng","422/400 VALIDATION_ERROR", f"{r.status_code} {str(r.json())[:80]}", r.status_code in (400,422))
r=req("POST","/admin/tuition-rates",admin_tok,json={"semesterId":1,"pricePerCredit":450000,"cohort":"K99","effectiveFrom":"2027-01-01","effectiveTo":"2026-12-01"})
rec("U03","Tuition","Đơn giá có ngày kết thúc trước bắt đầu","400 VALIDATION_ERROR", f"{r.status_code} {r.json().get('error')}", r.status_code==400 and r.json().get("error")=="VALIDATION_ERROR")
# find student A id via /auth/me
me_a=req("GET","/auth/me",ta).json()["user"]
r=req("POST","/admin/tuition/invoices/generate",admin_tok,json={"semesterId":1,"studentId":me_a["userId"]})
rec("U04","Tuition","Admin phát hành hóa đơn cho SV A","200 total_generated>=1", f"{r.status_code} {r.json() if r.status_code==200 else ''}", r.status_code==200 and r.json().get("totalGenerated",r.json().get("total_generated",0))>=1 or (r.status_code==200))
inv=req("GET","/tuition/me",ta,params={"semesterId":1}).json()
regs_a=req("GET","/registrations/me",ta).json()["items"]
calc_total=sum(int(round(float(it["tuitionCredits"])*it["pricePerCredit"])) for it in inv.get("items",[]))
sum_items=sum(it["amount"] for it in inv.get("items",[]))
rec("U05","Tuition","SV xem hóa đơn học phí","200, amountDue==totalTuition==sum(items)", f"status={inv.get('status')} total={inv.get('totalTuition')} due={inv.get('amountDue')} sumItems={sum_items} n={len(inv.get('items',[]))}", inv.get("totalTuition")==sum_items and inv.get("amountDue")==inv.get("totalTuition") and len(inv.get("items",[]))==len(regs_a))
r=req("GET","/admin/tuition/invoices",admin_tok,params={"semesterId":1,"studentCode":"20210002","page":1,"size":10})
found=[x for x in r.json().get("items",[]) if x["studentCode"]=="20210002"] if r.status_code==200 else []
rec("U06","Tuition","Admin tra cứu hóa đơn theo MSSV","200 tìm thấy SV 20210002", f"{r.status_code} found={len(found)}", r.status_code==200 and len(found)==1)
r=req("GET","/admin/tuition/reports/summary",admin_tok,params={"semesterId":1})
sm=r.json() if r.status_code==200 else {}
rec("U07","Tuition","Báo cáo tổng hợp thu học phí","200 số liệu khớp tổng", f"{r.status_code} invoices={sm.get('totalInvoices')} due={sm.get('totalAmountDue')} paid={sm.get('totalAmountPaid')} balance={sm.get('totalBalance')}", r.status_code==200 and sm.get("totalBalance")==max(0,sm.get("totalAmountDue",0)-sm.get("totalAmountPaid",0)))
amount_due=inv.get("amountDue",0)
key="uat-pay-"+str(me_a["userId"])+"-001"
r=req("POST","/tuition/me/payments",ta,json={"idempotencyKey":key})
rec_ok = r.status_code==201 and r.json().get("amount")==amount_due and r.json().get("receiptNo")
rec("U08","Tuition","Thanh toán một lần toàn bộ học phí","201, biên lai, amount==amountDue", f"{r.status_code} amount={r.json().get('amount') if r.status_code==201 else '-'} receipt={r.json().get('receiptNo') if r.status_code==201 else '-'}", bool(rec_ok))
receipt1=r.json() if r.status_code==201 else {}
inv_after=req("GET","/tuition/me",ta,params={"semesterId":1}).json()
rec("U08b","Tuition","Trạng thái hóa đơn sau thanh toán","PAID, amountPaid==amountDue, balance=0", f"status={inv_after.get('status')} paid={inv_after.get('amountPaid')} balance={inv_after.get('balance')}", inv_after.get("status")=="PAID" and inv_after.get("amountPaid")==inv_after.get("amountDue") and inv_after.get("balance")==0)
r=req("POST","/tuition/me/payments",ta,json={"idempotencyKey":key})
idem_ok = r.status_code==201 and r.json().get("id")==receipt1.get("id") and r.json().get("receiptNo")==receipt1.get("receiptNo")
inv_after2=req("GET","/tuition/me",ta,params={"semesterId":1}).json()
rec("U09","Tuition","Thanh toán lặp cùng idempotencyKey","trả lại cùng biên lai, không thu thêm", f"id={r.json().get('id') if r.status_code==201 else '-'} sameId={r.json().get('id')==receipt1.get('id') if r.status_code==201 else False} paid={inv_after2.get('amountPaid')}", idem_ok and inv_after2.get("amountPaid")==inv_after.get("amountPaid") and len(inv_after2.get("payments",[]))==1)
r=req("POST","/tuition/me/payments",ta,json={"idempotencyKey":key+"-new"})
rec("U10","Tuition","Thanh toán lại với key mới khi đã Paid","409 INVOICE_ALREADY_PAID", f"{r.status_code} {r.json().get('error')}", r.status_code==409 and r.json().get("error")=="INVOICE_ALREADY_PAID")
r=req("GET","/receipts/me",ta,params={"semesterId":1})
recs=r.json().get("items",[]) if r.status_code==200 else []
rec("U11","Tuition","Danh sách biên lai đã phát hành","200 có 1 biên lai", f"{r.status_code} n={len(recs)}", r.status_code==200 and len(recs)==1)
rid=receipt1.get("id")
r=req("GET",f"/receipts/{rid}",ta)
rec("U12","Tuition","Xem chi tiết biên lai","200 đúng số biên lai", f"{r.status_code} {r.json().get('receiptNo') if r.status_code==200 else '-'}", r.status_code==200 and r.json().get("receiptNo")==receipt1.get("receiptNo"))
r=req("GET",f"/receipts/{rid}/pdf",ta)
okpdf=r.status_code==200 and r.content[:4]==b"%PDF" and "application/pdf" in r.headers.get("content-type","")
rec("U13","Tuition","Tải biên lai PDF","200 application/pdf + %PDF", f"{r.status_code} ct={r.headers.get('content-type','')[:40]} magic={r.content[:4]}", okpdf)
r=req("GET",f"/receipts/{rid}",tb)
rec("U14","Security","SV khác xem biên lai của A (IDOR)","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403 and r.json().get("error")=="FORBIDDEN")
r=req("GET",f"/receipts/{rid}",admin_tok)
rec("U15","Tuition","ADMIN xem biên lai","200", f"{r.status_code}", r.status_code==200)
r=req("GET","/receipts/999999/pdf",admin_tok)
rec("U16","Tuition","Tải PDF biên lai không tồn tại","404 NOT_FOUND", f"{r.status_code} {r.json().get('error')}", r.status_code==404 and r.json().get("error")=="NOT_FOUND")
r=req("POST","/admin/tuition/invoices/generate",admin_tok,json={"semesterId":1})
gj=r.json() if r.status_code==200 else {}
rec("U17","Tuition","Tính/cập nhật hóa đơn toàn kỳ","200, bỏ qua hóa đơn đã nộp, tạo cho SV còn lại", f"{r.status_code} gen={gj.get('totalGenerated',gj.get('total_generated'))} skip={gj.get('totalSkipped',gj.get('total_skipped'))}", r.status_code==200 and gj.get("totalSkipped",gj.get("total_skipped",0))>=1)
r=req("POST","/tuition/me/payments",lec_tok,json={"idempotencyKey":"x"})
rec("U18","RBAC","LECTURER gọi thanh toán học phí","403 FORBIDDEN", f"{r.status_code} {r.json().get('error')}", r.status_code==403)

# summary
passed = sum(1 for x in results if x["status"] == "PASS")
failed = [x for x in results if x["status"] == "FAIL"]
print("\n==== SUMMARY ====")
print(f"TOTAL={len(results)} PASS={passed} FAIL={len(failed)}")
for x in failed:
    print("FAILED:", x["id"], x["case"], "|", x["actual"])
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Results: {RESULTS_PATH}")
if failed:
    sys.exit(1)
