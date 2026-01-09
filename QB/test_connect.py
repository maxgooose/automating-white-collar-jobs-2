from quickbooks_desktop.session_manager import SessionManager


if __name__ == '__main__':
    qb = SessionManager(application_name="AutomationTest")
    qb.open_connection()


    print("connected to QB")
    print("Step 2")

    qb.begin_session()

    if qb.session_begun:
        print("Session started")

    print("step 3, close connection")
    qb.close_qb()
    print("connection closed")