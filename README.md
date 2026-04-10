# SISApp-pyV2 🎓

An upgraded Student Information System built with Python and CustomTkinter. Version 2 introduces a fully integrated MySQL/MariaDB database backend, enhanced security, and improved data management features for a smoother user experience.

## ✨ Key Features
* **Modern GUI:** Built with `customtkinter` for a sleek interface.
* **Robust Database:** Fully integrated MySQL backend with connection pooling.
* **Secure Setup:** Uses `python-dotenv` to keep database credentials hidden and secure.
* **Smart Pagination (New in V2):** Loads and displays student records in manageable pages, ensuring the app remains lightning-fast even with thousands of entries!

---

## 🚀 How to Install and Run

### Prerequisites
Before you begin, ensure you have the following installed on your computer:
* **Python 3.8+**
* **MySQL** or **MariaDB Server** (running locally)

### Clone the Repository
Open your terminal and clone this project:
```bash
git clone [https://github.com/gitnsaen/SISApp-pyV2.git](https://github.com/gitnsaen/SISApp-pyV2.git)
cd SISApp-pyV2
```
### Set Up the Database
A database dump is included to help you get started instantly.

1. Open your terminal and log into your MySQL/MariaDB server:
```bash
mysql -u root -p
```
2. Create an empty database:
```bash
SQL
CREATE DATABASE sis_db;
exit;
```
3. Import the provided schema and sample data:
```bash
mysql -u root -p sis_db < database_with_data.sql
```
### Configure Environment Variables
To keep passwords secure, this app uses a .env file.
1. Create a file named .env in the root folder of the project.
2. Add your database credentials to it like this:
```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_database_password
DB_NAME=sis_db
```
### Install Dependencies
Install the required Python libraries using the provided requirements file:
```bash
pip install -r requirements.txt
```
### Launch the App!
Run the main Python file to start the application:
```bash
python main.py or python3 main.py
