"""
数据库性能基准测试

测试大数据量下的查询性能和索引效率
"""

import pytest
import random
from datetime import datetime, date, timedelta
from faker import Faker
from sqlalchemy import create_engine, text
from testcontainers.postgres import PostgresContainer
from alembic import command
from alembic.config import Config
import tempfile
from concurrent.futures import ThreadPoolExecutor
import time


fake = Faker()


class TestDatabasePerformance:
    """数据库性能测试套件"""
    
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
        """准备好的测试数据库（含表结构）"""
        engine = create_engine(test_database_url)
        
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

    def _generate_users(self, engine, count=1000):
        """生成测试用户数据"""
        users_data = []
        for i in range(count):
            users_data.append({
                'email': fake.unique.email(),
                'username': fake.unique.user_name(),
                'github_user_id': fake.random_int(min=1000, max=999999),
                'github_username': fake.unique.user_name(),
                'is_active': random.choice([True, False])
            })
        
        # 批量插入
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, username, github_user_id, github_username, is_active)
                VALUES (:email, :username, :github_user_id, :github_username, :is_active)
            """), users_data)
            conn.commit()
        
        return len(users_data)

    def _generate_daily_records(self, engine, user_count=1000, days=365):
        """生成用户日常记录数据"""
        # 获取用户ID
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM users LIMIT :limit"), {"limit": user_count})
            user_ids = [row[0] for row in result]
        
        records_data = []
        start_date = date.today() - timedelta(days=days)
        
        for user_id in user_ids:
            for day in range(days):
                record_date = start_date + timedelta(days=day)
                # 70%概率生成记录（模拟真实使用情况）
                if random.random() < 0.7:
                    records_data.append({
                        'user_id': user_id,
                        'record_date': record_date,
                        'sleep_start_time': fake.time_object(),
                        'sleep_end_time': fake.time_object(),
                        'sleep_quality': random.randint(1, 10),
                        'wake_clarity': random.randint(1, 10),
                        'calories': random.randint(1200, 3000),
                        'protein': random.randint(50, 200),
                        'overall_mood': random.randint(1, 10),
                        'stress_level': random.randint(1, 10),
                        'energy_level': random.randint(1, 10),
                        'deep_work_hours': round(random.uniform(0, 12), 1),
                        'focus_quality': random.randint(1, 10),
                    })
        
        # 分批插入（避免内存问题）
        batch_size = 1000
        with engine.connect() as conn:
            for i in range(0, len(records_data), batch_size):
                batch = records_data[i:i + batch_size]
                conn.execute(text("""
                    INSERT INTO user_daily_records (
                        user_id, record_date, sleep_start_time, sleep_end_time,
                        sleep_quality, wake_clarity, calories, protein,
                        overall_mood, stress_level, energy_level,
                        deep_work_hours, focus_quality
                    ) VALUES (
                        :user_id, :record_date, :sleep_start_time, :sleep_end_time,
                        :sleep_quality, :wake_clarity, :calories, :protein,
                        :overall_mood, :stress_level, :energy_level,
                        :deep_work_hours, :focus_quality
                    )
                """), batch)
                conn.commit()
        
        return len(records_data)

    @pytest.mark.benchmark
    def test_user_query_performance(self, benchmark, prepared_database):
        """测试用户查询性能"""
        # 生成测试数据
        user_count = self._generate_users(prepared_database, 5000)
        
        def query_users():
            with prepared_database.connect() as conn:
                result = conn.execute(text("""
                    SELECT u.username, u.email, u.github_username
                    FROM users u 
                    WHERE u.is_active = true 
                    ORDER BY u.created_at DESC 
                    LIMIT 100
                """))
                return list(result)
        
        # 基准测试
        results = benchmark(query_users)
        assert len(results) <= 100
        print(f"Generated {user_count} users, query returned {len(results)} active users")

    @pytest.mark.benchmark
    def test_daily_records_aggregation_performance(self, benchmark, prepared_database):
        """测试日常记录聚合查询性能"""
        # 生成测试数据
        user_count = self._generate_users(prepared_database, 1000)
        records_count = self._generate_daily_records(prepared_database, user_count, 180)  # 6个月数据
        
        def aggregate_query():
            with prepared_database.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        u.username,
                        COUNT(r.id) as record_count,
                        AVG(r.sleep_quality) as avg_sleep_quality,
                        AVG(r.overall_mood) as avg_mood,
                        AVG(r.stress_level) as avg_stress,
                        AVG(r.deep_work_hours) as avg_work_hours
                    FROM users u
                    LEFT JOIN user_daily_records r ON u.id = r.user_id
                    WHERE r.record_date >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY u.id, u.username
                    HAVING COUNT(r.id) > 0
                    ORDER BY avg_mood DESC
                    LIMIT 50
                """))
                return list(result)
        
        results = benchmark(aggregate_query)
        assert len(results) <= 50
        print(f"Generated {records_count} records, aggregation returned {len(results)} users")

    @pytest.mark.benchmark
    def test_large_dataset_query_performance(self, benchmark, prepared_database):
        """测试大数据集查询性能"""
        # 生成大量测试数据
        user_count = self._generate_users(prepared_database, 10000)
        records_count = self._generate_daily_records(prepared_database, 5000, 365)  # 1年数据
        
        def complex_query():
            with prepared_database.connect() as conn:
                result = conn.execute(text("""
                    WITH user_stats AS (
                        SELECT 
                            r.user_id,
                            AVG(r.sleep_quality) as avg_sleep,
                            AVG(r.overall_mood) as avg_mood,
                            AVG(r.stress_level) as avg_stress,
                            COUNT(*) as record_count
                        FROM user_daily_records r
                        WHERE r.record_date >= CURRENT_DATE - INTERVAL '90 days'
                        GROUP BY r.user_id
                        HAVING COUNT(*) >= 30
                    )
                    SELECT 
                        u.username,
                        u.email,
                        us.avg_sleep,
                        us.avg_mood,
                        us.avg_stress,
                        us.record_count,
                        CASE 
                            WHEN us.avg_mood >= 8 AND us.avg_sleep >= 7 THEN 'Excellent'
                            WHEN us.avg_mood >= 6 AND us.avg_sleep >= 6 THEN 'Good'
                            ELSE 'Needs Improvement'
                        END as wellness_score
                    FROM users u
                    JOIN user_stats us ON u.id = us.user_id
                    WHERE u.is_active = true
                    ORDER BY us.avg_mood DESC, us.avg_sleep DESC
                    LIMIT 100
                """))
                return list(result)
        
        results = benchmark(complex_query)
        assert len(results) <= 100
        print(f"Complex query on {user_count} users and {records_count} records returned {len(results)} results")

    @pytest.mark.benchmark
    def test_index_performance_verification(self, benchmark, prepared_database):
        """验证索引性能"""
        # 生成测试数据
        self._generate_users(prepared_database, 5000)
        self._generate_daily_records(prepared_database, 2000, 180)
        
        def indexed_query():
            with prepared_database.connect() as conn:
                # 这个查询应该使用索引
                result = conn.execute(text("""
                    SELECT r.* FROM user_daily_records r
                    WHERE r.record_date BETWEEN CURRENT_DATE - INTERVAL '7 days' AND CURRENT_DATE
                    ORDER BY r.record_date DESC, r.user_id
                """))
                return list(result)
        
        results = benchmark(indexed_query)
        
        # 验证查询计划使用了索引
        with prepared_database.connect() as conn:
            explain_result = conn.execute(text("""
                EXPLAIN (FORMAT JSON) 
                SELECT r.* FROM user_daily_records r
                WHERE r.record_date BETWEEN CURRENT_DATE - INTERVAL '7 days' AND CURRENT_DATE
                ORDER BY r.record_date DESC, r.user_id
            """))
            plan = explain_result.scalar()
            # 应该包含Index Scan或Index Only Scan
            assert 'Index' in str(plan), "Query should use index"

    def test_concurrent_read_performance(self, prepared_database):
        """测试并发读取性能"""
        # 生成测试数据
        self._generate_users(prepared_database, 2000)
        self._generate_daily_records(prepared_database, 1000, 90)
        
        def read_query(user_offset):
            with prepared_database.connect() as conn:
                result = conn.execute(text("""
                    SELECT u.username, COUNT(r.id) as record_count
                    FROM users u
                    LEFT JOIN user_daily_records r ON u.id = r.user_id
                    WHERE u.id BETWEEN :start_id AND :end_id
                    GROUP BY u.id, u.username
                    ORDER BY record_count DESC
                """), {"start_id": user_offset, "end_id": user_offset + 100})
                return len(list(result))
        
        # 并发执行查询
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_query, i * 100) for i in range(10)]
            results = [f.result() for f in futures]
        end_time = time.time()
        
        total_duration = end_time - start_time
        assert total_duration < 5.0, f"Concurrent queries took {total_duration:.2f}s, should be under 5s"
        assert all(result >= 0 for result in results), "All queries should return valid results"
        print(f"10 concurrent queries completed in {total_duration:.2f}s")

    def test_insert_performance(self, prepared_database):
        """测试批量插入性能"""
        # 生成用户数据
        self._generate_users(prepared_database, 1000)
        
        # 获取用户ID
        with prepared_database.connect() as conn:
            result = conn.execute(text("SELECT id FROM users"))
            user_ids = [row[0] for row in result]
        
        # 准备大量插入数据
        records_data = []
        for i in range(10000):  # 1万条记录
            records_data.append({
                'user_id': random.choice(user_ids),
                'record_date': fake.date_between(start_date='-30d', end_date='today'),
                'sleep_quality': random.randint(1, 10),
                'overall_mood': random.randint(1, 10),
                'stress_level': random.randint(1, 10),
            })
        
        # 测试批量插入性能
        start_time = time.time()
        batch_size = 500
        with prepared_database.connect() as conn:
            for i in range(0, len(records_data), batch_size):
                batch = records_data[i:i + batch_size]
                conn.execute(text("""
                    INSERT INTO user_daily_records (user_id, record_date, sleep_quality, overall_mood, stress_level)
                    VALUES (:user_id, :record_date, :sleep_quality, :overall_mood, :stress_level)
                    ON CONFLICT (user_id, record_date) DO NOTHING
                """), batch)
                conn.commit()
        end_time = time.time()
        
        insert_duration = end_time - start_time
        records_per_second = len(records_data) / insert_duration
        
        assert insert_duration < 30.0, f"Batch insert took {insert_duration:.2f}s, should be under 30s"
        assert records_per_second > 100, f"Insert rate {records_per_second:.0f} records/s is too slow"
        print(f"Inserted {len(records_data)} records in {insert_duration:.2f}s ({records_per_second:.0f} records/s)")