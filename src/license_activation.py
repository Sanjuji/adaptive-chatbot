#!/usr/bin/env python3
"""
License Activation Interface for Adaptive Chatbot
"""

import tkinter as tk
from tkinter import messagebox, ttk
from monetization_system import LicenseManager, PricingCalculator

class LicenseActivationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Adaptive Chatbot - License Activation")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.license_manager = LicenseManager()
        self.pricing_calc = PricingCalculator()
        
        self.create_widgets()
        self.update_license_info()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🤖 Adaptive Chatbot Professional",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # License info section
        info_frame = tk.LabelFrame(main_frame, text="Current License Status", padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.license_info_text = tk.Text(info_frame, height=6, wrap=tk.WORD)
        self.license_info_text.pack(fill=tk.X)
        
        # Activation section  
        activation_frame = tk.LabelFrame(main_frame, text="Activate License", padx=10, pady=10)
        activation_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(activation_frame, text="License Key:").pack(anchor=tk.W)
        self.license_key_entry = tk.Entry(activation_frame, width=50, font=("Courier", 11))
        self.license_key_entry.pack(fill=tk.X, pady=(5, 10))
        
        activate_btn = tk.Button(
            activation_frame, 
            text="Activate License",
            command=self.activate_license,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2
        )
        activate_btn.pack(fill=tk.X)
        
        # Pricing section
        pricing_frame = tk.LabelFrame(main_frame, text="Purchase License", padx=10, pady=10)
        pricing_frame.pack(fill=tk.X)
        
        pricing_text = """
Professional License: ₹4,999 (One-time)
• Unlimited voice and text chat • Commercial use
• 10,000 knowledge entries • Email support

Business License: ₹9,999 (One-time)  
• Everything in Professional • Multi-machine deployment
• 50,000 knowledge entries • Priority support

Contact: your-email@example.com | Phone: +91-XXXXXXXXXX
        """
        
        pricing_label = tk.Label(pricing_frame, text=pricing_text, justify=tk.LEFT)
        pricing_label.pack(anchor=tk.W)
    
    def update_license_info(self):
        """Update license information display"""
        info = self.license_manager.get_license_info()
        
        info_text = f"""
License Type: {info['license_type'].title()}
Status: {"✅ Valid" if info['valid'] else "❌ " + info['message']}
Machine ID: {info['machine_id']}
"""
        
        if info['license_type'] == 'trial':
            info_text += f"Days Remaining: {info.get('days_remaining', 0)}\n"
        
        # Add feature info
        features = info.get('features', {})
        info_text += f"\nFeatures Available:"
        info_text += f"\n• Voice Chat: {'✅' if features.get('voice_chat') else '❌'}"
        info_text += f"\n• Commercial Use: {'✅' if features.get('commercial_use') else '❌'}"
        info_text += f"\n• Max Knowledge: {features.get('max_knowledge_entries', 0)} entries"
        
        self.license_info_text.delete(1.0, tk.END)
        self.license_info_text.insert(1.0, info_text)
    
    def activate_license(self):
        """Activate license with user input"""
        license_key = self.license_key_entry.get().strip().upper()
        
        if not license_key:
            messagebox.showerror("Error", "Please enter a license key")
            return
        
        success, message = self.license_manager.activate_license(license_key)
        
        if success:
            messagebox.showinfo("Success", message)
            self.license_key_entry.delete(0, tk.END)
            self.update_license_info()
        else:
            messagebox.showerror("Activation Failed", message)
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LicenseActivationGUI()
    app.run()
