"""
数据库并发访问测试

测试多用户同时访问时的数据一致性和竞争条件处理
"""

import pytest
import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from testcontainers.postgres import PostgresContainer
from alembic import command
from alembic.config import Config
import tempfile
import threading


fake = Faker()


class TestDatabaseConcurrency:
    """数据库并发测试套件"""
    
    @pytest.fixture(scope="class")
    def postgres_container(self):
        """PostgreSQL测试容器"""
        with PostgresContainer("postgres:15-alpine") as postgres:
            yield postgres
    
    @pytest.fixture(scope="class")
    def test_database_url(self, postgres_container):
        """测试数据库URL"""
        return postgres_container.get_connection_url()
    
    @pytest.fixture(scope="class")
    def prepared_database(self, test_database_url):
        """准备好的测试数据库"""
        engine = create_engine(
            test_database_url,
            pool_size=20,  # 增加连接池大小支持并发测试
            max_overflow=30,
            pool_pre_ping=True
        )
        
        # 创建扩展
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            conn.commit()
        
        # 运行迁移
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(f"""
[alembic]
script_location = alembic
sqlalchemy.url = {test_database_url}
""")
            config_path = f.name
        
        config = Config(config_path)
        command.upgrade(config, "head")
        
        yield engine
        engine.dispose()

    def test_concurrent_user_creation(self, prepared_database):
        """测试并发用户创建"""
        created_users = []
        errors = []
        
        def create_user(worker_id):
            try:
                with prepared_database.connect() as conn:
                    email = f"user_{worker_id}_{fake.uuid4()}@example.com"
                    username = f"user_{worker_id}_{fake.uuid4()[:8]}"
                    github_user_id = fake.random_int(min=100000, max=999999)
                    
                    result = conn.execute(text("""
                        INSERT INTO users (email, username, github_user_id, github_username, is_active)
                        VALUES (:email, :username, :github_user_id, :github_username, true)
                        RETURNING id, email
                    """), {
                        "email": email,
                        "username": username, 
                        "github_user_id": github_user_id,
                        "github_username": username
                    })
                    conn.commit()
                    
                    user_data = result.fetchone()
                    return {"id": user_data[0], "email": user_data[1], "worker_id": worker_id}
            except Exception as e:
                return {"error": str(e), "worker_id": worker_id}
        
        # 并发创建100个用户
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_user, i) for i in range(100)]
            
            for future in as_completed(futures):
                result = future.result()
                if "error" in result:
                    errors.append(result)
                else:
                    created_users.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证结果
        assert len(errors) == 0, f"Concurrent user creation failed: {errors[:5]}"
        assert len(created_users) == 100, f"Expected 100 users, got {len(created_users)}"
        assert duration < 10.0, f"User creation took {duration:.2f}s, should be under 10s"
        
        # 验证数据库中的用户数量
        with prepared_database.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            assert user_count == 100, f"Database should have 100 users, found {user_count}"
        
        print(f"Successfully created {len(created_users)} users in {duration:.2f}s")

    def test_concurrent_daily_record_updates(self, prepared_database):
        """测试并发日常记录更新"""
        # 先创建测试用户
        with prepared_database.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, username, github_user_id, github_username, is_active)
                VALUES ('testuser@example.com', 'testuser', 123456, 'testuser', true)
            """))
            result = conn.execute(text("SELECT id FROM users WHERE email = 'testuser@example.com'"))
            user_id = result.scalar()
            conn.commit()
        
        record_date = date.today()
        update_results = []
        
        def update_daily_record(update_id):
            try:
                with prepared_database.connect() as conn:
                    # 尝试插入或更新记录
                    conn.execute(text("""
                        INSERT INTO user_daily_records (user_id, record_date, sleep_quality, overall_mood)
                        VALUES (:user_id, :record_date, :sleep_quality, :mood)
                        ON CONFLICT (user_id, record_date) 
                        DO UPDATE SET 
                            sleep_quality = EXCLUDED.sleep_quality,
                            overall_mood = EXCLUDED.overall_mood,
                            updated_at = CURRENT_TIMESTAMP
                    """), {
                        "user_id": user_id,
                        "record_date": record_date,
                        "sleep_quality": random.randint(1, 10),
                        "mood": random.randint(1, 10)
                    })
                    conn.commit()
                    return {"success": True, "update_id": update_id}
            except Exception as e:
                return {"error": str(e), "update_id": update_id}
        
        # 并发更新同一条记录
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(update_daily_record, i) for i in range(50)]
            
            for future in as_completed(futures):
                result = future.result()
                update_results.append(result)
        
        # 验证所有更新都成功
        errors = [r for r in update_results if "error" in r]
        successes = [r for r in update_results if "success" in r]
        
        assert len(errors) == 0, f"Concurrent updates failed: {errors[:3]}"
        assert len(successes) == 50, f"Expected 50 successful updates, got {len(successes)}"
        
        # 验证最终只有一条记录
        with prepared_database.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM user_daily_records 
                WHERE user_id = :user_id AND record_date = :record_date
            """), {"user_id": user_id, "record_date": record_date})
            record_count = result.scalar()
            assert record_count == 1, f"Should have exactly 1 record, found {record_count}"
        
        print(f"Successfully handled {len(successes)} concurrent updates to the same record")

    def test_deadlock_prevention(self, prepared_database):
        """测试死锁预防机制"""
        # 创建两个测试用户
        with prepared_database.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, username, github_user_id, github_username, is_active)
                VALUES 
                    ('user1@example.com', 'user1', 111111, 'user1', true),
                    ('user2@example.com', 'user2', 222222, 'user2', true)
            """))
            
            result = conn.execute(text("""
                SELECT id FROM users WHERE email IN ('user1@example.com', 'user2@example.com')
                ORDER BY email
            """))
            user_ids = [row[0] for row in result]
            conn.commit()
        
        user1_id, user2_id = user_ids
        completed_operations = []
        
        def cross_reference_operation(operation_id):
            """模拟可能导致死锁的交叉引用操作"""
            try:
                with prepared_database.connect() as conn:
                    if operation_id % 2 == 0:
                        # 操作序列A: 先更新user1再更新user2
                        conn.execute(text("""
                            INSERT INTO user_daily_records (user_id, record_date, sleep_quality)
                            VALUES (:user_id, :date, :quality)
                            ON CONFLICT (user_id, record_date) 
                            DO UPDATE SET sleep_quality = EXCLUDED.sleep_quality
                        """), {
                            "user_id": user1_id,
                            "date": date.today() - timedelta(days=operation_id % 10),
                            "quality": random.randint(1, 10)
                        })
                        
                        # 小延迟增加死锁概率
                        time.sleep(0.01)
                        
                        conn.execute(text("""
                            INSERT INTO user_daily_records (user_id, record_date, overall_mood)
                            VALUES (:user_id, :date, :mood)
                            ON CONFLICT (user_id, record_date) 
                            DO UPDATE SET overall_mood = EXCLUDED.overall_mood
                        """), {
                            "user_id": user2_id,
                            "date": date.today() - timedelta(days=operation_id % 10),
                            "mood": random.randint(1, 10)
                        })
                    else:
                        # 操作序列B: 先更新user2再更新user1
                        conn.execute(text("""
                            INSERT INTO user_daily_records (user_id, record_date, stress_level)
                            VALUES (:user_id, :date, :stress)
                            ON CONFLICT (user_id, record_date) 
                            DO UPDATE SET stress_level = EXCLUDED.stress_level
                        """), {
                            "user_id": user2_id,
                            "date": date.today() - timedelta(days=operation_id % 10),
                            "stress": random.randint(1, 10)
                        })
                        
                        time.sleep(0.01)
                        
                        conn.execute(text("""
                            INSERT INTO user_daily_records (user_id, record_date, energy_level)
                            VALUES (:user_id, :date, :energy)
                            ON CONFLICT (user_id, record_date) 
                            DO UPDATE SET energy_level = EXCLUDED.energy_level
                        """), {
                            "user_id": user1_id,
                            "date": date.today() - timedelta(days=operation_id % 10),
                            "energy": random.randint(1, 10)
                        })
                    
                    conn.commit()
                    return {"success": True, "operation_id": operation_id}
                    
            except Exception as e:
                error_msg = str(e)
                # 死锁应该被数据库检测并重试
                if "deadlock" in error_msg.lower():
                    return {"deadlock": True, "operation_id": operation_id}
                else:
                    return {"error": error_msg, "operation_id": operation_id}
        
        # 执行可能导致死锁的并发操作
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cross_reference_operation, i) for i in range(30)]
            
            for future in as_completed(futures):
                result = future.result()
                completed_operations.append(result)
        
        # 分析结果
        successes = [op for op in completed_operations if op.get("success")]
        deadlocks = [op for op in completed_operations if op.get("deadlock")]
        errors = [op for op in completed_operations if op.get("error")]
        
        # 大部分操作应该成功，少量死锁是可接受的
        assert len(successes) >= 25, f"Too many failed operations: {len(successes)} successes out of 30"
        assert len(deadlocks) <= 5, f"Too many deadlocks: {len(deadlocks)}"
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        
        print(f"Completed operations: {len(successes)} successes, {len(deadlocks)} deadlocks, {len(errors)} errors")

    def test_connection_pool_stress(self, prepared_database):
        """测试连接池压力测试"""
        def database_operation(operation_id):
            """执行数据库操作"""
            try:
                with prepared_database.connect() as conn:
                    # 模拟各种数据库操作
                    operations = [
                        # 读操作
                        lambda: conn.execute(text("SELECT COUNT(*) FROM users")).scalar(),
                        # 写操作  
                        lambda: conn.execute(text("""
                            INSERT INTO users (email, username, github_user_id, github_username, is_active)
                            VALUES (:email, :username, :github_id, :github_username, true)
                            ON CONFLICT (email) DO NOTHING
                        """), {
                            "email": f"stress_test_{operation_id}@example.com",
                            "username": f"stress_{operation_id}",
                            "github_id": 1000000 + operation_id,
                            "github_username": f"stress_{operation_id}"
                        }),
                        # 聚合查询
                        lambda: conn.execute(text("""
                            SELECT COUNT(*), AVG(CASE WHEN is_active THEN 1 ELSE 0 END)
                            FROM users
                        """)).fetchone()
                    ]
                    
                    # 随机执行操作
                    operation = random.choice(operations)
                    result = operation()
                    conn.commit()
                    
                    return {"success": True, "operation_id": operation_id}
                    
            except Exception as e:
                return {"error": str(e), "operation_id": operation_id}
        
        # 高并发压力测试
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:  # 高并发数
            futures = [executor.submit(database_operation, i) for i in range(200)]
            
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 分析结果
        successes = [r for r in results if r.get("success")]
        errors = [r for r in results if r.get("error")]
        
        success_rate = len(successes) / len(results) * 100
        
        assert success_rate >= 95, f"Success rate {success_rate:.1f}% too low, errors: {errors[:3]}"
        assert duration < 30.0, f"Stress test took {duration:.2f}s, should be under 30s"
        
        print(f"Connection pool stress test: {success_rate:.1f}% success rate, {duration:.2f}s duration")

    def test_transaction_isolation(self, prepared_database):
        """测试事务隔离级别"""
        # 创建测试用户
        with prepared_database.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, username, github_user_id, github_username, is_active)
                VALUES ('isolation_test@example.com', 'isolation_user', 999999, 'isolation_user', true)
            """))
            result = conn.execute(text("SELECT id FROM users WHERE email = 'isolation_test@example.com'"))
            user_id = result.scalar()
            conn.commit()
        
        record_date = date.today()
        isolation_results = []
        
        def transaction_operation(tx_id):
            """测试事务隔离的操作"""
            try:
                with prepared_database.connect() as conn:
                    # 开始事务
                    trans = conn.begin()
                    try:
                        # 读取当前值
                        result = conn.execute(text("""
                            SELECT sleep_quality FROM user_daily_records 
                            WHERE user_id = :user_id AND record_date = :date
                        """), {"user_id": user_id, "date": record_date})
                        
                        current_value = result.scalar()
                        if current_value is None:
                            # 插入新记录
                            conn.execute(text("""
                                INSERT INTO user_daily_records (user_id, record_date, sleep_quality)
                                VALUES (:user_id, :date, :quality)
                            """), {
                                "user_id": user_id,
                                "date": record_date,
                                "quality": tx_id % 10 + 1
                            })
                            new_value = tx_id % 10 + 1
                        else:
                            # 更新现有记录
                            new_value = (current_value + tx_id) % 10 + 1
                            conn.execute(text("""
                                UPDATE user_daily_records 
                                SET sleep_quality = :new_quality
                                WHERE user_id = :user_id AND record_date = :date
                            """), {
                                "new_quality": new_value,
                                "user_id": user_id,
                                "date": record_date
                            })
                        
                        # 小延迟模拟处理时间
                        time.sleep(0.05)
                        
                        trans.commit()
                        return {"success": True, "tx_id": tx_id, "final_value": new_value}
                        
                    except Exception as e:
                        trans.rollback()
                        raise e
                        
            except Exception as e:
                return {"error": str(e), "tx_id": tx_id}
        
        # 并发执行事务
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(transaction_operation, i) for i in range(20)]
            
            for future in as_completed(futures):
                result = future.result()
                isolation_results.append(result)
        
        # 验证事务隔离性
        successes = [r for r in isolation_results if r.get("success")]
        errors = [r for r in isolation_results if r.get("error")]
        
        assert len(errors) == 0, f"Transaction isolation test failed: {errors}"
        assert len(successes) == 20, f"Expected 20 successful transactions, got {len(successes)}"
        
        # 验证最终数据一致性
        with prepared_database.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM user_daily_records 
                WHERE user_id = :user_id AND record_date = :date
            """), {"user_id": user_id, "date": record_date})
            final_count = result.scalar()
            
            assert final_count == 1, f"Should have exactly 1 record after all transactions, found {final_count}"
        
        print(f"Transaction isolation test: {len(successes)} successful transactions, final consistency verified")