import datetime
import json
import os
from typing import Dict, List

class BankAccount:
    def __init__(self, account_number: str, account_holder: str, initial_balance: float = 0.0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = initial_balance
        self.transaction_history = []
        self.created_at = datetime.datetime.now()
        self.add_transaction("Akun dibuat", initial_balance, initial_balance)
    
    def add_transaction(self, transaction_type: str, amount: float, new_balance: float):
        """Mencatat riwayat transaksi"""
        transaction = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': transaction_type,
            'amount': amount,
            'balance': new_balance
        }
        self.transaction_history.append(transaction)
    
    def deposit(self, amount: float) -> bool:
        """Menyimpan uang ke akun"""
        if amount <= 0:
            print("Jumlah deposit harus lebih dari 0.")
            return False
        
        self.balance += amount
        self.add_transaction("Deposit", amount, self.balance)
        return True
    
    def withdraw(self, amount: float) -> bool:
        """Menarik uang dari akun"""
        if amount <= 0:
            print("Jumlah penarikan harus lebih dari 0.")
            return False
        
        if amount > self.balance:
            print("Saldo tidak cukup.")
            return False
        
        self.balance -= amount
        self.add_transaction("Penarikan", amount, self.balance)
        return True
    
    def transfer(self, target_account, amount: float) -> bool:
        """Transfer uang ke akun lain"""
        if amount <= 0:
            print("Jumlah transfer harus lebih dari 0.")
            return False
        
        if amount > self.balance:
            print("Saldo tidak cukup untuk transfer.")
            return False
        
        # Tarik dari akun pengirim
        self.balance -= amount
        self.add_transaction(f"Transfer ke {target_account.account_number}", -amount, self.balance)
        
        # Tambah ke akun penerima
        target_account.balance += amount
        target_account.add_transaction(f"Transfer dari {self.account_number}", amount, target_account.balance)
        
        return True
    
    def get_account_info(self) -> str:
        """Mendapatkan informasi akun"""
        info = f"\n{'='*40}"
        info += f"\nInformasi Akun"
        info += f"\n{'='*40}"
        info += f"\nNomor Akun: {self.account_number}"
        info += f"\nNama Pemilik: {self.account_holder}"
        info += f"\nSaldo: Rp {self.balance:,.2f}"
        info += f"\nTanggal Pembuatan: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        info += f"\n{'='*40}"
        return info
    
    def get_transaction_history(self) -> str:
        """Mendapatkan riwayat transaksi"""
        if not self.transaction_history:
            return "Belum ada transaksi."
        
        history = f"\n{'='*60}"
        history += f"\nRiwayat Transaksi - {self.account_holder}"
        history += f"\n{'='*60}"
        
        for i, transaction in enumerate(self.transaction_history, 1):
            amount_str = f"Rp {transaction['amount']:+,.2f}"
            history += f"\n{i}. {transaction['date']} | {transaction['type']:20} | {amount_str:15} | Saldo: Rp {transaction['balance']:,.2f}"
        
        history += f"\n{'='*60}"
        return history
    
    def to_dict(self) -> Dict:
        """Mengubah objek akun menjadi dictionary untuk disimpan"""
        return {
            'account_number': self.account_number,
            'account_holder': self.account_holder,
            'balance': self.balance,
            'transaction_history': self.transaction_history,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Membuat objek akun dari dictionary"""
        account = cls(data['account_number'], data['account_holder'], data['balance'])
        account.transaction_history = data['transaction_history']
        account.created_at = datetime.datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
        return account


class SimpleBankSystem:
    def __init__(self, data_file: str = "bank_data.json"):
        self.data_file = data_file
        self.accounts = {}
        self.load_data()
    
    def generate_account_number(self) -> str:
        """Menghasilkan nomor akun baru"""
        if not self.accounts:
            return "100001"
        
        # Cari nomor akun terbesar
        max_account = max([int(acc_num) for acc_num in self.accounts.keys()])
        return str(max_account + 1)
    
    def create_account(self, account_holder: str, initial_deposit: float = 0.0) -> BankAccount:
        """Membuat akun baru"""
        if initial_deposit < 0:
            print("Deposit awal tidak boleh negatif.")
            return None
        
        account_number = self.generate_account_number()
        new_account = BankAccount(account_number, account_holder, initial_deposit)
        self.accounts[account_number] = new_account
        self.save_data()
        
        print(f"\n✓ Akun berhasil dibuat!")
        print(new_account.get_account_info())
        return new_account
    
    def find_account(self, account_number: str) -> BankAccount:
        """Mencari akun berdasarkan nomor akun"""
        return self.accounts.get(account_number)
    
    def delete_account(self, account_number: str) -> bool:
        """Menghapus akun"""
        if account_number not in self.accounts:
            print("Akun tidak ditemukan.")
            return False
        
        # Cek saldo sebelum menghapus
        if self.accounts[account_number].balance > 0:
            print("Tidak dapat menghapus akun dengan saldo positif.")
            return False
        
        del self.accounts[account_number]
        self.save_data()
        print(f"Akun {account_number} berhasil dihapus.")
        return True
    
    def list_all_accounts(self) -> str:
        """Menampilkan semua akun"""
        if not self.accounts:
            return "Belum ada akun yang terdaftar."
        
        list_str = f"\n{'='*60}"
        list_str += f"\nDaftar Semua Akun"
        list_str += f"\n{'='*60}"
        list_str += f"\n{'No.':<6} {'No. Akun':<12} {'Nama Pemilik':<20} {'Saldo':<15}"
        list_str += f"\n{'-'*60}"
        
        for i, (acc_num, account) in enumerate(self.accounts.items(), 1):
            list_str += f"\n{i:<6} {acc_num:<12} {account.account_holder:<20} Rp {account.balance:,.2f}"
        
        list_str += f"\n{'='*60}"
        return list_str
    
    def save_data(self):
        """Menyimpan data ke file JSON"""
        data = {
            'accounts': {acc_num: account.to_dict() for acc_num, account in self.accounts.items()}
        }
        
        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=4)
    
    def load_data(self):
        """Memuat data dari file JSON"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
            
            for acc_num, acc_data in data['accounts'].items():
                self.accounts[acc_num] = BankAccount.from_dict(acc_data)
        except Exception as e:
            print(f"Error loading data: {e}")


def display_menu():
    """Menampilkan menu utama"""
    print("\n" + "="*50)
    print("SISTEM PERBANKAN SEDERHANA")
    print("="*50)
    print("1. Buat Akun Baru")
    print("2. Deposit")
    print("3. Penarikan")
    print("4. Transfer")
    print("5. Informasi Akun")
    print("6. Riwayat Transaksi")
    print("7. Tampilkan Semua Akun")
    print("8. Hapus Akun")
    print("9. Keluar")
    print("="*50)


def main():
    bank = SimpleBankSystem()
    
    while True:
        display_menu()
        
        try:
            choice = input("\nPilih menu (1-9): ").strip()
            
            if choice == "1":
                # Buat akun baru
                print("\n--- BUAT AKUN BARU ---")
                name = input("Masukkan nama lengkap: ").strip()
                if not name:
                    print("Nama tidak boleh kosong.")
                    continue
                
                try:
                    initial_deposit = float(input("Deposit awal (Rp): ").strip() or "0")
                except ValueError:
                    print("Jumlah deposit harus angka.")
                    continue
                
                bank.create_account(name, initial_deposit)
            
            elif choice == "2":
                # Deposit
                print("\n--- DEPOSIT ---")
                acc_num = input("Masukkan nomor akun: ").strip()
                account = bank.find_account(acc_num)
                
                if not account:
                    print("Akun tidak ditemukan.")
                    continue
                
                try:
                    amount = float(input("Jumlah deposit (Rp): ").strip())
                except ValueError:
                    print("Jumlah deposit harus angka.")
                    continue
                
                if account.deposit(amount):
                    bank.save_data()
                    print(f"\n✓ Deposit berhasil! Saldo baru: Rp {account.balance:,.2f}")
            
            elif choice == "3":
                # Penarikan
                print("\n--- PENARIKAN ---")
                acc_num = input("Masukkan nomor akun: ").strip()
                account = bank.find_account(acc_num)
                
                if not account:
                    print("Akun tidak ditemukan.")
                    continue
                
                try:
                    amount = float(input("Jumlah penarikan (Rp): ").strip())
                except ValueError:
                    print("Jumlah penarikan harus angka.")
                    continue
                
                if account.withdraw(amount):
                    bank.save_data()
                    print(f"\n✓ Penarikan berhasil! Saldo baru: Rp {account.balance:,.2f}")
            
            elif choice == "4":
                # Transfer
                print("\n--- TRANSFER ---")
                from_acc_num = input("Masukkan nomor akun pengirim: ").strip()
                from_account = bank.find_account(from_acc_num)
                
                if not from_account:
                    print("Akun pengirim tidak ditemukan.")
                    continue
                
                to_acc_num = input("Masukkan nomor akun penerima: ").strip()
                to_account = bank.find_account(to_acc_num)
                
                if not to_account:
                    print("Akun penerima tidak ditemukan.")
                    continue
                
                if from_acc_num == to_acc_num:
                    print("Tidak dapat transfer ke akun sendiri.")
                    continue
                
                try:
                    amount = float(input("Jumlah transfer (Rp): ").strip())
                except ValueError:
                    print("Jumlah transfer harus angka.")
                    continue
                
                if from_account.transfer(to_account, amount):
                    bank.save_data()
                    print(f"\n✓ Transfer berhasil!")
                    print(f"Saldo Anda: Rp {from_account.balance:,.2f}")
            
            elif choice == "5":
                # Informasi akun
                print("\n--- INFORMASI AKUN ---")
                acc_num = input("Masukkan nomor akun: ").strip()
                account = bank.find_account(acc_num)
                
                if account:
                    print(account.get_account_info())
                else:
                    print("Akun tidak ditemukan.")
            
            elif choice == "6":
                # Riwayat transaksi
                print("\n--- RIWAYAT TRANSAKSI ---")
                acc_num = input("Masukkan nomor akun: ").strip()
                account = bank.find_account(acc_num)
                
                if account:
                    print(account.get_transaction_history())
                else:
                    print("Akun tidak ditemukan.")
            
            elif choice == "7":
                # Tampilkan semua akun
                print(bank.list_all_accounts())
            
            elif choice == "8":
                # Hapus akun
                print("\n--- HAPUS AKUN ---")
                acc_num = input("Masukkan nomor akun: ").strip()
                confirm = input(f"Apakah Anda yakin ingin menghapus akun {acc_num}? (ya/tidak): ").strip().lower()
                
                if confirm == "ya":
                    bank.delete_account(acc_num)
                else:
                    print("Penghapusan dibatalkan.")
            
            elif choice == "9":
                # Keluar
                print("\nTerima kasih telah menggunakan sistem perbankan sederhana.")
                print("Data telah disimpan secara otomatis.")
                break
            
            else:
                print("Pilihan tidak valid. Silakan pilih 1-9.")
        
        except KeyboardInterrupt:
            print("\n\nProgram dihentikan.")
            break
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")


if __name__ == "__main__":
    main()