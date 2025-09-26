#!/usr/bin/env python3
"""
Enhanced Business Intelligence Engine - Smart Business Operations
Implements dynamic pricing, inventory management, installation services, and market analysis
Specialized for electrical business domain with real-time recommendations
"""

import asyncio
import json
import sqlite3
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
from enum import Enum
import random
import math

from logger import log_info, log_error, log_warning
from performance_monitor import monitor_performance, MetricType, get_performance_monitor

class BusinessCategory(Enum):
    """Product categories in electrical business"""
    SWITCHES = "switches"
    WIRES = "wires"
    MCB = "mcb"
    LED_LIGHTS = "led_lights"
    FANS = "fans"
    SOCKETS = "sockets"
    PANELS = "panels"
    CONDUITS = "conduits"
    ACCESSORIES = "accessories"

class ServiceType(Enum):
    """Types of services offered"""
    INSTALLATION = "installation"
    REPAIR = "repair"
    MAINTENANCE = "maintenance"
    CONSULTATION = "consultation"
    EMERGENCY = "emergency"

class PriceFactorType(Enum):
    """Factors affecting dynamic pricing"""
    DEMAND = "demand"
    SEASON = "season"
    INVENTORY = "inventory"
    COMPETITION = "competition"
    LABOR = "labor"
    MATERIAL_COST = "material_cost"

@dataclass
class Product:
    """Product information"""
    id: str
    name: str
    category: BusinessCategory
    base_price: float
    current_price: float
    stock_quantity: int
    min_stock_level: int
    brand: str
    specifications: Dict[str, Any]
    demand_score: float = 1.0
    seasonal_factor: float = 1.0
    last_updated: Optional[datetime] = None

@dataclass
class Service:
    """Service information"""
    id: str
    name: str
    service_type: ServiceType
    base_price: float
    current_price: float
    duration_hours: float
    complexity_level: int  # 1-5
    required_skills: List[str]
    seasonal_demand: Dict[str, float]  # Month -> demand factor
    last_updated: Optional[datetime] = None

@dataclass
class PricingFactor:
    """Dynamic pricing factor"""
    factor_type: PriceFactorType
    current_value: float
    impact_multiplier: float
    last_updated: datetime

@dataclass
class MarketAnalysis:
    """Market analysis result"""
    category: BusinessCategory
    demand_trend: str  # "increasing", "decreasing", "stable"
    price_trend: str  # "rising", "falling", "stable"
    seasonal_factor: float
    competition_level: str  # "low", "medium", "high"
    recommended_action: str
    confidence: float

@dataclass
class BusinessRecommendation:
    """Business recommendation"""
    type: str  # "pricing", "inventory", "service", "marketing"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    expected_impact: str
    implementation_effort: str  # "low", "medium", "high"
    estimated_roi: Optional[float] = None

class InventoryManager:
    """Manages product inventory and stock levels"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.products = {}  # Product ID -> Product
        self.reorder_alerts = deque(maxlen=100)
        self._lock = threading.RLock()
        
        # Initialize database
        self._initialize_inventory_db()
        
        # Load existing inventory
        asyncio.create_task(self._load_inventory())
    
    def _initialize_inventory_db(self):
        """Initialize inventory database"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                # Products table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        base_price REAL NOT NULL,
                        current_price REAL NOT NULL,
                        stock_quantity INTEGER NOT NULL,
                        min_stock_level INTEGER NOT NULL,
                        brand TEXT,
                        specifications TEXT,
                        demand_score REAL DEFAULT 1.0,
                        seasonal_factor REAL DEFAULT 1.0,
                        last_updated TEXT
                    )
                ''')
                
                # Stock movements table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS stock_movements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id TEXT NOT NULL,
                        movement_type TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        notes TEXT,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # Create indexes
                conn.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_stock_movements_product ON stock_movements(product_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_stock_movements_timestamp ON stock_movements(timestamp)')
                
            log_info("📦 Inventory database initialized")
            
        except Exception as e:
            log_error(f"Failed to initialize inventory database: {e}")
    
    async def _load_inventory(self):
        """Load inventory from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, category, base_price, current_price, stock_quantity,
                           min_stock_level, brand, specifications, demand_score, seasonal_factor, last_updated
                    FROM products
                ''')
                
                for row in cursor.fetchall():
                    product_id = row[0]
                    specifications = json.loads(row[8] or '{}')
                    last_updated = datetime.fromisoformat(row[11]) if row[11] else None
                    
                    product = Product(
                        id=product_id,
                        name=row[1],
                        category=BusinessCategory(row[2]),
                        base_price=row[3],
                        current_price=row[4],
                        stock_quantity=row[5],
                        min_stock_level=row[6],
                        brand=row[7] or "",
                        specifications=specifications,
                        demand_score=row[9] or 1.0,
                        seasonal_factor=row[10] or 1.0,
                        last_updated=last_updated
                    )
                    
                    self.products[product_id] = product
                
            log_info(f"📦 Loaded {len(self.products)} products from inventory")
            
        except Exception as e:
            log_error(f"Failed to load inventory: {e}")
    
    def add_product(self, product: Product) -> bool:
        """Add or update product in inventory"""
        try:
            with self._lock:
                product.last_updated = datetime.now()
                self.products[product.id] = product
                
                # Save to database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO products 
                        (id, name, category, base_price, current_price, stock_quantity, 
                         min_stock_level, brand, specifications, demand_score, seasonal_factor, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product.id, product.name, product.category.value,
                        product.base_price, product.current_price, product.stock_quantity,
                        product.min_stock_level, product.brand, json.dumps(product.specifications),
                        product.demand_score, product.seasonal_factor, product.last_updated.isoformat()
                    ))
                
            return True
            
        except Exception as e:
            log_error(f"Failed to add product {product.id}: {e}")
            return False
    
    def update_stock(self, product_id: str, quantity_change: int, movement_type: str, notes: str = "") -> bool:
        """Update stock quantity for a product"""
        try:
            with self._lock:
                if product_id not in self.products:
                    return False
                
                product = self.products[product_id]
                new_quantity = product.stock_quantity + quantity_change
                
                if new_quantity < 0:
                    log_warning(f"Attempted to reduce stock below zero for {product_id}")
                    return False
                
                product.stock_quantity = new_quantity
                product.last_updated = datetime.now()
                
                # Update database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        UPDATE products SET stock_quantity = ?, last_updated = ? WHERE id = ?
                    ''', (new_quantity, product.last_updated.isoformat(), product_id))
                    
                    # Record stock movement
                    conn.execute('''
                        INSERT INTO stock_movements (product_id, movement_type, quantity, timestamp, notes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (product_id, movement_type, quantity_change, datetime.now().isoformat(), notes))
                
                # Check for low stock alert
                if new_quantity <= product.min_stock_level:
                    self._add_reorder_alert(product)
                
            return True
            
        except Exception as e:
            log_error(f"Failed to update stock for {product_id}: {e}")
            return False
    
    def _add_reorder_alert(self, product: Product):
        """Add reorder alert for low stock"""
        alert = {
            'product_id': product.id,
            'product_name': product.name,
            'current_stock': product.stock_quantity,
            'min_level': product.min_stock_level,
            'timestamp': datetime.now(),
            'category': product.category.value
        }
        
        self.reorder_alerts.append(alert)
        log_warning(f"🔔 Low stock alert: {product.name} ({product.stock_quantity} units remaining)")
    
    def get_low_stock_products(self) -> List[Product]:
        """Get products with low stock"""
        with self._lock:
            return [p for p in self.products.values() if p.stock_quantity <= p.min_stock_level]
    
    def get_category_stock_summary(self, category: BusinessCategory) -> Dict[str, Any]:
        """Get stock summary for a category"""
        with self._lock:
            category_products = [p for p in self.products.values() if p.category == category]
            
            if not category_products:
                return {'total_products': 0, 'total_value': 0.0, 'low_stock_count': 0}
            
            total_value = sum(p.current_price * p.stock_quantity for p in category_products)
            low_stock_count = sum(1 for p in category_products if p.stock_quantity <= p.min_stock_level)
            
            return {
                'total_products': len(category_products),
                'total_value': total_value,
                'low_stock_count': low_stock_count,
                'avg_demand_score': sum(p.demand_score for p in category_products) / len(category_products)
            }

class DynamicPricingEngine:
    """Handles dynamic pricing based on multiple factors"""
    
    def __init__(self):
        self.pricing_factors = {}  # Factor type -> PricingFactor
        self.pricing_history = deque(maxlen=1000)  # Recent pricing decisions
        
        # Initialize default factors
        self._initialize_default_factors()
    
    def _initialize_default_factors(self):
        """Initialize default pricing factors"""
        default_factors = [
            PricingFactor(PriceFactorType.DEMAND, 1.0, 0.2, datetime.now()),
            PricingFactor(PriceFactorType.SEASON, 1.0, 0.15, datetime.now()),
            PricingFactor(PriceFactorType.INVENTORY, 1.0, 0.1, datetime.now()),
            PricingFactor(PriceFactorType.COMPETITION, 1.0, 0.25, datetime.now()),
            PricingFactor(PriceFactorType.LABOR, 1.0, 0.1, datetime.now()),
            PricingFactor(PriceFactorType.MATERIAL_COST, 1.0, 0.2, datetime.now())
        ]
        
        for factor in default_factors:
            self.pricing_factors[factor.factor_type] = factor
    
    def update_factor(self, factor_type: PriceFactorType, new_value: float):
        """Update a pricing factor"""
        if factor_type in self.pricing_factors:
            factor = self.pricing_factors[factor_type]
            factor.current_value = new_value
            factor.last_updated = datetime.now()
            
            log_info(f"💰 Updated pricing factor {factor_type.value}: {new_value:.2f}")
    
    def calculate_dynamic_price(self, base_price: float, product: Product) -> float:
        """Calculate dynamic price based on current factors"""
        try:
            price_multiplier = 1.0
            
            # Apply each factor
            for factor in self.pricing_factors.values():
                factor_impact = (factor.current_value - 1.0) * factor.impact_multiplier
                price_multiplier += factor_impact
            
            # Apply product-specific factors
            price_multiplier *= product.seasonal_factor
            price_multiplier *= product.demand_score
            
            # Apply stock-based pricing
            if product.stock_quantity <= product.min_stock_level:
                price_multiplier *= 1.1  # 10% increase for low stock
            elif product.stock_quantity > product.min_stock_level * 3:
                price_multiplier *= 0.95  # 5% decrease for overstock
            
            # Ensure reasonable bounds
            price_multiplier = max(0.7, min(2.0, price_multiplier))  # 30% decrease to 100% increase max
            
            dynamic_price = base_price * price_multiplier
            
            # Record pricing decision
            self.pricing_history.append({
                'product_id': product.id,
                'base_price': base_price,
                'dynamic_price': dynamic_price,
                'multiplier': price_multiplier,
                'timestamp': datetime.now()
            })
            
            return round(dynamic_price, 2)
            
        except Exception as e:
            log_error(f"Failed to calculate dynamic price: {e}")
            return base_price
    
    def get_pricing_explanation(self, product: Product) -> Dict[str, Any]:
        """Get explanation for current pricing"""
        try:
            explanation = {
                'base_price': product.base_price,
                'current_price': product.current_price,
                'factors': []
            }
            
            # Analyze each factor
            for factor_type, factor in self.pricing_factors.items():
                impact = (factor.current_value - 1.0) * factor.impact_multiplier
                explanation['factors'].append({
                    'factor': factor_type.value,
                    'value': factor.current_value,
                    'impact': impact,
                    'description': self._get_factor_description(factor_type, factor.current_value)
                })
            
            # Product-specific factors
            if product.seasonal_factor != 1.0:
                explanation['factors'].append({
                    'factor': 'seasonal',
                    'value': product.seasonal_factor,
                    'impact': product.seasonal_factor - 1.0,
                    'description': f"Seasonal adjustment: {'+' if product.seasonal_factor > 1.0 else ''}{(product.seasonal_factor - 1.0) * 100:.1f}%"
                })
            
            if product.demand_score != 1.0:
                explanation['factors'].append({
                    'factor': 'demand',
                    'value': product.demand_score,
                    'impact': product.demand_score - 1.0,
                    'description': f"Demand-based adjustment: {'+' if product.demand_score > 1.0 else ''}{(product.demand_score - 1.0) * 100:.1f}%"
                })
            
            return explanation
            
        except Exception as e:
            log_error(f"Failed to get pricing explanation: {e}")
            return {'error': str(e)}
    
    def _get_factor_description(self, factor_type: PriceFactorType, value: float) -> str:
        """Get human-readable description of factor impact"""
        impact_pct = (value - 1.0) * 100
        
        descriptions = {
            PriceFactorType.DEMAND: f"Market demand is {'high' if value > 1.0 else 'low'} ({impact_pct:+.1f}%)",
            PriceFactorType.SEASON: f"Seasonal adjustment ({impact_pct:+.1f}%)",
            PriceFactorType.INVENTORY: f"Inventory level impact ({impact_pct:+.1f}%)",
            PriceFactorType.COMPETITION: f"Competition factor ({impact_pct:+.1f}%)",
            PriceFactorType.LABOR: f"Labor cost adjustment ({impact_pct:+.1f}%)",
            PriceFactorType.MATERIAL_COST: f"Material cost factor ({impact_pct:+.1f}%)"
        }
        
        return descriptions.get(factor_type, f"Factor adjustment ({impact_pct:+.1f}%)")

class MarketAnalyzer:
    """Analyzes market trends and provides insights"""
    
    def __init__(self):
        self.market_data = {}  # Category -> historical data
        self.analysis_cache = {}  # Cache for recent analyses
        
    def analyze_category_market(self, category: BusinessCategory, products: List[Product]) -> MarketAnalysis:
        """Analyze market conditions for a product category"""
        try:
            # Simple market analysis based on available data
            if not products:
                return MarketAnalysis(
                    category=category,
                    demand_trend="stable",
                    price_trend="stable", 
                    seasonal_factor=1.0,
                    competition_level="medium",
                    recommended_action="maintain_current_strategy",
                    confidence=0.5
                )
            
            # Analyze demand trends
            avg_demand = sum(p.demand_score for p in products) / len(products)
            demand_trend = "increasing" if avg_demand > 1.2 else "decreasing" if avg_demand < 0.8 else "stable"
            
            # Analyze price trends
            avg_price_ratio = sum(p.current_price / p.base_price for p in products) / len(products)
            price_trend = "rising" if avg_price_ratio > 1.05 else "falling" if avg_price_ratio < 0.95 else "stable"
            
            # Seasonal factor (simplified)
            current_month = datetime.now().month
            seasonal_factors = {
                BusinessCategory.FANS: self._get_fan_seasonal_factor(current_month),
                BusinessCategory.LED_LIGHTS: self._get_lighting_seasonal_factor(current_month),
                BusinessCategory.SWITCHES: 1.0,  # Generally stable
                BusinessCategory.WIRES: 1.0,     # Generally stable
                BusinessCategory.MCB: 1.0        # Generally stable
            }
            seasonal_factor = seasonal_factors.get(category, 1.0)
            
            # Competition analysis (simplified)
            low_stock_ratio = sum(1 for p in products if p.stock_quantity <= p.min_stock_level) / len(products)
            competition_level = "high" if low_stock_ratio > 0.3 else "low" if low_stock_ratio < 0.1 else "medium"
            
            # Recommendation
            recommended_action = self._get_recommended_action(demand_trend, price_trend, seasonal_factor)
            
            # Confidence based on data quality
            confidence = min(0.9, 0.5 + len(products) * 0.05)  # Higher confidence with more products
            
            return MarketAnalysis(
                category=category,
                demand_trend=demand_trend,
                price_trend=price_trend,
                seasonal_factor=seasonal_factor,
                competition_level=competition_level,
                recommended_action=recommended_action,
                confidence=confidence
            )
            
        except Exception as e:
            log_error(f"Market analysis failed for {category.value}: {e}")
            return MarketAnalysis(
                category=category,
                demand_trend="unknown",
                price_trend="unknown",
                seasonal_factor=1.0,
                competition_level="unknown", 
                recommended_action="maintain_current_strategy",
                confidence=0.0
            )
    
    def _get_fan_seasonal_factor(self, month: int) -> float:
        """Get seasonal factor for fans based on month"""
        # Higher demand in summer months (April-June)
        seasonal_map = {
            1: 0.7, 2: 0.8, 3: 1.1, 4: 1.4, 5: 1.5, 6: 1.4,
            7: 1.2, 8: 1.1, 9: 1.0, 10: 0.9, 11: 0.8, 12: 0.7
        }
        return seasonal_map.get(month, 1.0)
    
    def _get_lighting_seasonal_factor(self, month: int) -> float:
        """Get seasonal factor for lights based on month"""
        # Higher demand during festival seasons (Oct-Dec) and winter
        seasonal_map = {
            1: 1.1, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0,
            7: 1.0, 8: 1.0, 9: 1.1, 10: 1.3, 11: 1.4, 12: 1.3
        }
        return seasonal_map.get(month, 1.0)
    
    def _get_recommended_action(self, demand_trend: str, price_trend: str, seasonal_factor: float) -> str:
        """Get recommended business action based on trends"""
        if demand_trend == "increasing" and price_trend == "stable":
            return "increase_inventory" if seasonal_factor > 1.1 else "maintain_stock"
        elif demand_trend == "increasing" and price_trend == "rising":
            return "optimize_pricing"
        elif demand_trend == "decreasing" and price_trend == "falling":
            return "reduce_inventory"
        elif seasonal_factor > 1.2:
            return "prepare_for_seasonal_demand"
        elif seasonal_factor < 0.8:
            return "focus_on_other_categories"
        else:
            return "maintain_current_strategy"

class EnhancedBusinessIntelligenceEngine:
    """Main business intelligence engine"""
    
    def __init__(self, db_path: str = "data/business_intelligence.db"):
        self.db_path = db_path
        
        # Core components
        self.inventory_manager = InventoryManager(self.db_path)
        self.pricing_engine = DynamicPricingEngine()
        self.market_analyzer = MarketAnalyzer()
        
        # Services management
        self.services = {}  # Service ID -> Service
        
        # Recommendations cache
        self.recommendations_cache = deque(maxlen=100)
        
        # Initialize with sample data
        asyncio.create_task(self._initialize_sample_data())
        
        log_info("🧠 Enhanced Business Intelligence Engine initialized")
    
    async def _initialize_sample_data(self):
        """Initialize with sample electrical business data"""
        try:
            # Sample products
            sample_products = [
                Product("SW001", "Modular Switch 1-Way", BusinessCategory.SWITCHES, 45.0, 45.0, 150, 20, "Legrand", {"type": "1-way", "color": "white"}),
                Product("SW002", "Modular Switch 2-Way", BusinessCategory.SWITCHES, 65.0, 65.0, 100, 15, "Legrand", {"type": "2-way", "color": "white"}),
                Product("WR001", "Copper Wire 1.5sq", BusinessCategory.WIRES, 85.0, 85.0, 200, 30, "Finolex", {"size": "1.5sqmm", "material": "copper"}),
                Product("WR002", "Copper Wire 2.5sq", BusinessCategory.WIRES, 125.0, 125.0, 180, 25, "Finolex", {"size": "2.5sqmm", "material": "copper"}),
                Product("MCB001", "MCB 16A Single Pole", BusinessCategory.MCB, 185.0, 185.0, 75, 10, "Schneider", {"rating": "16A", "poles": 1}),
                Product("LED001", "LED Bulb 9W", BusinessCategory.LED_LIGHTS, 120.0, 120.0, 300, 40, "Philips", {"wattage": "9W", "type": "bulb"}),
                Product("FAN001", "Ceiling Fan 48 inch", BusinessCategory.FANS, 2500.0, 2500.0, 25, 5, "Havells", {"size": "48inch", "type": "ceiling"}),
                Product("SK001", "3-Pin Socket", BusinessCategory.SOCKETS, 55.0, 55.0, 120, 20, "Anchor", {"type": "3-pin", "rating": "16A"})
            ]
            
            # Add products to inventory
            for product in sample_products:
                self.inventory_manager.add_product(product)
            
            # Sample services
            sample_services = [
                Service("SRV001", "Basic Wiring Installation", ServiceType.INSTALLATION, 500.0, 500.0, 4.0, 2, ["basic_electrical"], {"1": 1.0, "12": 1.0}),
                Service("SRV002", "Fan Installation", ServiceType.INSTALLATION, 300.0, 300.0, 2.0, 2, ["basic_electrical"], {"4": 1.3, "5": 1.4, "6": 1.2}),
                Service("SRV003", "MCB Panel Setup", ServiceType.INSTALLATION, 1200.0, 1200.0, 6.0, 4, ["advanced_electrical"], {"1": 1.0, "12": 1.0}),
                Service("SRV004", "Emergency Repair", ServiceType.EMERGENCY, 800.0, 800.0, 2.0, 3, ["troubleshooting"], {"1": 1.0, "12": 1.0})
            ]
            
            for service in sample_services:
                self.services[service.id] = service
            
            log_info(f"📦 Initialized with {len(sample_products)} products and {len(sample_services)} services")
            
        except Exception as e:
            log_error(f"Failed to initialize sample data: {e}")
    
    @monitor_performance("business_intelligence")
    async def get_product_recommendations(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get product recommendations based on query"""
        try:
            recommendations = []
            query_lower = query.lower()
            
            # Extract product categories from query
            category_matches = []
            for category in BusinessCategory:
                if category.value in query_lower or any(word in query_lower for word in self._get_category_keywords(category)):
                    category_matches.append(category)
            
            # Get products from matched categories
            relevant_products = []
            for product in self.inventory_manager.products.values():
                if not category_matches or product.category in category_matches:
                    relevant_products.append(product)
            
            # Sort by demand score and stock availability
            relevant_products.sort(key=lambda p: (p.demand_score, p.stock_quantity > p.min_stock_level), reverse=True)
            
            # Generate recommendations
            for product in relevant_products[:5]:  # Top 5 recommendations
                # Update dynamic pricing
                dynamic_price = self.pricing_engine.calculate_dynamic_price(product.base_price, product)
                product.current_price = dynamic_price
                
                # Get stock status
                stock_status = "in_stock" if product.stock_quantity > product.min_stock_level else "low_stock" if product.stock_quantity > 0 else "out_of_stock"
                
                recommendation = {
                    "product_id": product.id,
                    "name": product.name,
                    "category": product.category.value,
                    "price": product.current_price,
                    "original_price": product.base_price,
                    "brand": product.brand,
                    "stock_status": stock_status,
                    "stock_quantity": product.stock_quantity,
                    "specifications": product.specifications,
                    "recommendation_reason": self._get_recommendation_reason(product, query),
                    "pricing_factors": self.pricing_engine.get_pricing_explanation(product)
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            log_error(f"Failed to get product recommendations: {e}")
            return []
    
    def _get_category_keywords(self, category: BusinessCategory) -> List[str]:
        """Get keywords associated with a category"""
        keyword_map = {
            BusinessCategory.SWITCHES: ["switch", "switches", "modular", "press", "button"],
            BusinessCategory.WIRES: ["wire", "wires", "cable", "cables", "copper", "aluminium"],
            BusinessCategory.MCB: ["mcb", "circuit breaker", "protection", "safety", "trip"],
            BusinessCategory.LED_LIGHTS: ["light", "lights", "led", "bulb", "tube", "lamp"],
            BusinessCategory.FANS: ["fan", "fans", "ceiling", "exhaust", "table"],
            BusinessCategory.SOCKETS: ["socket", "sockets", "plug", "outlet", "point"],
            BusinessCategory.PANELS: ["panel", "panels", "distribution", "board"],
            BusinessCategory.CONDUITS: ["conduit", "conduits", "pipe", "pvc"],
            BusinessCategory.ACCESSORIES: ["accessory", "accessories", "connector", "junction"]
        }
        
        return keyword_map.get(category, [])
    
    def _get_recommendation_reason(self, product: Product, query: str) -> str:
        """Generate recommendation reason"""
        reasons = []
        
        if product.demand_score > 1.2:
            reasons.append("High demand product")
        
        if product.current_price < product.base_price:
            reasons.append("Special pricing")
        
        if product.stock_quantity > product.min_stock_level * 2:
            reasons.append("Good availability")
        
        if product.brand in ["Legrand", "Schneider", "Philips", "Havells"]:
            reasons.append("Premium brand")
        
        if not reasons:
            reasons.append("Popular choice")
        
        return ", ".join(reasons)
    
    async def get_service_recommendations(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get service recommendations"""
        try:
            recommendations = []
            query_lower = query.lower()
            
            # Match services based on keywords
            relevant_services = []
            for service in self.services.values():
                if any(word in query_lower for word in [service.name.lower(), service.service_type.value]):
                    relevant_services.append(service)
            
            # If no direct matches, suggest all services
            if not relevant_services:
                relevant_services = list(self.services.values())
            
            # Generate recommendations
            for service in relevant_services[:3]:  # Top 3 services
                # Apply seasonal pricing if applicable
                current_month = str(datetime.now().month)
                seasonal_multiplier = service.seasonal_demand.get(current_month, 1.0)
                adjusted_price = service.base_price * seasonal_multiplier
                
                recommendation = {
                    "service_id": service.id,
                    "name": service.name,
                    "type": service.service_type.value,
                    "price": adjusted_price,
                    "duration_hours": service.duration_hours,
                    "complexity": service.complexity_level,
                    "required_skills": service.required_skills,
                    "seasonal_factor": seasonal_multiplier,
                    "description": self._get_service_description(service)
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            log_error(f"Failed to get service recommendations: {e}")
            return []
    
    def _get_service_description(self, service: Service) -> str:
        """Generate service description"""
        descriptions = {
            "Basic Wiring Installation": "Professional wiring installation for residential and commercial spaces",
            "Fan Installation": "Expert ceiling fan installation with proper mounting and electrical connections",
            "MCB Panel Setup": "Complete MCB panel installation with proper circuit distribution and safety measures", 
            "Emergency Repair": "24/7 emergency electrical repair services for urgent issues"
        }
        
        return descriptions.get(service.name, f"Professional {service.service_type.value} service")
    
    async def generate_business_insights(self) -> Dict[str, Any]:
        """Generate comprehensive business insights"""
        try:
            insights = {
                "inventory_analysis": self._analyze_inventory(),
                "pricing_analysis": self._analyze_pricing(),
                "market_trends": await self._analyze_market_trends(),
                "recommendations": await self._generate_recommendations(),
                "performance_metrics": self._get_performance_metrics()
            }
            
            return insights
            
        except Exception as e:
            log_error(f"Failed to generate business insights: {e}")
            return {"error": str(e)}
    
    def _analyze_inventory(self) -> Dict[str, Any]:
        """Analyze current inventory status"""
        try:
            total_products = len(self.inventory_manager.products)
            low_stock_products = self.inventory_manager.get_low_stock_products()
            
            # Category-wise analysis
            category_analysis = {}
            for category in BusinessCategory:
                summary = self.inventory_manager.get_category_stock_summary(category)
                category_analysis[category.value] = summary
            
            # Calculate total inventory value
            total_value = sum(p.current_price * p.stock_quantity for p in self.inventory_manager.products.values())
            
            return {
                "total_products": total_products,
                "total_inventory_value": total_value,
                "low_stock_count": len(low_stock_products),
                "low_stock_products": [{"id": p.id, "name": p.name, "quantity": p.stock_quantity} for p in low_stock_products],
                "category_analysis": category_analysis,
                "reorder_alerts_count": len(self.inventory_manager.reorder_alerts)
            }
            
        except Exception as e:
            log_error(f"Inventory analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_pricing(self) -> Dict[str, Any]:
        """Analyze current pricing strategies"""
        try:
            pricing_data = []
            
            for product in self.inventory_manager.products.values():
                price_variance = (product.current_price - product.base_price) / product.base_price * 100
                
                pricing_data.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "base_price": product.base_price,
                    "current_price": product.current_price,
                    "variance_percent": price_variance,
                    "category": product.category.value
                })
            
            # Overall pricing statistics
            variances = [item["variance_percent"] for item in pricing_data]
            avg_variance = sum(variances) / len(variances) if variances else 0
            
            return {
                "average_price_variance": avg_variance,
                "products_with_increased_prices": len([p for p in pricing_data if p["variance_percent"] > 0]),
                "products_with_decreased_prices": len([p for p in pricing_data if p["variance_percent"] < 0]),
                "pricing_factors": {ft.value: f.current_value for ft, f in self.pricing_engine.pricing_factors.items()},
                "recent_pricing_decisions": len(self.pricing_engine.pricing_history)
            }
            
        except Exception as e:
            log_error(f"Pricing analysis failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_market_trends(self) -> Dict[str, Any]:
        """Analyze market trends for all categories"""
        try:
            market_analysis = {}
            
            for category in BusinessCategory:
                category_products = [p for p in self.inventory_manager.products.values() if p.category == category]
                analysis = self.market_analyzer.analyze_category_market(category, category_products)
                market_analysis[category.value] = asdict(analysis)
            
            return market_analysis
            
        except Exception as e:
            log_error(f"Market trend analysis failed: {e}")
            return {"error": str(e)}
    
    async def _generate_recommendations(self) -> List[BusinessRecommendation]:
        """Generate business recommendations"""
        try:
            recommendations = []
            
            # Inventory-based recommendations
            low_stock_products = self.inventory_manager.get_low_stock_products()
            if low_stock_products:
                recommendations.append(BusinessRecommendation(
                    type="inventory",
                    priority="high",
                    title="Restock Low Inventory Items",
                    description=f"You have {len(low_stock_products)} products with low stock levels",
                    expected_impact="Prevent stockouts and maintain sales",
                    implementation_effort="medium"
                ))
            
            # Pricing-based recommendations
            overpriced_products = [p for p in self.inventory_manager.products.values() 
                                 if p.current_price > p.base_price * 1.2 and p.stock_quantity > p.min_stock_level * 2]
            
            if overpriced_products:
                recommendations.append(BusinessRecommendation(
                    type="pricing",
                    priority="medium", 
                    title="Consider Price Optimization",
                    description=f"{len(overpriced_products)} products may benefit from price adjustments",
                    expected_impact="Increase sales volume",
                    implementation_effort="low"
                ))
            
            # Market-based recommendations
            current_month = datetime.now().month
            if current_month in [4, 5, 6]:  # Summer months
                recommendations.append(BusinessRecommendation(
                    type="marketing",
                    priority="high",
                    title="Focus on Summer Products",
                    description="Promote fans and cooling products during peak summer season",
                    expected_impact="Increase seasonal sales by 20-30%",
                    implementation_effort="medium"
                ))
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            log_error(f"Failed to generate recommendations: {e}")
            return []
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get business performance metrics"""
        try:
            # Calculate metrics
            total_inventory_value = sum(p.current_price * p.stock_quantity for p in self.inventory_manager.products.values())
            avg_demand_score = sum(p.demand_score for p in self.inventory_manager.products.values()) / len(self.inventory_manager.products) if self.inventory_manager.products else 0
            
            # Stock turnover simulation (simplified)
            stock_efficiency = 1 - (len(self.inventory_manager.get_low_stock_products()) / len(self.inventory_manager.products)) if self.inventory_manager.products else 0
            
            return {
                "total_inventory_value": total_inventory_value,
                "average_demand_score": avg_demand_score,
                "stock_efficiency": stock_efficiency,
                "active_products": len(self.inventory_manager.products),
                "active_services": len(self.services),
                "pricing_optimization_score": min(avg_demand_score, 1.0) * 100
            }
            
        except Exception as e:
            log_error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
    
    async def process_business_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process business-related queries"""
        try:
            query_lower = query.lower()
            response = {"type": "business_query", "query": query}
            
            # Product inquiries
            if any(word in query_lower for word in ["price", "cost", "kitna", "rate"]):
                product_recs = await self.get_product_recommendations(query, context)
                response["products"] = product_recs
                response["type"] = "product_inquiry"
            
            # Service inquiries
            elif any(word in query_lower for word in ["install", "repair", "service", "maintenance"]):
                service_recs = await self.get_service_recommendations(query, context)
                response["services"] = service_recs
                response["type"] = "service_inquiry"
            
            # Business insights
            elif any(word in query_lower for word in ["business", "sales", "inventory", "stock"]):
                insights = await self.generate_business_insights()
                response["insights"] = insights
                response["type"] = "business_insights"
            
            # General product search
            else:
                product_recs = await self.get_product_recommendations(query, context)
                response["products"] = product_recs
                response["type"] = "product_search"
            
            return response
            
        except Exception as e:
            log_error(f"Failed to process business query: {e}")
            return {"error": str(e), "query": query}
    
    async def cleanup(self):
        """Clean up resources"""
        log_info("🧹 Cleaning up Business Intelligence Engine...")
        
        # Clear caches
        self.recommendations_cache.clear()
        self.pricing_engine.pricing_history.clear()
        
        log_info("✅ Business Intelligence Engine cleanup completed")


# Global instance
_business_intelligence_engine = None

def get_business_intelligence_engine(**kwargs) -> EnhancedBusinessIntelligenceEngine:
    """Get or create global business intelligence engine"""
    global _business_intelligence_engine
    if _business_intelligence_engine is None:
        _business_intelligence_engine = EnhancedBusinessIntelligenceEngine(**kwargs)
    return _business_intelligence_engine

if __name__ == "__main__":
    # Test the business intelligence engine
    async def test_business_intelligence():
        print("🧪 Testing Enhanced Business Intelligence Engine")
        print("=" * 60)
        
        # Create engine
        engine = EnhancedBusinessIntelligenceEngine(db_path="test_business.db")
        
        # Wait for initialization
        await asyncio.sleep(2)
        
        # Test product recommendations
        test_queries = [
            "Switch ka price kya hai?",
            "Wire installation service chahiye",
            "LED lights available hain?",
            "Fan price aur installation cost",
            "MCB safety ke liye chahiye"
        ]
        
        print("\n🔍 Testing Product & Service Recommendations:")
        for query in test_queries:
            print(f"\n--- Query: {query} ---")
            
            result = await engine.process_business_query(query)
            print(f"Query Type: {result['type']}")
            
            if 'products' in result and result['products']:
                print("Product Recommendations:")
                for i, product in enumerate(result['products'][:3], 1):
                    print(f"  {i}. {product['name']} - ₹{product['price']:.2f}")
                    print(f"     Brand: {product['brand']}, Stock: {product['stock_status']}")
                    print(f"     Reason: {product['recommendation_reason']}")
            
            if 'services' in result and result['services']:
                print("Service Recommendations:")
                for i, service in enumerate(result['services'][:2], 1):
                    print(f"  {i}. {service['name']} - ₹{service['price']:.2f}")
                    print(f"     Duration: {service['duration_hours']} hours")
        
        # Test business insights
        print("\n📊 Business Insights:")
        insights = await engine.generate_business_insights()
        
        if 'inventory_analysis' in insights:
            inv = insights['inventory_analysis']
            print(f"• Total Products: {inv['total_products']}")
            print(f"• Inventory Value: ₹{inv['total_inventory_value']:,.2f}")
            print(f"• Low Stock Items: {inv['low_stock_count']}")
        
        if 'recommendations' in insights:
            print("\n💡 Business Recommendations:")
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                print(f"  {i}. {rec.title} ({rec.priority} priority)")
                print(f"     {rec.description}")
        
        # Test market analysis
        if 'market_trends' in insights:
            print("\n📈 Market Trends:")
            for category, analysis in list(insights['market_trends'].items())[:3]:
                if 'demand_trend' in analysis:
                    print(f"  • {category}: {analysis['demand_trend']} demand, {analysis['price_trend']} prices")
        
        # Test dynamic pricing
        print("\n💰 Dynamic Pricing Test:")
        sample_product = list(engine.inventory_manager.products.values())[0]
        print(f"Product: {sample_product.name}")
        print(f"Base Price: ₹{sample_product.base_price:.2f}")
        print(f"Current Price: ₹{sample_product.current_price:.2f}")
        
        pricing_explanation = engine.pricing_engine.get_pricing_explanation(sample_product)
        if 'factors' in pricing_explanation:
            print("Pricing Factors:")
            for factor in pricing_explanation['factors'][:3]:
                print(f"  • {factor['factor']}: {factor['description']}")
        
        # Cleanup
        await engine.cleanup()
        print("\n🧹 Test completed")
    
    # Run test
    asyncio.run(test_business_intelligence())