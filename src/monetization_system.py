#!/usr/bin/env python3
"""
Monetization and Licensing System for Adaptive Chatbot
Professional pricing tiers and licensing management
"""

import json
import os
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from logger import log_info, log_error

class LicenseManager:
    """Manages software licensing and monetization"""
    
    def __init__(self):
        self.license_file = "license.json"
        self.machine_id = self._generate_machine_id()
        self.license_data = self._load_license()
    
    def _generate_machine_id(self) -> str:
        """Generate unique machine identifier"""
        try:
            import platform
            import uuid
            
            machine_info = f"{platform.node()}-{platform.system()}-{uuid.getnode()}"
            return hashlib.md5(machine_info.encode()).hexdigest()[:16].upper()
        except Exception:
            return "DEMO-MACHINE-ID"
    
    def _load_license(self) -> Dict[str, Any]:
        """Load existing license data"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._create_trial_license()
        except Exception as e:
            log_error("Failed to load license", error=e)
            return self._create_trial_license()
    
    def _create_trial_license(self) -> Dict[str, Any]:
        """Create 7-day trial license"""
        trial_data = {
            'license_type': 'trial',
            'machine_id': self.machine_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
            'features': {
                'voice_chat': True,
                'text_chat': True,
                'voice_teaching': True,
                'knowledge_export': False,
                'commercial_use': False,
                'max_knowledge_entries': 100
            },
            'usage_stats': {
                'total_conversations': 0,
                'knowledge_entries_created': 0,
                'voice_sessions': 0
            }
        }
        
        self._save_license(trial_data)
        return trial_data
    
    def _save_license(self, license_data: Dict[str, Any]):
        """Save license data to file"""
        try:
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, indent=2)
            self.license_data = license_data
        except Exception as e:
            log_error("Failed to save license", error=e)
    
    def check_license_validity(self) -> Tuple[bool, str]:
        """Check if current license is valid"""
        try:
            license_type = self.license_data.get('license_type', 'trial')
            
            # Check expiration for trial licenses
            if license_type == 'trial':
                expires_at = datetime.fromisoformat(self.license_data['expires_at'])
                if datetime.now() > expires_at:
                    return False, "Trial license has expired. Please purchase a full license."
            
            # Check machine ID for paid licenses
            if license_type in ['professional', 'business']:
                if self.license_data.get('machine_id') != self.machine_id:
                    return False, "License is not valid for this machine."
            
            return True, "License is valid"
            
        except Exception as e:
            log_error("License validation error", error=e)
            return False, "License validation failed"
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get detailed license information"""
        valid, message = self.check_license_validity()
        
        info = {
            'valid': valid,
            'message': message,
            'license_type': self.license_data.get('license_type', 'trial'),
            'machine_id': self.machine_id,
            'features': self.license_data.get('features', {}),
            'usage_stats': self.license_data.get('usage_stats', {})
        }
        
        # Add expiration info for trial
        if info['license_type'] == 'trial':
            try:
                expires_at = datetime.fromisoformat(self.license_data['expires_at'])
                days_left = (expires_at - datetime.now()).days
                info['days_remaining'] = max(0, days_left)
                info['expires_at'] = expires_at.strftime('%Y-%m-%d %H:%M:%S')
            except:
                info['days_remaining'] = 0
        
        return info
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """Activate a purchased license"""
        try:
            # Decode license key (simplified validation)
            if self._validate_license_key(license_key):
                license_type = self._extract_license_type(license_key)
                
                professional_features = {
                    'voice_chat': True,
                    'text_chat': True,
                    'voice_teaching': True,
                    'knowledge_export': True,
                    'commercial_use': True,
                    'max_knowledge_entries': 10000
                }
                
                business_features = {
                    **professional_features,
                    'multi_machine': True,
                    'custom_branding': True,
                    'priority_support': True,
                    'max_knowledge_entries': 50000
                }
                
                features = business_features if license_type == 'business' else professional_features
                
                activated_license = {
                    'license_type': license_type,
                    'license_key': license_key,
                    'machine_id': self.machine_id,
                    'activated_at': datetime.now().isoformat(),
                    'features': features,
                    'usage_stats': self.license_data.get('usage_stats', {
                        'total_conversations': 0,
                        'knowledge_entries_created': 0,
                        'voice_sessions': 0
                    })
                }
                
                self._save_license(activated_license)
                log_info(f"License activated: {license_type}")
                return True, f"Successfully activated {license_type} license!"
            
            return False, "Invalid license key. Please check and try again."
            
        except Exception as e:
            log_error("License activation error", error=e)
            return False, "License activation failed. Please try again."
    
    def _validate_license_key(self, license_key: str) -> bool:
        """Validate license key format (simplified)"""
        # Professional license: PROF-XXXX-XXXX-XXXX
        # Business license: BUSI-XXXX-XXXX-XXXX  
        # Trial upgrade: TRIAL-XXXX-XXXX-XXXX
        
        if not license_key or len(license_key) != 19:
            return False
        
        parts = license_key.split('-')
        if len(parts) != 4:
            return False
        
        prefix = parts[0]
        if prefix not in ['PROF', 'BUSI', 'TRIAL']:
            return False
        
        # Check if all parts after prefix are 4 characters
        for part in parts[1:]:
            if len(part) != 4:
                return False
        
        return True
    
    def _extract_license_type(self, license_key: str) -> str:
        """Extract license type from key"""
        prefix = license_key.split('-')[0]
        mapping = {
            'PROF': 'professional',
            'BUSI': 'business', 
            'TRIAL': 'trial'
        }
        return mapping.get(prefix, 'trial')
    
    def update_usage_stats(self, stat_type: str, increment: int = 1):
        """Update usage statistics"""
        try:
            if 'usage_stats' not in self.license_data:
                self.license_data['usage_stats'] = {}
            
            current = self.license_data['usage_stats'].get(stat_type, 0)
            self.license_data['usage_stats'][stat_type] = current + increment
            self._save_license(self.license_data)
            
        except Exception as e:
            log_error("Failed to update usage stats", error=e)

class PricingCalculator:
    """Calculate pricing and ROI for different business scenarios"""
    
    def __init__(self):
        self.pricing_tiers = {
            'trial': {
                'price': 0,
                'currency': 'INR',
                'duration': '7 days',
                'features': [
                    'Basic voice and text chat',
                    'Limited to 100 knowledge entries',
                    'Personal use only',
                    '7-day trial period'
                ]
            },
            'professional': {
                'price': 4999,
                'currency': 'INR', 
                'duration': 'Lifetime',
                'features': [
                    'Unlimited voice and text chat',
                    'Voice teaching capability',
                    'Up to 10,000 knowledge entries',
                    'Knowledge export/import',
                    'Commercial use allowed',
                    '1 year email support',
                    'Free updates'
                ]
            },
            'business': {
                'price': 9999,
                'currency': 'INR',
                'duration': 'Lifetime',
                'features': [
                    'Everything in Professional',
                    'Up to 50,000 knowledge entries',
                    'Multi-machine deployment',
                    'Custom branding options',
                    'Priority phone support',
                    'Custom knowledge integration',
                    'Training and consultation'
                ]
            }
        }
    
    def calculate_roi(self, business_type: str, monthly_customers: int) -> Dict[str, Any]:
        """Calculate ROI for different business scenarios"""
        
        roi_scenarios = {
            'electronics_shop': {
                'avg_query_time_saved': 3,  # minutes per query
                'staff_hourly_rate': 200,   # INR per hour
                'queries_automated_percent': 70
            },
            'customer_service': {
                'avg_query_time_saved': 5,
                'staff_hourly_rate': 300,
                'queries_automated_percent': 80
            },
            'general_business': {
                'avg_query_time_saved': 4,
                'staff_hourly_rate': 250,
                'queries_automated_percent': 60
            }
        }
        
        scenario = roi_scenarios.get(business_type, roi_scenarios['general_business'])
        
        # Calculate monthly savings
        automated_queries = monthly_customers * (scenario['queries_automated_percent'] / 100)
        time_saved_hours = (automated_queries * scenario['avg_query_time_saved']) / 60
        monthly_savings = time_saved_hours * scenario['staff_hourly_rate']
        
        # Professional license ROI
        prof_payback_months = self.pricing_tiers['professional']['price'] / monthly_savings
        prof_yearly_net_benefit = (monthly_savings * 12) - self.pricing_tiers['professional']['price']
        
        # Business license ROI  
        busi_payback_months = self.pricing_tiers['business']['price'] / monthly_savings
        busi_yearly_net_benefit = (monthly_savings * 12) - self.pricing_tiers['business']['price']
        
        return {
            'monthly_customers': monthly_customers,
            'automated_queries_per_month': int(automated_queries),
            'time_saved_hours_per_month': round(time_saved_hours, 1),
            'monthly_cost_savings': round(monthly_savings, 2),
            'professional': {
                'payback_period_months': round(prof_payback_months, 1),
                'yearly_net_benefit': round(prof_yearly_net_benefit, 2),
                'roi_percentage': round((prof_yearly_net_benefit / self.pricing_tiers['professional']['price']) * 100, 1)
            },
            'business': {
                'payback_period_months': round(busi_payback_months, 1), 
                'yearly_net_benefit': round(busi_yearly_net_benefit, 2),
                'roi_percentage': round((busi_yearly_net_benefit / self.pricing_tiers['business']['price']) * 100, 1)
            }
        }
    
    def get_pricing_comparison(self) -> Dict[str, Any]:
        """Get detailed pricing comparison"""
        return {
            'tiers': self.pricing_tiers,
            'comparison_matrix': {
                'features': {
                    'Voice Chat': {'trial': '✓', 'professional': '✓', 'business': '✓'},
                    'Text Chat': {'trial': '✓', 'professional': '✓', 'business': '✓'},
                    'Voice Teaching': {'trial': '✓', 'professional': '✓', 'business': '✓'},
                    'Knowledge Entries': {'trial': '100', 'professional': '10,000', 'business': '50,000'},
                    'Commercial Use': {'trial': '✗', 'professional': '✓', 'business': '✓'},
                    'Export/Import': {'trial': '✗', 'professional': '✓', 'business': '✓'},
                    'Multi-machine': {'trial': '✗', 'professional': '✗', 'business': '✓'},
                    'Custom Branding': {'trial': '✗', 'professional': '✗', 'business': '✓'},
                    'Support': {'trial': 'None', 'professional': 'Email', 'business': 'Phone + Email'},
                    'Duration': {'trial': '7 days', 'professional': 'Lifetime', 'business': 'Lifetime'}
                }
            }
        }

def create_license_activation_gui():
    """Create simple license activation interface"""
    activation_script = '''#!/usr/bin/env python3
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
        info_text += f"\\nFeatures Available:"
        info_text += f"\\n• Voice Chat: {'✅' if features.get('voice_chat') else '❌'}"
        info_text += f"\\n• Commercial Use: {'✅' if features.get('commercial_use') else '❌'}"
        info_text += f"\\n• Max Knowledge: {features.get('max_knowledge_entries', 0)} entries"
        
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
'''
    
    with open('license_activation.py', 'w', encoding='utf-8') as f:
        f.write(activation_script)

def main():
    """Demonstrate monetization system"""
    print("💰 Adaptive Chatbot Monetization System")
    print("="*50)
    
    # Initialize components
    license_manager = LicenseManager()
    pricing_calc = PricingCalculator()
    
    # Show current license status
    license_info = license_manager.get_license_info()
    print(f"\n📄 Current License Status:")
    print(f"   Type: {license_info['license_type'].title()}")
    print(f"   Valid: {'✅' if license_info['valid'] else '❌'}")
    
    if license_info['license_type'] == 'trial':
        print(f"   Days Remaining: {license_info.get('days_remaining', 0)}")
    
    # Show pricing tiers
    pricing = pricing_calc.get_pricing_comparison()
    print(f"\n💵 Pricing Tiers:")
    for tier, details in pricing['tiers'].items():
        print(f"\n{tier.title()}: ₹{details['price']} ({details['duration']})")
        for feature in details['features'][:3]:  # Show first 3 features
            print(f"   • {feature}")
    
    # Calculate ROI for sample business
    print(f"\n📊 ROI Calculation (Electronics Shop, 1000 monthly customers):")
    roi = pricing_calc.calculate_roi('electronics_shop', 1000)
    print(f"   Monthly Savings: ₹{roi['monthly_cost_savings']:,}")
    print(f"   Professional ROI: {roi['professional']['roi_percentage']}% annually")
    print(f"   Payback Period: {roi['professional']['payback_period_months']} months")
    
    # Create license activation GUI
    create_license_activation_gui()
    print(f"\n🔑 License activation GUI created: license_activation.py")
    
    print(f"\n✅ Monetization system ready!")
    print(f"💡 Users can now:")
    print(f"   • Try 7-day free trial")
    print(f"   • Purchase professional license (₹4,999)")
    print(f"   • Upgrade to business license (₹9,999)")
    print(f"   • Activate licenses easily")

if __name__ == "__main__":
    main()