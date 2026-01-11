from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .models import Student, Attendance
from datetime import datetime
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
import numpy as np

# Import our recognition utility (which handles the library presence)
from .utils import compare_faces, INSIGHTFACE_AVAILABLE

def home(request):
    students = Student.objects.all()
    recent_attendance = Attendance.objects.order_by('-date', '-time')[:10]
    return render(request, 'core/home.html', {
        'students': students,
        'recent_attendance': recent_attendance,
        'insightface_available': INSIGHTFACE_AVAILABLE
    })

def mark_attendance(request):
    if request.method == 'POST' and request.FILES.get('group_photo'):
        if not INSIGHTFACE_AVAILABLE:
            return render(request, 'core/result.html', {
                'error': 'The face recognition library (InsightFace) is currently not installed. Attendance cannot be processed via photo.'
            })
            
        # Re-importing here if available to avoid crashing if it fails during global load
        from .utils import face_app
            
        group_photo = request.FILES['group_photo']
        fs = FileSystemStorage()
        filename = fs.save('temp_group_photo.jpg', group_photo)
        filepath = fs.path(filename)
        
        # Load known embeddings from DB
        known_students = Student.objects.exclude(embedding__isnull=True)
        known_embeddings = {s.name: np.frombuffer(s.embedding, dtype=np.float32) for s in known_students}
        
        if not known_embeddings:
            return render(request, 'core/result.html', {'error': 'No student face patterns found in the database. Please add students with photos first.'})
            
        import cv2
        # Process group photo
        img = cv2.imread(filepath)
        faces = face_app.get(img)
        
        found_names = set()
        for face in faces:
            name, score = compare_faces(face.embedding, known_embeddings)
            if name:
                found_names.add(name)
        
        # Mark present and absent
        all_students = Student.objects.all()
        date_now = datetime.now().date()
        time_now = datetime.now().time()
        
        results = []
        for student in all_students:
            status = 'Present' if student.name in found_names else 'Absent'
            Attendance.objects.create(
                student=student,
                status=status,
                date=date_now,
                time=time_now
            )
            results.append({'name': student.name, 'status': status})
            
        # Cleanup temp file
        fs.delete(filename)
        
        return render(request, 'core/result.html', {
            'results': results,
            'date': date_now
        })
        
    return redirect('home')

def export_attendance_excel(request):
    queryset = Attendance.objects.order_by('-date', '-time')
    
    data = []
    for record in queryset:
        data.append({
            'Student Name': record.student.name,
            'Status': record.status,
            'Date': record.date,
            'Time': record.time,
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=attendance_report.xlsx'
    
    return response
