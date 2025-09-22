from website import create_app

app = create_app()

# Inject test accounts (development only)
from testaccount import inject_test_accounts
inject_test_accounts(app)

if __name__ == '__main__': 
    app.run(debug=True)