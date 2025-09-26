"""
Database Optimization System
Advanced database operations with connection pooling and query optimization
"""

import asyncio
import sqlite3
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import queue
import weakref
import gc

try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False

class ConnectionState(Enum):
    """Connection states"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    CLOSED = "closed"

class QueryType(Enum):
    """Query types for optimization"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    DROP = "drop"

@dataclass
class DatabaseConnection:
    """Database connection wrapper"""
    connection: sqlite3.Connection
    state: ConnectionState = ConnectionState.IDLE
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    query_count: int = 0
    error_count: int = 0
    connection_id: str = ""
    
    def __post_init__(self):
        if not self.connection_id:
            self.connection_id = f"conn_{id(self.connection)}"
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        try:
            self.connection.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def update_usage(self):
        """Update usage statistics"""
        self.last_used = time.time()
        self.query_count += 1
    
    def record_error(self):
        """Record an error"""
        self.error_count += 1
        self.state = ConnectionState.ERROR

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_type: QueryType
    execution_time: float
    rows_affected: int
    connection_id: str
    timestamp: float
    success: bool
    error_message: Optional[str] = None

class ConnectionPool:
    """Advanced connection pool with health monitoring"""
    
    def __init__(self, 
                 database_path: str,
                 min_connections: int = 2,
                 max_connections: int = 10,
                 connection_timeout: float = 30.0,
                 idle_timeout: float = 300.0):
        self.database_path = database_path
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        
        # Connection management
        self._connections: Dict[str, DatabaseConnection] = {}
        self._available_connections: queue.Queue = queue.Queue()
        self._busy_connections: Dict[str, DatabaseConnection] = {}
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Metrics
        self._query_metrics: List[QueryMetrics] = []
        self._total_queries = 0
        self._successful_queries = 0
        self._failed_queries = 0
        
        # Initialize pool
        self._initialize_pool()
        self._start_monitoring()
    
    def _initialize_pool(self):
        """Initialize connection pool with minimum connections"""
        for i in range(self.min_connections):
            self._create_connection()
    
    def _create_connection(self) -> Optional[DatabaseConnection]:
        """Create a new database connection"""
        try:
            connection = sqlite3.connect(
                self.database_path,
                timeout=self.connection_timeout,
                check_same_thread=False
            )
            
            # Optimize connection settings
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute("PRAGMA cache_size=10000")
            connection.execute("PRAGMA temp_store=MEMORY")
            connection.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            db_conn = DatabaseConnection(connection=connection)
            self._connections[db_conn.connection_id] = db_conn
            self._available_connections.put(db_conn)
            
            print(f"✅ Created database connection: {db_conn.connection_id}")
            return db_conn
            
        except Exception as e:
            print(f"⚠️ Failed to create database connection: {e}")
            return None
    
    def get_connection(self, timeout: float = 10.0) -> Optional[DatabaseConnection]:
        """Get a connection from the pool"""
        try:
            # Try to get available connection
            try:
                connection = self._available_connections.get(timeout=timeout)
                if connection.is_healthy():
                    connection.state = ConnectionState.BUSY
                    self._busy_connections[connection.connection_id] = connection
                    return connection
                else:
                    # Connection is unhealthy, remove it
                    self._remove_connection(connection.connection_id)
            except queue.Empty:
                pass
            
            # Create new connection if under limit
            with self._lock:
                if len(self._connections) < self.max_connections:
                    connection = self._create_connection()
                    if connection:
                        connection.state = ConnectionState.BUSY
                        self._busy_connections[connection.connection_id] = connection
                        return connection
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error getting connection: {e}")
            return None
    
    def return_connection(self, connection: DatabaseConnection):
        """Return connection to the pool"""
        try:
            with self._lock:
                if connection.connection_id in self._busy_connections:
                    del self._busy_connections[connection.connection_id]
                    connection.state = ConnectionState.IDLE
                    connection.update_usage()
                    
                    if connection.is_healthy():
                        self._available_connections.put(connection)
                    else:
                        self._remove_connection(connection.connection_id)
                        
        except Exception as e:
            print(f"⚠️ Error returning connection: {e}")
    
    def _remove_connection(self, connection_id: str):
        """Remove connection from pool"""
        try:
            with self._lock:
                if connection_id in self._connections:
                    connection = self._connections.pop(connection_id)
                    connection.connection.close()
                    print(f"🗑️ Removed connection: {connection_id}")
                    
        except Exception as e:
            print(f"⚠️ Error removing connection: {e}")
    
    def _start_monitoring(self):
        """Start connection pool monitoring"""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitor_thread.start()
    
    def _monitoring_loop(self):
        """Connection pool monitoring loop"""
        while self._monitoring:
            try:
                self._cleanup_idle_connections()
                self._check_connection_health()
                time.sleep(5.0)  # Check every 5 seconds
            except Exception as e:
                print(f"⚠️ Connection monitoring error: {e}")
                time.sleep(10.0)
    
    def _cleanup_idle_connections(self):
        """Clean up idle connections"""
        current_time = time.time()
        idle_connections = []
        
        with self._lock:
            for conn_id, connection in self._connections.items():
                if (connection.state == ConnectionState.IDLE and 
                    current_time - connection.last_used > self.idle_timeout and
                    len(self._connections) > self.min_connections):
                    idle_connections.append(conn_id)
        
        for conn_id in idle_connections:
            self._remove_connection(conn_id)
    
    def _check_connection_health(self):
        """Check health of all connections"""
        unhealthy_connections = []
        
        with self._lock:
            for conn_id, connection in self._connections.items():
                if not connection.is_healthy():
                    unhealthy_connections.append(conn_id)
        
        for conn_id in unhealthy_connections:
            self._remove_connection(conn_id)
    
    def execute_query(self, query: str, params: Tuple = (), 
                     query_type: QueryType = QueryType.SELECT) -> Tuple[bool, Any, Optional[str]]:
        """Execute a query with metrics tracking"""
        start_time = time.time()
        connection = None
        
        try:
            connection = self.get_connection()
            if not connection:
                return False, None, "No available connections"
            
            cursor = connection.connection.cursor()
            cursor.execute(query, params)
            
            # Get results based on query type
            if query_type == QueryType.SELECT:
                result = cursor.fetchall()
                rows_affected = len(result)
            else:
                connection.connection.commit()
                result = cursor.rowcount
                rows_affected = result
            
            # Record metrics
            execution_time = time.time() - start_time
            metrics = QueryMetrics(
                query_type=query_type,
                execution_time=execution_time,
                rows_affected=rows_affected,
                connection_id=connection.connection_id,
                timestamp=time.time(),
                success=True
            )
            self._record_query_metrics(metrics)
            
            return True, result, None
            
        except Exception as e:
            error_msg = str(e)
            if connection:
                connection.record_error()
            
            # Record error metrics
            execution_time = time.time() - start_time
            metrics = QueryMetrics(
                query_type=query_type,
                execution_time=execution_time,
                rows_affected=0,
                connection_id=connection.connection_id if connection else "unknown",
                timestamp=time.time(),
                success=False,
                error_message=error_msg
            )
            self._record_query_metrics(metrics)
            
            return False, None, error_msg
            
        finally:
            if connection:
                self.return_connection(connection)
    
    def _record_query_metrics(self, metrics: QueryMetrics):
        """Record query performance metrics"""
        self._query_metrics.append(metrics)
        self._total_queries += 1
        
        if metrics.success:
            self._successful_queries += 1
        else:
            self._failed_queries += 1
        
        # Keep only recent metrics (last 1000)
        if len(self._query_metrics) > 1000:
            self._query_metrics = self._query_metrics[-1000:]
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self._lock:
            total_connections = len(self._connections)
            available_connections = self._available_connections.qsize()
            busy_connections = len(self._busy_connections)
            
            # Calculate average query time
            avg_query_time = 0.0
            if self._query_metrics:
                avg_query_time = sum(m.execution_time for m in self._query_metrics) / len(self._query_metrics)
            
            # Calculate success rate
            success_rate = 0.0
            if self._total_queries > 0:
                success_rate = self._successful_queries / self._total_queries
            
            return {
                "total_connections": total_connections,
                "available_connections": available_connections,
                "busy_connections": busy_connections,
                "min_connections": self.min_connections,
                "max_connections": self.max_connections,
                "total_queries": self._total_queries,
                "successful_queries": self._successful_queries,
                "failed_queries": self._failed_queries,
                "success_rate": f"{success_rate:.2%}",
                "average_query_time_ms": avg_query_time * 1000,
                "monitoring_active": self._monitoring
            }
    
    def cleanup(self):
        """Cleanup connection pool"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        with self._lock:
            for connection in self._connections.values():
                connection.connection.close()
            self._connections.clear()
            
            # Clear queues
            while not self._available_connections.empty():
                try:
                    self._available_connections.get_nowait()
                except queue.Empty:
                    break

class DatabaseOptimizer:
    """Main database optimization system"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.connection_pool = ConnectionPool(database_path)
        self._query_cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, float] = {}
        self._cache_timeout = 300.0  # 5 minutes
        
    def execute_optimized_query(self, query: str, params: Tuple = (), 
                              use_cache: bool = True,
                              cache_ttl: float = 300.0) -> Tuple[bool, Any, Optional[str]]:
        """Execute query with optimizations"""
        # Check cache first
        if use_cache:
            cache_key = f"{query}:{str(params)}"
            if self._is_cached(cache_key):
                cached_result = self._query_cache[cache_key]
                print(f"📋 Cache hit for query: {query[:50]}...")
                return True, cached_result, None
        
        # Execute query
        query_type = self._determine_query_type(query)
        success, result, error = self.connection_pool.execute_query(query, params, query_type)
        
        # Cache successful SELECT queries
        if success and use_cache and query_type == QueryType.SELECT:
            cache_key = f"{query}:{str(params)}"
            self._query_cache[cache_key] = result
            self._cache_ttl[cache_key] = time.time() + cache_ttl
        
        return success, result, error
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if query result is cached and not expired"""
        if cache_key not in self._query_cache:
            return False
        
        if cache_key in self._cache_ttl:
            if time.time() > self._cache_ttl[cache_key]:
                # Cache expired
                del self._query_cache[cache_key]
                del self._cache_ttl[cache_key]
                return False
        
        return True
    
    def _determine_query_type(self, query: str) -> QueryType:
        """Determine query type for optimization"""
        query_lower = query.lower().strip()
        if query_lower.startswith('select'):
            return QueryType.SELECT
        elif query_lower.startswith('insert'):
            return QueryType.INSERT
        elif query_lower.startswith('update'):
            return QueryType.UPDATE
        elif query_lower.startswith('delete'):
            return QueryType.DELETE
        elif query_lower.startswith('create'):
            return QueryType.CREATE
        elif query_lower.startswith('drop'):
            return QueryType.DROP
        else:
            return QueryType.SELECT
    
    def batch_execute(self, queries: List[Tuple[str, Tuple]]) -> List[Tuple[bool, Any, Optional[str]]]:
        """Execute multiple queries in batch"""
        results = []
        for query, params in queries:
            success, result, error = self.execute_optimized_query(query, params)
            results.append((success, result, error))
        return results
    
    def optimize_database(self):
        """Run database optimization commands"""
        optimization_queries = [
            ("VACUUM", ()),
            ("ANALYZE", ()),
            ("PRAGMA optimize", ())
        ]
        
        print("🔧 Running database optimization...")
        for query, params in optimization_queries:
            success, result, error = self.connection_pool.execute_query(query, params)
            if success:
                print(f"✅ {query} completed")
            else:
                print(f"⚠️ {query} failed: {error}")
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get database optimization statistics"""
        pool_stats = self.connection_pool.get_pool_statistics()
        
        return {
            "database_path": self.database_path,
            "connection_pool": pool_stats,
            "query_cache_size": len(self._query_cache),
            "cache_timeout_seconds": self._cache_timeout
        }
    
    def cleanup(self):
        """Cleanup database optimizer"""
        self.connection_pool.cleanup()
        self._query_cache.clear()
        self._cache_ttl.clear()

def get_database_optimizer(database_path: str) -> DatabaseOptimizer:
    """Get database optimizer instance"""
    global _database_optimizers
    if '_database_optimizers' not in globals():
        _database_optimizers = {}
    
    if database_path not in _database_optimizers:
        _database_optimizers[database_path] = DatabaseOptimizer(database_path)
    
    return _database_optimizers[database_path]

@contextmanager
def database_transaction(optimizer: DatabaseOptimizer):
    """Context manager for database transactions"""
    connection = None
    try:
        connection = optimizer.connection_pool.get_connection()
        if not connection:
            raise Exception("No available database connections")
        
        connection.connection.execute("BEGIN TRANSACTION")
        yield connection.connection
        connection.connection.commit()
        
    except Exception as e:
        if connection:
            connection.connection.rollback()
        raise e
    finally:
        if connection:
            optimizer.connection_pool.return_connection(connection)

if __name__ == "__main__":
    # Test the database optimizer
    print("🗄️ Testing Database Optimizer")
    print("=" * 50)
    
    # Create test database
    test_db = "test_optimized.db"
    optimizer = get_database_optimizer(test_db)
    
    # Create test table
    create_table = """
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    success, result, error = optimizer.execute_optimized_query(create_table)
    print(f"Create table: {'✅' if success else '❌'} {error or 'Success'}")
    
    # Insert test data
    insert_data = "INSERT INTO test_table (name, value) VALUES (?, ?)"
    test_data = [("Item 1", 100), ("Item 2", 200), ("Item 3", 300)]
    
    for name, value in test_data:
        success, result, error = optimizer.execute_optimized_query(insert_data, (name, value))
        print(f"Insert {name}: {'✅' if success else '❌'}")
    
    # Query data (should be cached on second call)
    select_query = "SELECT * FROM test_table WHERE value > ?"
    
    # First call (cache miss)
    start = time.time()
    success, result, error = optimizer.execute_optimized_query(select_query, (150,))
    time1 = time.time() - start
    print(f"First query: {len(result) if success else 0} rows in {time1:.3f}s")
    
    # Second call (cache hit)
    start = time.time()
    success, result, error = optimizer.execute_optimized_query(select_query, (150,))
    time2 = time.time() - start
    print(f"Second query: {len(result) if success else 0} rows in {time2:.3f}s")
    print(f"Cache speedup: {time1/time2:.1f}x")
    
    # Show statistics
    stats = optimizer.get_optimization_statistics()
    print(f"Database statistics: {stats}")
    
    # Cleanup
    optimizer.cleanup()
    print("✅ Database optimizer test completed")
