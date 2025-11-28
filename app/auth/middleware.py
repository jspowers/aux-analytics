from flask import session, redirect, url_for, request, render_template

def setup_auth(app):
    """Setup authentication middleware"""

    @app.before_request
    def check_auth():
        # Allow access to login page and static files
        if request.endpoint in ['login', 'static']:
            return

        # Check if user is authenticated
        if not session.get('authenticated'):
            return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            password = request.form.get('password')
            if password == app.config['APP_PASSWORD']:
                session['authenticated'] = True
                session.permanent = True
                return redirect(url_for('main.index'))
            else:
                return render_template('login.html', error='Invalid password')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('authenticated', None)
        return redirect(url_for('login'))
