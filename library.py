import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

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

def create_borrowing_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            borrower TEXT NOT NULL,
            returned INTEGER DEFAULT 0,
            FOREIGN KEY (book_id) REFERENCES books(id)
        );
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
        cursor.execute(
        "SELECT id FROM borrowings WHERE book_id = ?",
        (book_id,)
)

        if cursor.fetchone():
            print("Cannot delete a book with borrowing history")
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
        borrower = input("Enter borrower naem: ").strip()

        cursor.execute("SELECT * FROM books WHERE id = ?",(book_id,))
        book = cursor.fetchone()

        if not book:
            print("No book found")
            return

        if not borrower:
            print("Borrower name can not empty")
            return

        if book[3] <= 0:
            print("No copies available")
            return

        cursor.execute("""
            INSERT INTO borrowings(book_id, borrower)
            VALUES(?, ?)
        """,(book_id, borrower))
        
        cursor.execute("""
            UPDATE books
            SET quantity = quantity - 1
            WHERE id = ?
        """,(book_id,))

        conn.commit()
        print("Book borrowed succesfully")

    except ValueError:
        print("Enter a valid number")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")

def return_book():
    print("\n====RETURN BOOK====")

    try:
        book_id = int(input("Enter book id: "))
        borrower = input("Enter borrower name: ").strip()
        cursor.execute("SELECT * FROM books WHERE id = ?",(book_id,))
        book = cursor.fetchone()
        cursor.execute("""SELECT * FROM borrowings
            WHERE book_id =? AND borrower = ? AND returned = 0
        """,(book_id, borrower))
        borrow = cursor.fetchone()

        if not book:
            print("No book found")
            return
        if not borrow:
            print("No active borrowing found")
            return

        cursor.execute("""
            UPDATE borrowings
            SET returned = 1
            WHERE id = ?
        """,(borrow[0],))
        cursor.execute("""
            UPDATE books
            SET quantity = quantity + 1
            WHERE id = ?
        """,(book_id,))
        conn.commit()
        print("Book returned successfully")
    except ValueError:
        print("Enter a valid book id")
    except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")

def view_borrowing_history():
    print("\n====BORROWING HISTORY====")

    cursor.execute("""
        SELECT
            borrowings.id,
            books.title,
            borrowings.borrower,
            borrowings.returned
        FROM borrowings
        JOIN books
        ON borrowings.book_id = books.id
    """)

    records = cursor.fetchall()

    if not records:
        print("No borrowing history found")
        return

    for record in records:
        status = "Returned" if record[3] == 1 else "Borrowed"

        print(
            f"Borrowing ID: {record[0]} | "
            f"Book: {record[1]} | "
            f"Borrower: {record[2]} | "
            f"Status: {status}"
        )

def main():

    create_table()
    create_borrowing_table()

    while True:
        print("\n========== LIBRARY MANAGEMENT SYSTEM ==========")
        print("1. Add Book")
        print("2. View All Books")
        print("3. Search Book")
        print("4. Update Book")
        print("5. Delete Book")
        print("6. Borrow Book")
        print("7. Return Book")
        print("8. View Borrowing History")
        print("9. Exit")

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
            view_borrowing_history()
        elif choice == "9":
            print("Thank you for using the Library Management System!")
            break

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    try:
        main()
    finally:
        conn.close()