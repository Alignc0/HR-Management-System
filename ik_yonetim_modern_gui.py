import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# ===================== VERİ SINIFLARI =====================
class Departman:
    def __init__(self, departman_adi):
        self.departman_adi = departman_adi
        self.calisanlar = []

    def calisan_ekle(self, calisan):
        self.calisanlar.append(calisan)

    def calisan_sil(self, calisan):
        if calisan in self.calisanlar:
            self.calisanlar.remove(calisan)
            return True
        return False

class Calisan:
    def __init__(self, ad_soyad, email, telefon, maas, departman):
        self.ad_soyad = ad_soyad
        self.email = email
        self.telefon = telefon
        self.maas = maas
        self.departman = departman
        departman.calisan_ekle(self)

    def departman_degistir(self, yeni_departman):
        self.departman.calisan_sil(self)
        self.departman = yeni_departman
        yeni_departman.calisan_ekle(self)

# ===================== VERİ YÖNETİMİ =====================
class InsanKaynaklariSistemi:
    def __init__(self):
        self.departmanlar = {}
        self.veri_dosyasi = "ik_verileri.json"
        self.verileri_yukle()

    def departman_ekle(self, departman_adi):
        if departman_adi and departman_adi not in self.departmanlar:
            self.departmanlar[departman_adi] = Departman(departman_adi)
            self.verileri_kaydet()
            return True
        return False

    def departman_sil(self, departman_adi):
        # Departmanda çalışan varsa silme
        dep = self.departmanlar.get(departman_adi)
        if dep:
            if dep.calisanlar:
                return False
            del self.departmanlar[departman_adi]
            self.verileri_kaydet()
            return True
        return False

    def calisan_ekle(self, ad_soyad, email, telefon, maas, departman_adi):
        dep = self.departmanlar.get(departman_adi)
        if dep:
            Calisan(ad_soyad, email, telefon, maas, dep)
            self.verileri_kaydet()
            return True
        return False

    def calisan_sil(self, ad_soyad):
        for dep in self.departmanlar.values():
            for c in dep.calisanlar:
                if c.ad_soyad == ad_soyad:
                    dep.calisan_sil(c)
                    self.verileri_kaydet()
                    return True
        return False

    def calisan_ara(self, filtre):
        filtre = filtre.lower()
        return [c for d in self.departmanlar.values() for c in d.calisanlar if filtre in c.ad_soyad.lower()]

    def verileri_kaydet(self):
        veri = {
            "departmanlar": {
                dep_adi: [
                    {
                        "ad_soyad": c.ad_soyad,
                        "email": c.email,
                        "telefon": c.telefon,
                        "maas": c.maas
                    } for c in dep.calisanlar
                ] for dep_adi, dep in self.departmanlar.items()
            }
        }
        with open(self.veri_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)

    def verileri_yukle(self):
        if os.path.exists(self.veri_dosyasi):
            with open(self.veri_dosyasi, 'r', encoding='utf-8') as f:
                veri = json.load(f)
                for dep_adi, calisanlar in veri.get("departmanlar", {}).items():
                    self.departmanlar[dep_adi] = Departman(dep_adi)
                    for c in calisanlar:
                        Calisan(c.get("ad_soyad"), c.get("email"), c.get("telefon"), c.get("maas"), self.departmanlar[dep_adi])
        else:
            # İlk veri oluşturma
            for d in ["Muhasebe", "Satın Alma", "Pazarlama", "Dış Ticaret", "Ar-Ge"]:
                self.departman_ekle(d)
            for i in range(5):
                for d in self.departmanlar:
                    self.calisan_ekle(f"{d} Personel {i+1}", f"{d.lower()}{i+1}@firma.com", f"05{i}1234567{i}", 10000+i*500, d)

# ===================== ARAYÜZ =====================
class IKApp:
    def __init__(self, root):
        self.sistem = InsanKaynaklariSistemi()
        self.root = root
        self.root.title("İK Yönetim Paneli")
        self.root.geometry("900x650")

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), rowheight=28)
        style.configure("TButton", font=("Arial", 10))
        style.configure("TLabel", font=("Arial", 10))

        self.kontrol_cubugu = ttk.Frame(self.root)
        self.kontrol_cubugu.pack(pady=10)

        ttk.Button(self.kontrol_cubugu, text="Çalışan Ekle", command=self.calisan_ekle).grid(row=0, column=0, padx=5)
        ttk.Button(self.kontrol_cubugu, text="Çalışan Sil", command=self.calisan_sil).grid(row=0, column=1, padx=5)
        ttk.Button(self.kontrol_cubugu, text="Departman Ekle", command=self.departman_ekle).grid(row=0, column=2, padx=5)
        ttk.Button(self.kontrol_cubugu, text="Departman Sil", command=self.departman_sil).grid(row=0, column=3, padx=5)
        ttk.Button(self.kontrol_cubugu, text="Yenile", command=self.liste_guncelle).grid(row=0, column=4, padx=5)
        ttk.Button(self.kontrol_cubugu, text="CSV'ye Aktar", command=self.csv_aktar).grid(row=0, column=5, padx=5)

        self.arama_girdisi = ttk.Entry(self.kontrol_cubugu)
        self.arama_girdisi.grid(row=0, column=6, padx=5)
        ttk.Button(self.kontrol_cubugu, text="Ara", command=self.calisan_ara).grid(row=0, column=7, padx=5)

        self.tree = ttk.Treeview(self.root, columns=("Ad Soyad", "Email", "Telefon", "Maaş", "Departman"), show='headings')
        for col in ("Ad Soyad", "Email", "Telefon", "Maaş", "Departman"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=150)
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

        self.liste_guncelle()

    def liste_guncelle(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for dep in self.sistem.departmanlar.values():
            for c in dep.calisanlar:
                self.tree.insert("", "end", values=(c.ad_soyad, c.email, c.telefon, c.maas, dep.departman_adi))

    def calisan_ekle(self):
        ad = simpledialog.askstring("Ad Soyad", "Ad Soyad:")
        if not ad:
            return
        email = simpledialog.askstring("Email", "Email:")
        telefon = simpledialog.askstring("Telefon", "Telefon:")
        try:
            maas_str = simpledialog.askstring("Maaş", "Maaş:")
            maas = float(maas_str)
        except:
            messagebox.showerror("Hata", "Geçerli bir maaş giriniz.")
            return
        dep = simpledialog.askstring("Departman", "Departman:")
        if not dep:
            return
        if self.sistem.calisan_ekle(ad, email, telefon, maas, dep):
            messagebox.showinfo("Başarılı", "Çalışan eklendi.")
            self.liste_guncelle()
        else:
            messagebox.showerror("Hata", "Departman bulunamadı.")

    def calisan_sil(self):
        secili = self.tree.selection()
        if secili:
            ad = self.tree.item(secili[0])["values"][0]
            if self.sistem.calisan_sil(ad):
                messagebox.showinfo("Silindi", f"{ad} silindi.")
                self.liste_guncelle()
            else:
                messagebox.showerror("Hata", "Silinemedi.")
        else:
            messagebox.showwarning("Uyarı", "Lütfen silinecek çalışanı seçin.")

    def calisan_ara(self):
        filtre = self.arama_girdisi.get()
        if not filtre:
            self.liste_guncelle()
            return
        sonuc = self.sistem.calisan_ara(filtre)
        self.tree.delete(*self.tree.get_children())
        for c in sonuc:
            self.tree.insert("", "end", values=(c.ad_soyad, c.email, c.telefon, c.maas, c.departman.departman_adi))

    def csv_aktar(self):
        dosya = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV dosyası", "*.csv")])
        if not dosya:
            return
        with open(dosya, "w", encoding="utf-8") as f:
            f.write("Ad Soyad,Email,Telefon,Maaş,Departman\n")
            for dep in self.sistem.departmanlar.values():
                for c in dep.calisanlar:
                    f.write(f"{c.ad_soyad},{c.email},{c.telefon},{c.maas},{dep.departman_adi}\n")
        messagebox.showinfo("Başarılı", "Veriler CSV dosyasına aktarıldı.")

    def departman_ekle(self):
        dep_adi = simpledialog.askstring("Departman Ekle", "Departman Adı:")
        if not dep_adi:
            return
        if self.sistem.departman_ekle(dep_adi):
            messagebox.showinfo("Başarılı", f"{dep_adi} departmanı eklendi.")
            self.liste_guncelle()
        else:
            messagebox.showerror("Hata", "Departman adı zaten var veya geçersiz.")

    def departman_sil(self):
        dep_adi = simpledialog.askstring("Departman Sil", "Silinecek Departman Adı:")
        if not dep_adi:
            return
        sonuc = self.sistem.departman_sil(dep_adi)
        if sonuc:
            messagebox.showinfo("Başarılı", f"{dep_adi} departmanı silindi.")
            self.liste_guncelle()
        else:
            messagebox.showerror("Hata", f"{dep_adi} departmanı silinemedi. (Departmanda çalışan olabilir ya da departman yok.)")

# ===================== BAŞLAT =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = IKApp(root)
    root.mainloop()
