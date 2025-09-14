# Gotenberg Sandbox (PDF conversion API) — Docker Compose

Gotenberg คือ HTTP API สำหรับแปลง **HTML/URL/Office → PDF** และงาน PDF อื่น ๆ (merge ฯลฯ)  
ไฟล์ชุดนี้พร้อมให้คุณรันในเครื่อง และมีสคริปต์ทดสอบให้พร้อม

---

## 1) สเปคที่แนะนำ (Guideline)
> ปรับตามขนาดเอกสาร/จำนวน concurrent requests ของคุณ

- **Dev/เบา ๆ (PoC):** 1–2 vCPU, 1–2 GB RAM
- **งานทั่วไป/หลายผู้ใช้:** 4 vCPU, 4 GB RAM
- **งานหนัก/รายงานยาว/พร้อมกันมาก:** 8 vCPU+, 8–16 GB RAM
- **ดิสก์:** SSD ปกติพอ (ใช้พื้นที่ชั่วคราวตอนเรนเดอร์)
- **พอร์ต:** เปิด `3000/tcp` ให้ client เข้ามาเรียก API
- **สเกล:** ทำ load balancing หลาย instance ด้านหน้าได้ (stateless)

> เคล็ดลับ: ถ้าเจองาน HTML ซับซ้อน/ยาวมาก ให้เพิ่ม RAM/CPU และตั้ง timeout ฝั่ง client ให้เหมาะสม

---

## 2) เริ่มต้นใช้งาน
```bash
docker compose up -d
curl -s http://localhost:3000/health
# ควรได้ {"status":"UP"}
```

หรือใช้สคริปต์ช่วย:
```bash
./quickstart.sh
```

---

## 3) โครงสร้างไฟล์
```
.
├─ docker-compose.yml
├─ README.md
├─ examples/
│  └─ index.html
└─ scripts/
   ├─ convert_html.sh     # HTML → PDF
   ├─ convert_url.sh      # URL → PDF
   ├─ convert_docx.sh     # DOCX → PDF (ต้องมีไฟล์ตัวเอง)
   └─ merge_pdfs.sh       # รวมหลาย PDF
```

---

## 4) ตัวอย่างเรียกใช้งาน (cURL)

### 4.1 HTML → PDF
```bash
curl -X POST "http://localhost:3000/forms/chromium/convert/html"   -F "files=@examples/index.html"   -F "emulatedMediaType=screen"   -F "marginTop=10" -F "marginBottom=10" -F "marginLeft=10" -F "marginRight=10"   -o out.pdf
```

### 4.2 URL → PDF
```bash
curl -X POST "http://localhost:3000/forms/chromium/convert/url"   -F "url=https://example.com"   -F "landscape=false"   -o example.pdf
```

### 4.3 DOCX/XLSX/PPTX → PDF (LibreOffice)
```bash
# ใส่พาธไฟล์เอกสารของคุณเองแทน /path/to/sample.docx
curl -X POST "http://localhost:3000/forms/libreoffice/convert"   -F "files=@/path/to/sample.docx"   -o docx.pdf
```

### 4.4 รวมหลาย PDF (Merge)
```bash
curl -X POST "http://localhost:3000/forms/pdfengines/merge"   -F "files=@/path/to/one.pdf"   -F "files=@/path/to/two.pdf"   -o merged.pdf
```

---

## 5) ตัวอย่าง HTML
ดู `examples/index.html` แล้วลองแปลง:
```bash
./scripts/convert_html.sh
# จะได้ไฟล์ out.pdf
```

---

## 6) ทิปส์โปรดักชัน
- ใช้ **CSS สำหรับงานพิมพ์** (`@page`, margin, font embed) เพื่อคุณภาพที่คงที่
- อย่าเปิด service สู่สาธารณะโดยตรงถ้าไม่จำเป็น (ใส่ reverse proxy + auth)
- หาก input มาจากผู้ใช้ภายนอก ให้ sanitize/validate เสมอ
- ใช้ job queue + autoscale ถ้างานเยอะและต้องการความเสถียร
- บน Kubernetes ให้ตั้ง liveness/readiness probe ไปที่ `/health`
