"""Views for the main blueprint."""
from datetime import datetime, timezone
from flask import render_template, jsonify, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.routes import main_bp
from app.services.task_service import TaskService
from app.services.travel_service import TravelService
from app.models.activity import Activity
from app import db

NO_AUTHORIZED = 'No autorizado'

@main_bp.route('/')
def index():
    """Index route."""
    pending_tasks = []
    upcoming_travels = []
    
    if current_user.is_authenticated:
        # Get pending tasks
        task_service = TaskService()
        pending_tasks = task_service.get_user_tasks(
            current_user,
            status='pending',
            limit=5
        )
        
        # Get upcoming travels
        travel_service = TravelService()
        upcoming_travels = travel_service.get_user_diaries(current_user)
        # limitar a 5
        now = datetime.now(timezone.utc)
        upcoming_travels = [
            travel for travel in upcoming_travels 
        ][:5]
    
    return render_template(
        'index.html',
        pending_tasks=pending_tasks,
        upcoming_travels=upcoming_travels
    )

@main_bp.route('/profile')
@login_required
def profile():
    """User profile route."""
    return render_template('profile.html', user=current_user)

@main_bp.route('/tasks')
@login_required
def tasks():
    """Tasks list route."""
    task_service = TaskService()
    
    # Get filter parameters
    category = request.args.get('category')
    status = request.args.get('status')
    
    # Get tasks with filters
    tasks = task_service.get_user_tasks(
        current_user,
        category=category,
        status=status
    )
    
    return render_template(
        'tasks/index.html',
        tasks=tasks,
        categories=TaskService.VALID_CATEGORIES,
        statuses=TaskService.VALID_STATUSES,
        selected_category=category,
        selected_status=status
    )

@main_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """Create new task route."""
    task_service = TaskService()
    
    try:
        # Get form data
        title = request.form['title']
        description = request.form.get('description')
        category = request.form['category']
        due_date_str = request.form.get('due_date')
        
        # Convert due_date string to datetime if provided
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            due_date = due_date.replace(tzinfo=timezone.utc)
        
        # Create task
        task_service.create_task(
            user=current_user,
            title=title,
            description=description,
            category=category,
            due_date=due_date
        )
        
        flash('Tarea creada exitosamente.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Error al crear la tarea.', 'danger')
    
    return redirect(url_for('main.tasks'))

@main_bp.route('/tasks/<int:task_id>')
@login_required
def get_task(task_id):
    """Get task details route."""
    task_service = TaskService()
    
    try:
        task = task_service.get_task_by_id(task_id)
        if task.user != current_user:
            return jsonify({'error': NO_AUTHORIZED}), 403
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'category': task.category,
            'status': task.status,
            'due_date': task.due_date.isoformat() if task.due_date else None
        })
    except ValueError:
        return jsonify({'error': 'Tarea no encontrada'}), 404

@main_bp.route('/tasks/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    """Update task route."""
    task_service = TaskService()
    
    try:
        # Primero obtener la tarea existente
        task = task_service.get_task_by_id(task_id)
        if task.user != current_user:
            flash(NO_AUTHORIZED, 'danger')
            return redirect(url_for('main.tasks'))
        
        # Construir el diccionario de actualización solo con los campos que cambiaron
        update_data = {}
        
        # Verificar cada campo del formulario
        form_title = request.form.get('title')
        if form_title and form_title != task.title:
            update_data['title'] = form_title
            
        form_description = request.form.get('description')
        if form_description != task.description:  # description puede ser vacío
            update_data['description'] = form_description
            
        form_category = request.form.get('category')
        if form_category and form_category != task.category:
            update_data['category'] = form_category
            
        form_status = request.form.get('status')
        if form_status and form_status != task.status:
            update_data['status'] = form_status
        
        # Manejar la fecha de vencimiento
        form_due_date = request.form.get('due_date')
        current_due_date = task.due_date.strftime('%Y-%m-%d') if task.due_date else None
        
        if form_due_date != current_due_date:
            if form_due_date:
                try:
                    due_date = datetime.strptime(form_due_date, '%Y-%m-%d')
                    due_date = due_date.replace(tzinfo=timezone.utc)
                    update_data['due_date'] = due_date
                except ValueError:
                    flash('Formato de fecha inválido', 'danger')
                    return redirect(url_for('main.tasks'))
            else:
                update_data['due_date'] = None
        
        # Solo actualizar si hay cambios
        if update_data:
            task_service.update_task(task, update_data)
            flash('Tarea actualizada exitosamente.', 'success')
        else:
            flash('No se detectaron cambios en la tarea.', 'info')
            
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Error al actualizar la tarea.', 'danger')
    
    return redirect(url_for('main.tasks'))

@main_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Mark task as completed route."""
    task_service = TaskService()
    
    try:
        task = task_service.get_task_by_id(task_id)
        if task.user != current_user:
            return jsonify({'error': NO_AUTHORIZED}), 403
        
        task_service.mark_task_completed(task)
        return jsonify({'message': 'Tarea completada exitosamente'})
    except ValueError:
        return jsonify({'error': 'Tarea no encontrada'}), 404

@main_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete task route."""
    task_service = TaskService()
    
    try:
        task = task_service.get_task_by_id(task_id)
        if task.user != current_user:
            return jsonify({'error': NO_AUTHORIZED}), 403
        
        task_service.delete_task(task)
        return jsonify({'message': 'Tarea eliminada exitosamente'})
    except ValueError:
        return jsonify({'error': 'Tarea no encontrada'}), 404

@main_bp.route('/travel')
@login_required
def travel():
    """Travel diaries list route."""
    travel_service = TravelService()
    travel_diaries = travel_service.get_user_diaries(current_user)
    
    return render_template(
        'travel/index.html',
        travel_diaries=travel_diaries
    )

@main_bp.route('/travel', methods=['POST'])
@login_required
def create_travel():
    """Create new travel diary route."""
    travel_service = TravelService()
    
    try:
        # Get form data
        title = request.form['title']
        location = request.form['location']
        description = request.form.get('description')
        start_date_str = request.form['start_date']
        end_date_str = request.form.get('end_date')
        
        # Convert dates to datetime
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        start_date = start_date.replace(tzinfo=timezone.utc)
        
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(tzinfo=timezone.utc)
        
        # Create travel diary
        travel_service.create_travel_diary(
            user=current_user,
            title=title,
            location=location,
            description=description,
            start_date=start_date,
            end_date=end_date
        )
        
        flash('Viaje creado exitosamente.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Error al crear el viaje.', 'danger')
    
    return redirect(url_for('main.travel'))

@main_bp.route('/travel/<int:diary_id>')
@login_required
def travel_detail(diary_id):
    """Travel diary detail route."""
    travel_service = TravelService()
    
    try:
        diary = travel_service.get_diary_by_id(diary_id)
        if diary.user != current_user:
            flash(NO_AUTHORIZED, 'danger')
            return redirect(url_for('main.travel'))
        
        return render_template(
            'travel/detail.html',
            diary=diary
        )
    except ValueError:
        flash('Viaje no encontrado.', 'danger')
        return redirect(url_for('main.travel'))

@main_bp.route('/travel/<int:diary_id>', methods=['GET'])
@login_required
def get_travel(diary_id):
    """Get travel diary details route."""
    travel_service = TravelService()
    
    try:
        diary = travel_service.get_diary_by_id(diary_id)
        if diary.user != current_user:
            return jsonify({'error': NO_AUTHORIZED}), 403
        
        return jsonify({
            'id': diary.id,
            'title': diary.title,
            'location': diary.location,
            'description': diary.description,
            'start_date': diary.start_date.isoformat(),
            'end_date': diary.end_date.isoformat() if diary.end_date else None
        })
    except ValueError:
        return jsonify({'error': 'Viaje no encontrado'}), 404

@main_bp.route('/travel/<int:diary_id>', methods=['POST'])
@login_required
def update_travel(diary_id):
    """Update travel diary route."""
    travel_service = TravelService()
    
    try:
        diary = travel_service.get_diary_by_id(diary_id)
        if diary.user != current_user:
            flash(NO_AUTHORIZED, 'danger')
            return redirect(url_for('main.travel'))
        
        # Get form data
        update_data = {
            'title': request.form['title'],
            'location': request.form['location'],
            'description': request.form.get('description')
        }
        
        # Handle dates
        start_date_str = request.form['start_date']
        end_date_str = request.form.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        start_date = start_date.replace(tzinfo=timezone.utc)
        update_data['start_date'] = start_date
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(tzinfo=timezone.utc)
            update_data['end_date'] = end_date
        
        travel_service.update_diary(diary, update_data)
        flash('Viaje actualizado exitosamente.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Error al actualizar el viaje.', 'danger')
    
    return redirect(url_for('main.travel_detail', diary_id=diary_id))

@main_bp.route('/travel/<int:diary_id>', methods=['DELETE'])
@login_required
def delete_travel(diary_id):
    """Delete travel diary route."""
    travel_service = TravelService()
    
    try:
        diary = travel_service.get_diary_by_id(diary_id)
        if diary.user != current_user:
            return jsonify({'error': NO_AUTHORIZED}), 403
        
        travel_service.delete_diary(diary)
        return jsonify({'message': 'Viaje eliminado exitosamente'})
    except ValueError:
        return jsonify({'error': 'Viaje no encontrado'}), 404

@main_bp.route('/travel/<int:diary_id>/activity', methods=['POST'])
@login_required
def create_activity(diary_id):
    """Create new activity route."""
    travel_service = TravelService()
    
    try:
        diary = travel_service.get_diary_by_id(diary_id)
        if diary.user != current_user:
            flash(NO_AUTHORIZED, 'danger')
            return redirect(url_for('main.travel'))
        
        # Get form data
        title = request.form['title']
        location = request.form.get('location')
        description = request.form.get('description')
        notes = request.form.get('notes')
        cost = request.form.get('cost')
        
        if cost:
            cost = float(cost)
        
        # Handle planned date and time
        date_str = request.form['planned_date']
        time_str = request.form['planned_time']
        planned_date = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        planned_date = planned_date.replace(tzinfo=timezone.utc)
        
        travel_service.add_activity(
            diary=diary,
            title=title,
            location=location,
            description=description,
            planned_date=planned_date,
            cost=cost,
            notes=notes
        )
        
        flash('Actividad creada exitosamente.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Error al crear la actividad.', 'danger')
    
    return redirect(url_for('main.travel_detail', diary_id=diary_id))

@main_bp.route('/travel/activity/<int:activity_id>', methods=['GET'])
@login_required
def get_activity(activity_id):
    """Get activity details route."""
    travel_service = TravelService()
    
    try:
        activity = travel_service.get_activity_by_id(activity_id)
        if activity.diary.user != current_user:
            return jsonify({'error': NO_AUTHORIZED}), 403
        
        return jsonify({
            'id': activity.id,
            'title': activity.title,
            'location': activity.location,
            'description': activity.description,
            'planned_date': activity.planned_date.isoformat(),
            'cost': activity.cost,
            'notes': activity.notes,
            'completed': activity.completed,
            'completion_notes': activity.completion_notes
        })
    except ValueError:
        return jsonify({'error': 'Actividad no encontrada'}), 404

@main_bp.route('/travel/activity/<int:activity_id>', methods=['POST'])
@login_required
def update_activity(activity_id):
    """Update activity route."""
    travel_service = TravelService()
    
    try:
        activity = travel_service.get_activity_by_id(activity_id)
        if activity.diary.user != current_user:
            flash(NO_AUTHORIZED, 'danger')
            return redirect(url_for('main.travel'))
        
        # Get form data
        update_data = {
            'title': request.form['title'],
            'location': request.form.get('location'),
            'description': request.form.get('description'),
            'notes': request.form.get('notes')
        }
        
        cost = request.form.get('cost')
        if cost:
            update_data['cost'] = float(cost)
        
        # Handle planned date and time
        date_str = request.form['planned_date']
        time_str = request.form['planned_time']
        planned_date = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        update_data['planned_date'] = planned_date.replace(tzinfo=timezone.utc)
        
        travel_service.update_activity(activity, update_data)
        flash('Actividad actualizada exitosamente.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Error al actualizar la actividad.', 'danger')
    
    return redirect(url_for('main.travel_detail', diary_id=activity.diary_id))

@main_bp.route('/travel/activity/<int:activity_id>/complete', methods=['POST'])
@login_required
def complete_activity(activity_id):
    """Mark activity as completed route."""
    travel_service = TravelService()
    
    try:
        activity = Activity.query.get(activity_id)
        if not activity:
            flash('No se encontró la actividad.', 'danger')
            return redirect(url_for('main.travel'))
            
        if activity.diary.user != current_user:
            flash('No tienes permiso para completar esta actividad.', 'danger')
            return redirect(url_for('main.travel_detail', diary_id=activity.diary_id))
        
        completion_notes = request.form.get('completion_notes')
        travel_service.mark_activity_completed(activity, completion_notes)
        
        flash('Actividad completada exitosamente.', 'success')
        return redirect(url_for('main.travel_detail', diary_id=activity.diary_id))
    except Exception as e:
        flash('Error al completar la actividad.', 'danger')
        return redirect(url_for('main.travel'))

@main_bp.route('/travel/activity/<int:activity_id>', methods=['DELETE'])
@login_required
def delete_activity(activity_id):
    """Delete activity route."""
    travel_service = TravelService()
    
    try:
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({'error': 'Actividad no encontrada'}), 404
            
        if activity.diary.user != current_user:
            return jsonify({'error': NO_AUTHORIZED}), 403
        
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({'message': 'Actividad eliminada exitosamente'})
    except Exception as e:
        return jsonify({'error': 'Error al eliminar la actividad'}), 500 