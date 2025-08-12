from database import init_db, add_user, add_message, get_history

def main():
    conn = init_db()
    add_user(conn, "alice")
    add_message(conn, "alice", "hell")
    add_message(conn, "alice", "hello world")
    print(get_history(conn, "alice"))
    conn.close()

if __name__ == "__main__":
    main()