from app import app

if __name__ == '__main__':
    # Production mode - debug disabled
    app.run(host='0.0.0.0', port=5000, debug=False)
