import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()


def create_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity >= 0)
        )
    """)
    conn.commit()

def add_book():
    print("\n====ADD BOOK====")
    title = input("Enter book title: ")
    author = input("Enter author name: ")

    if not title or not author:
        print("Title and Author cannot be empty")
        return
    try:
        quantity = int(input("Enter book quantity: "))

        if quantity <= 0:
            print("Quantity must be graeter than zero!")
            return

        cursor.execute("""
            INSERT INTO books(title, author, quantity)
            VALUES (?, ?, ?)
        """, (title, author, quantity))

        conn.commit()
        print("Book added successfully!")

    except ValueError:
        print("Invalid input try again!")
        

def view_books():
    print("\n====ALL BOOKS====")

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    if not books:
        print("No books found.")
        return

    for book in books:
        print(
            f"ID: {book[0]} | "
            f"Title: {book[1]} | "
            f"Author: {book[2]} | "
            f"Available: {book[3]}"
        )
    

def search_book():
    print("\n====SEARCH BOOKS====")

    keyword = input("Enter book title or author: ").strip()

    if not keyword:
        print("Search cannot be empty")
        return

    cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ?
    """,(f"%{keyword}%", f"%{keyword}%"))

    books = cursor.fetchall()

    if not books:
        print("No maching books found")
        return

    for book in books:
        print(
              f"ID: {book[0]} | "
              f"Title: {book[1]} | "
              f"Author: {book[2]} | "
              f"Available: {book[3]}"
              )

def update_book():
    print("\n====UPDATE BOOKS====")

    try:
        book_id = int(input("Enter book id: "))
        cursor.execute("SELECT * FROM books WHERE id = ?",(book_id,))
        book = cursor.fetchone()

        if not book:
            print("No book found")
            return

        print(f"Title: {book[1]}"
              f"Author: {book[2]}"
              f"Quantity: {book[3]}")

        title = input("New title(press Enter to keep current): ")
        author = input("New author(press Enter to keep current): ")
        quantity_input = input("New quantity(press Enter to keep current): ")

        title = title if title else book[1]
        author = author if author else book[2]

        if quantity_input:
            quantity = int(quantity_input)

            if quantity < 0:
                print("Qiuantity cannot be less than Zero")
                return
        else:
            quantity = book[3]
        cursor.execute("""
            UPDATE books
            SET title = ?, author = ?, quantity = ?
            WHERE id =?
        """,(title, author, quantity, book_id))
        conn.commit()
        print("Book added successsfully")
    except ValueError:
        print("Please enter valid numbers")


def delete_book():
    print("\n====DELETE BOOK====")

    try:
        book_id = int(input("Enter book id: "))

        cursor.execute("SELECT * FROM books WHERE id = ?",(book_id,))
        book = cursor.fetchone()

        if not book:
            print("No book found")
            return

        confirm = input(f"Delete '{book[1]}' ?(yes/no): ").strip().lower()
        if confirm == "yes":
            cursor.execute("DELETE FROM books WHERE id = ?",(book_id,))
            conn.commit()
            print("Deletion successfull")
        else:
            print("Deletion cancelled")
    except ValueError:
        print("Please enter a valid number")

        

def borrow_book():
    print("\n====BORROW BOOK====")

    try:
        book_id = int(input("Enter book id: "))

        cursor.execute("SELECT * FROM books WHERE id = ?",(book_id,))
        book = cursor.fetchone()

        if not book:
            print("No book found")
            return

        if book[3] <= 0:
            print("No copies available")
            return
        cursor.execute("""
            UPDATE books
            SET quantity = quantity - 1
            WHERE id = ?
        """,(book_id,))

        conn.commit()
        print("Book borrowed succesfully")

    except ValueError:
        print("Enter a valid number")

def return_book():
    print("\n====RETURN BOOK====")

    try:
        book_id = int(input("Enter book id: "))

        cursor.execute("SELECT * FROM books WHERE id = ?",(book_id,))
        book = cursor.fetchone()

        if not book:
            print("No book found")
            return
        cursor.execute("""
            UPDATE books
            SET quantity = quantity + 1
            WHERE id = ?
        """,(book_id,))
        conn.commit()
        print("Book returned successfully")
    except ValueError:
        print("Enter a valid book id")

def main():

    create_table()
    
    while True:
        print("\n========== LIBRARY MANAGEMENT SYSTEM ==========")
        print("1. Add Book")
        print("2. View All Books")
        print("3. Search Book")
        print("4. Update Book")
        print("5. Delete Book")
        print("6. Borrow Book")
        print("7. Return Book")
        print("8. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            add_book()

        elif choice == "2":
            view_books()

        elif choice == "3":
            search_book()

        elif choice == "4":
            update_book()

        elif choice == "5":
            delete_book()

        elif choice == "6":
            borrow_book()

        elif choice == "7":
            return_book()

        elif choice == "8":
            print("Thank you for using the Library Management System!")
            break

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    try:
        main()
    finally:
        conn.close()