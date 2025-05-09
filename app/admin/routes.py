from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Job, Application

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('jobs.index'))
    
    total_users = User.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    
    recent_jobs = Job.query.order_by(Job.date_posted.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_jobs=total_jobs,
                         total_applications=total_applications,
                         recent_jobs=recent_jobs)

@admin.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('jobs.index'))
    
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/admin/delete-user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action', 'error')
        return redirect(url_for('jobs.index'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))