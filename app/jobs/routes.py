from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Job, Application
from datetime import datetime

jobs = Blueprint('jobs', __name__)

@jobs.route('/')
def index():
    featured_jobs = Job.query.order_by(Job.date_posted.desc()).limit(3).all()
    return render_template('jobs/index.html', jobs=featured_jobs)

@jobs.route('/browse')
def browse():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    job_type = request.args.get('type', '')
    
    jobs_query = Job.query
    
    if query:
        jobs_query = jobs_query.filter(
            (Job.title.ilike(f'%{query}%')) | 
            (Job.description.ilike(f'%{query}%'))
        )
    
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        jobs_query = jobs_query.filter(Job.job_type == job_type)
    
    jobs = jobs_query.order_by(Job.date_posted.desc()).paginate(page=page, per_page=10)
    
    return render_template('jobs/browse.html', 
                         jobs=jobs,
                         query=query,
                         location=location,
                         job_type=job_type)

@jobs.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    has_applied = False
    
    if current_user.is_authenticated and not current_user.is_employer:
        has_applied = Application.query.filter_by(
            user_id=current_user.id,
            job_id=job.id
        ).first() is not None
    
    return render_template('jobs/job_detail.html', job=job, has_applied=has_applied)

@jobs.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if not current_user.is_employer:
        flash('Only employers can post jobs', 'error')
        return redirect(url_for('jobs.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        salary = request.form.get('salary')
        job_type = request.form.get('job_type')
        
        job = Job(
            title=title,
            description=description,
            location=location,
            salary=salary,
            job_type=job_type,
            user_id=current_user.id
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs.job_detail', job_id=job.id))
    
    return render_template('jobs/post_job.html')

@jobs.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply(job_id):
    if current_user.is_employer:
        flash('Employers cannot apply for jobs', 'error')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    job = Job.query.get_or_404(job_id)
    
    # Check if already applied
    existing_application = Application.query.filter_by(
        user_id=current_user.id,
        job_id=job.id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job.id))
    
    # Handle file upload would go here (S3 or local storage)
    resume_url = "path/to/resume.pdf"  # Replace with actual upload logic
    
    application = Application(
        message=request.form.get('message'),
        resume_url=resume_url,
        user_id=current_user.id,
        job_id=job.id
    )
    
    db.session.add(application)
    db.session.commit()
    
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('jobs.job_detail', job_id=job.id))

@jobs.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_employer:
        jobs_posted = Job.query.filter_by(user_id=current_user.id).all()
        applications = []
        for job in jobs_posted:
            applications.extend(job.applications)
        return render_template('jobs/dashboard.html', 
                            jobs=jobs_posted,
                            applications=applications,
                            is_employer=True)
    else:
        applications = Application.query.filter_by(user_id=current_user.id).all()
        return render_template('jobs/dashboard.html',
                            applications=applications,
                            is_employer=False)