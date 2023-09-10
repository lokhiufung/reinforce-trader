from dash_app.main import create_dash_app

if __name__ == '__main__':
    app = create_dash_app()
    app.run(host='0.0.0.0', port=8050, debug=True)
    