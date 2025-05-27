"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.services.user_service import UserService

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        current_app.logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            flash('Por favor ingresa tu email y contraseña.', 'danger')
            return redirect(url_for('auth.login'))
        
        try:
            user = user_service.get_user_by_email(email)
            current_app.logger.info(f"User found: {user}")
            
            # Verificar si el usuario tiene password_hash
            if not user.password_hash:
                current_app.logger.error(f"User {email} has no password hash")
                flash('Error en la configuración de la cuenta. Contacta al administrador.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Verificar si el usuario está activo
            if not user.is_active:
                current_app.logger.warning(f"Inactive user attempted to login: {email}")
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'danger')
                return redirect(url_for('auth.login'))
            
            if user.check_password(password):
                current_app.logger.info(f"Password check passed for user: {email}")
                
                # Intentar login y capturar el resultado
                login_result = login_user(user, remember=remember)
                current_app.logger.info(f"Login result for {email}: {login_result}")
                
                if login_result:
                    flash('¡Bienvenido!', 'success')
                    next_page = request.args.get('next')
                    if not next_page or not next_page.startswith('/'):
                        next_page = url_for('main.index')
                    return redirect(next_page)
                else:
                    current_app.logger.error(f"Login failed for user {email} despite valid credentials")
                    flash('No se pudo iniciar sesión. Por favor intenta nuevamente.', 'danger')
            else:
                current_app.logger.warning(f"Invalid password for user: {email}")
                flash('Email o contraseña incorrectos.', 'danger')
        except ValueError as e:
            current_app.logger.error(f"ValueError during login: {str(e)}")
            flash('Usuario no encontrado.', 'danger')
        except Exception as e:
            current_app.logger.error(f"Unexpected error during login: {str(e)}")
            flash('Ocurrió un error al intentar iniciar sesión.', 'danger')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = user_service.create_user(
                username=username,
                email=email,
                password=password
            )
            current_app.logger.info(f"User registered successfully: {user.email}")
            flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            flash(str(e), 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route."""
    email = current_user.email
    logout_user()
    current_app.logger.info(f"User logged out: {email}")
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.index')) 