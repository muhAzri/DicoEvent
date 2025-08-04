# DicoEvent - Asynchronous Task Implementation (Celery)

## Overview
Implementasi Asynchronous Task menggunakan Celery untuk mengirimkan email reminder event kepada pengguna yang telah memesan tiket.

## Fitur yang Diimplementasikan

### ✅ Basic (2 pts)
- ✅ Menggunakan library Celery
- ✅ Mengonfigurasi pengiriman email di proyek Django
- ✅ Menerapkan asynchronous task untuk mengirimkan email reminder event ke pengguna yang telah memesan tiket
- ✅ Pengujian mandatory Postman tidak ada yang error

### ✅ Skilled (3 pts)
- ✅ Mengirimkan email reminder event ke pengguna yang order tiket H-2 jam sebelum event

### ✅ Advanced (4 pts)
- ✅ Kredensial celery disimpan di environment variables (`CELERY_BROKER_URL`)
- ✅ Kredensial email disimpan di environment variables:
  - `MAIL_HOST`
  - `MAIL_PORT`  
  - `MAIL_USER`
  - `MAIL_PASSWORD`
- ✅ Menggunakan Docker dan Docker Compose

## Konfigurasi Environment Variables

Tambahkan environment variables berikut di file `.env`:

```bash
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0

# Email Configuration
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Cara Menjalankan

### 1. Dengan Docker Compose (Recommended)

```bash
# Build dan jalankan semua services
docker compose up --build

# Atau jalankan di background
docker compose up -d --build
```

Services yang akan berjalan:
- `web`: Django application (port 8000)
- `celery_worker`: Celery worker untuk memproses tasks
- `celery_beat`: Celery beat scheduler untuk periodic tasks
- `db`: PostgreSQL database (port 5433)
- `redis`: Redis broker (port 6379)
- `minio`: MinIO object storage (port 9000, 9001)

### 2. Manual Development

```bash
# Terminal 1: Jalankan Django
pipenv run python manage.py runserver

# Terminal 2: Jalankan Celery Worker
pipenv run celery -A DicoEvent worker --loglevel=info

# Terminal 3: Jalankan Celery Beat Scheduler
pipenv run celery -A DicoEvent beat --loglevel=info
```

## API Endpoints

### Manual Trigger Email Reminders
```
POST /api/events/send-reminders/
Authorization: Bearer <admin_or_superuser_token>
```

Response:
```json
{
    "message": "Event reminder task has been queued successfully",
    "task_id": "task-uuid"
}
```

## Cara Kerja Email Reminder

### Automatic Scheduling
1. **Celery Beat** menjalankan task `send_event_reminders` setiap 15 menit
2. Task mencari events yang akan dimulai dalam 2 jam (±15 menit buffer)
3. Untuk setiap event yang ditemukan, system mengirim email reminder ke semua pengguna yang sudah registrasi

### Manual Trigger
Admin/SuperUser dapat memicu pengiriman email reminder secara manual melalui API endpoint

### Email Content
Email reminder berisi informasi:
- Nama event
- Waktu mulai event
- Lokasi event
- Pesan reminder bahwa event akan dimulai dalam 2 jam

## Testing

### 1. Test Email Configuration
```bash
# Test Django email backend
pipenv run python manage.py shell

# Di dalam shell:
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email from DicoEvent.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### 2. Test Celery Task
```bash
# Test manual task execution
pipenv run python manage.py shell

# Di dalam shell:
from events.tasks import send_event_reminders
result = send_event_reminders.delay()
print(f"Task ID: {result.id}")
```

### 3. Test dengan Postman
1. Buat event baru yang akan dimulai dalam 2 jam
2. Buat user dan registrasi untuk event tersebut
3. Panggil API endpoint `POST /api/events/send-reminders/`
4. Cek email yang terdaftar untuk menerima reminder

## Troubleshooting

### Common Issues

1. **Celery Worker tidak jalan**
   - Pastikan Redis berjalan di port 6379
   - Check CELERY_BROKER_URL di environment variables

2. **Email tidak terkirim**
   - Verifikasi MAIL_* environment variables
   - Pastikan menggunakan App Password untuk Gmail
   - Check firewall dan network connectivity

3. **Docker issues**
   - Jalankan `docker compose down -v` untuk reset volumes
   - Build ulang dengan `docker compose build --no-cache`

### Logs Monitoring

```bash
# Docker logs
docker compose logs -f celery_worker
docker compose logs -f celery_beat

# Manual logs
pipenv run celery -A DicoEvent worker --loglevel=debug
```

## File Structure

```
DicoEvent/
├── DicoEvent/
│   ├── celery.py          # Celery configuration
│   ├── __init__.py        # Celery app import
│   └── settings.py        # Celery & Email settings
├── events/
│   ├── tasks.py           # Celery tasks for email reminders
│   ├── views.py           # API endpoint for manual trigger
│   └── urls.py            # URL routing
├── docker-compose.yml     # Docker services configuration
├── .env                   # Environment variables
└── Pipfile               # Python dependencies
```

## Performance Considerations

1. **Email Rate Limiting**: Consider implementing rate limiting untuk menghindari spam
2. **Database Queries**: Task menggunakan select_related untuk optimize database queries
3. **Error Handling**: Implement proper error handling dan retry mechanisms
4. **Monitoring**: Add logging dan monitoring untuk track task execution

## Security Notes

1. **Environment Variables**: Semua kredensial disimpan sebagai environment variables
2. **Email Authentication**: Gunakan App Password untuk Gmail, bukan password utama
3. **API Authentication**: Endpoint manual trigger hanya bisa diakses oleh Admin/SuperUser
4. **Data Privacy**: Email content tidak menyimpan informasi sensitif pengguna