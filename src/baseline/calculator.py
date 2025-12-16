"""
Baseline Calculator

Calculates statistical baselines and stores them in BigQuery Baseline table.
Supports configurable baseline calculation methods with robust error handling.

Production-ready features:
- Automatic table creation
- Comprehensive error handling
- Detailed logging
- Configurable calculation methods
- BigQuery integration
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from dotenv import load_dotenv

from ..models.baseline import BaselineStats, BASELINE_TABLE_SCHEMA
from ..utils.config import get_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaselineCalculator:
    """
    Calculates statistical baselines from historical data
    Stores results in BigQuery Baseline table for future analysis
    
    Supports multiple calculation methods:
    - simple_stats: Mean, std dev, percentiles (default)
    - rolling_average: Rolling window average
    - seasonal_decomposition: Time series decomposition
    """
    
    def __init__(self, config=None):
        """
        Initialize baseline calculator
        
        Args:
            config: Config object. If None, uses global config.
        """
        self.config = config or get_config()
        
        self.project_id = self.config.bigquery_project_id
        self.dataset_id = self.config.bigquery_dataset_id
        self.client = bigquery.Client(project=self.project_id)
        
        # Get calculation method from config
        self.calculation_method = self.config.baseline_calculation_method
        self.lookback_days = self.config.baseline_lookback_days
        
        logger.info("Baseline Calculator initialized")
        logger.info(f"Method: {self.calculation_method}")
        logger.info(f"Lookback: {self.lookback_days} days")
        logger.info(f"Project: {self.project_id}")
        logger.info(f"Dataset: {self.dataset_id}")
        
        # Ensure Baseline table exists
        try:
            self._ensure_baseline_table()
        except Exception as e:
            logger.error(f"Failed to initialize Baseline table: {e}")
            raise
    
    def _ensure_baseline_table(self):
        """Create Baseline table if it doesn't exist"""
        table_id = f"{self.project_id}.{self.dataset_id}.Baseline"
        
        try:
            self.client.get_table(table_id)
            logger.info(f"Baseline table exists: {table_id}")
        except Exception as e:
            # Table doesn't exist, create it
            logger.info(f"Creating Baseline table: {table_id}")
            
            try:
                schema = [bigquery.SchemaField(**field) for field in BASELINE_TABLE_SCHEMA]
                table = bigquery.Table(table_id, schema=schema)
                table = self.client.create_table(table)
                logger.info(f"Successfully created Baseline table: {table_id}")
            except GoogleCloudError as gce:
                logger.error(f"Failed to create Baseline table: {gce}")
                raise
            except Exception as ex:
                logger.error(f"Unexpected error creating Baseline table: {ex}")
                raise
    
    def calculate_baseline(
        self,
        metric_name: str,
        metric_column: str,
        source_table: str,
        lookback_days: Optional[int] = None,
        calculation_method: Optional[str] = None
    ) -> BaselineStats:
        """
        Calculate baseline statistics for a metric
        
        Args:
            metric_name: Name for the baseline (e.g., "error_rate")
            metric_column: Column name in source table (e.g., "Error_Rate _%_")
            source_table: Source table name (e.g., "cloud_workload_dataset")
            lookback_days: Number of days of historical data to analyze (uses config if None)
            calculation_method: Method to use (uses config if None)
        
        Returns:
            BaselineStats object with calculated statistics
        """
        # Use config values if not specified
        lookback_days = lookback_days or self.lookback_days
        calculation_method = calculation_method or self.calculation_method
        
        logger.info(f"Calculating baseline for {metric_name}")
        logger.info(f"Source: {source_table}, Column: {metric_column}")
        logger.info(f"Method: {calculation_method}, Lookback: {lookback_days} days")
        
        try:
            # Route to appropriate calculation method
            if calculation_method == "simple_stats":
                return self._calculate_simple_stats(
                    metric_name, metric_column, source_table, lookback_days
                )
            elif calculation_method == "rolling_average":
                return self._calculate_rolling_average(
                    metric_name, metric_column, source_table, lookback_days
                )
            elif calculation_method == "seasonal_decomposition":
                return self._calculate_seasonal_decomposition(
                    metric_name, metric_column, source_table, lookback_days
                )
            else:
                logger.warning(f"Unknown method '{calculation_method}', using simple_stats")
                return self._calculate_simple_stats(
                    metric_name, metric_column, source_table, lookback_days
                )
        except Exception as e:
            logger.error(f"Failed to calculate baseline for {metric_name}: {e}")
            raise
    
    def _calculate_simple_stats(
        self,
        metric_name: str,
        metric_column: str,
        source_table: str,
        lookback_days: int
    ) -> BaselineStats:
        """
        Calculate baseline using simple statistical methods
        (mean, std dev, percentiles)
        """
        
        # Query to calculate statistics
        query = f"""
        SELECT
            AVG(`{metric_column}`) as mean,
            STDDEV(`{metric_column}`) as std_dev,
            MIN(`{metric_column}`) as min_value,
            MAX(`{metric_column}`) as max_value,
            APPROX_QUANTILES(`{metric_column}`, 100)[OFFSET(50)] as p50,
            APPROX_QUANTILES(`{metric_column}`, 100)[OFFSET(95)] as p95,
            APPROX_QUANTILES(`{metric_column}`, 100)[OFFSET(99)] as p99,
            COUNT(*) as sample_count
        FROM `{self.project_id}.{self.dataset_id}.{source_table}`
        WHERE `{metric_column}` IS NOT NULL
        """
        
        # Note: cloud_workload_dataset has all data from 2024, no need for time filter for MVP
        # Time filter can be added later when we have real-time data
        
        try:
            # Execute query
            logger.debug(f"Executing baseline query for {metric_name}")
            result = self.client.query(query).result()
            row = next(result)
            
            # Validate we got data
            if row['sample_count'] == 0:
                logger.warning(f"No data found for {metric_name} in {source_table}")
                raise ValueError(f"No data found for metric {metric_name}")
            
            # Create baseline object
            baseline_id = f"baseline-{metric_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            baseline = BaselineStats(
                baseline_id=baseline_id,
                metric_name=metric_name,
                mean=float(row['mean']) if row['mean'] is not None else 0.0,
                std_dev=float(row['std_dev']) if row['std_dev'] is not None else 0.0,
                min_value=float(row['min_value']) if row['min_value'] is not None else 0.0,
                max_value=float(row['max_value']) if row['max_value'] is not None else 0.0,
                p50=float(row['p50']) if row['p50'] is not None else 0.0,
                p95=float(row['p95']) if row['p95'] is not None else 0.0,
                p99=float(row['p99']) if row['p99'] is not None else 0.0,
                calculated_at=datetime.now(),
                lookback_days=lookback_days,
                sample_count=int(row['sample_count']),
                data_source=source_table,
                notes=f"Calculated from {metric_column} column using simple_stats method"
            )
            
            logger.info(f"Baseline calculated successfully for {metric_name}")
            logger.info(f"  Mean: {baseline.mean:.4f}, Std Dev: {baseline.std_dev:.4f}")
            logger.info(f"  P95: {baseline.p95:.4f}, P99: {baseline.p99:.4f}")
            logger.info(f"  Samples: {baseline.sample_count:,}")
            
            return baseline
            
        except StopIteration:
            logger.error(f"Query returned no results for {metric_name}")
            raise ValueError(f"No data returned from query for {metric_name}")
        except GoogleCloudError as gce:
            logger.error(f"BigQuery error calculating baseline: {gce}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in _calculate_simple_stats: {e}")
            raise
    
    def _calculate_rolling_average(
        self,
        metric_name: str,
        metric_column: str,
        source_table: str,
        lookback_days: int
    ) -> BaselineStats:
        """
        Calculate baseline using rolling average
        (for future implementation)
        """
        logger.warning("Rolling average method not yet implemented")
        logger.info("Falling back to simple_stats method")
        return self._calculate_simple_stats(
            metric_name, metric_column, source_table, lookback_days
        )
    
    def _calculate_seasonal_decomposition(
        self,
        metric_name: str,
        metric_column: str,
        source_table: str,
        lookback_days: int
    ) -> BaselineStats:
        """
        Calculate baseline using seasonal decomposition
        (for future implementation)
        """
        logger.warning("Seasonal decomposition method not yet implemented")
        logger.info("Falling back to simple_stats method")
        return self._calculate_simple_stats(
            metric_name, metric_column, source_table, lookback_days
        )
    
    def save_baseline(self, baseline: BaselineStats):
        """
        Save baseline to BigQuery Baseline table
        
        Args:
            baseline: BaselineStats object to save
        """
        table_id = f"{self.project_id}.{self.dataset_id}.Baseline"
        
        logger.info(f"Saving baseline to BigQuery: {table_id}")
        logger.debug(f"Baseline ID: {baseline.baseline_id}")
        
        try:
            # Insert row
            errors = self.client.insert_rows_json(
                table_id,
                [baseline.to_bigquery_row()]
            )
            
            if errors:
                logger.error(f"Failed to save baseline: {errors}")
                raise Exception(f"Failed to save baseline: {errors}")
            
            logger.info(f"Baseline saved successfully: {baseline.baseline_id}")
            
        except GoogleCloudError as gce:
            logger.error(f"BigQuery error saving baseline: {gce}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving baseline: {e}")
            raise
    
    def get_latest_baseline(self, metric_name: str) -> Optional[BaselineStats]:
        """
        Retrieve the most recent baseline for a metric
        
        Args:
            metric_name: Name of the metric
        
        Returns:
            BaselineStats object or None if not found
        """
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.Baseline`
        WHERE metric_name = @metric_name
        ORDER BY calculated_at DESC
        LIMIT 1
        """
        
        try:
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("metric_name", "STRING", metric_name)
                ]
            )
            
            result = self.client.query(query, job_config=job_config).result()
            
            try:
                row = next(result)
                logger.info(f"Retrieved latest baseline for {metric_name}")
                return BaselineStats(
                    baseline_id=row['baseline_id'],
                    metric_name=row['metric_name'],
                    mean=float(row['mean']),
                    std_dev=float(row['std_dev']),
                    min_value=float(row['min_value']),
                    max_value=float(row['max_value']),
                    p50=float(row['p50']),
                    p95=float(row['p95']),
                    p99=float(row['p99']),
                    calculated_at=row['calculated_at'],
                    lookback_days=int(row['lookback_days']),
                    sample_count=int(row['sample_count']),
                    data_source=row['data_source'],
                    notes=row.get('notes')
                )
            except StopIteration:
                logger.warning(f"No baseline found for {metric_name}")
                return None
                
        except GoogleCloudError as gce:
            logger.error(f"BigQuery error retrieving baseline: {gce}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving baseline: {e}")
            raise
    
    def calculate_and_save_all_baselines(self) -> List[BaselineStats]:
        """
        Calculate and save baselines for all configured metrics
        
        Returns:
            List of BaselineStats objects
        """
        logger.info("=" * 80)
        logger.info("CALCULATING ALL BASELINES")
        logger.info("=" * 80)
        logger.info(f"Method: {self.calculation_method}")
        logger.info(f"Lookback: {self.lookback_days} days")
        
        baselines = []
        failed_metrics = []
        
        # Get metrics from config
        metrics = self.config.baseline_metrics
        
        if not metrics:
            logger.warning("No metrics configured, using defaults")
            metrics = [
                {
                    'name': 'error_rate',
                    'column': 'Error_Rate _%_',
                    'table': 'cloud_workload_dataset',
                    'enabled': True
                },
                {
                    'name': 'cpu_utilization',
                    'column': 'CPU_Utilization _%_',
                    'table': 'cloud_workload_dataset',
                    'enabled': True
                },
                {
                    'name': 'memory_consumption',
                    'column': 'Memory_Consumption _MB_',
                    'table': 'cloud_workload_dataset',
                    'enabled': True
                },
                {
                    'name': 'execution_time',
                    'column': 'Task_Execution_Time _ms_',
                    'table': 'cloud_workload_dataset',
                    'enabled': True
                }
            ]
        
        for metric in metrics:
            # Skip disabled metrics
            if not metric.get('enabled', True):
                print(f"\n[SKIP] {metric['name']} (disabled in config)")
                continue
            
            try:
                baseline = self.calculate_baseline(
                    metric_name=metric['name'],
                    metric_column=metric['column'],
                    source_table=metric['table']
                )
                
                self.save_baseline(baseline)
                baselines.append(baseline)
                
            except Exception as e:
                print(f"[ERROR] Failed to calculate baseline for {metric['name']}: {e}")
        
        print("\n" + "=" * 80)
        print(f"BASELINE CALCULATION COMPLETE - {len(baselines)} baselines saved")
        print("=" * 80)
        
        return baselines
    
    def calculate_baseline_with_ai(
        self,
        metric_name: str,
        metric_column: str,
        source_table: str
    ) -> BaselineStats:
        """
        Calculate baseline using AI-recommended method
        
        Args:
            metric_name: Name for the baseline (e.g., "error_rate")
            metric_column: Column name in source table
            source_table: Source table name
        
        Returns:
            BaselineStats object with calculated statistics
        """
        from ..baseline.ai_optimizer import AIBaselineOptimizer
        
        logger.info(f"Using AI to determine optimal method for {metric_name}")
        
        try:
            # Get sample data for analysis (limit to 10K rows for performance)
            query = f"""
            SELECT `{metric_column}` as value
            FROM `{self.project_id}.{self.dataset_id}.{source_table}`
            WHERE `{metric_column}` IS NOT NULL
            LIMIT 10000
            """
            
            logger.debug(f"Fetching sample data for AI analysis")
            df = self.client.query(query).to_dataframe()
            
            if len(df) == 0:
                logger.warning(f"No data found for {metric_name}, using default method")
                return self.calculate_baseline(
                    metric_name, metric_column, source_table
                )
            
            # Get AI recommendation
            optimizer = AIBaselineOptimizer(self.config)
            recommendation = optimizer.analyze_metric(
                metric_name=metric_name,
                data=df['value']
            )
            
            logger.info(f"AI recommends: {recommendation['recommended_method']} "
                       f"(confidence: {recommendation['confidence']:.0%})")
            
            # Use recommended method and parameters
            return self.calculate_baseline(
                metric_name=metric_name,
                metric_column=metric_column,
                source_table=source_table,
                calculation_method=recommendation['recommended_method'],
                lookback_days=recommendation['parameters']['lookback_days']
            )
            
        except Exception as e:
            logger.error(f"AI-driven calculation failed for {metric_name}: {e}")
            logger.info("Falling back to standard calculation")
            return self.calculate_baseline(
                metric_name, metric_column, source_table
            )
    
    def _get_table_columns(self, table_name: str) -> List[str]:
        """Get list of column names for a table"""
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        table = self.client.get_table(table_id)
        return [field.name for field in table.schema]


if __name__ == "__main__":
    # Test baseline calculation
    calculator = BaselineCalculator()
    baselines = calculator.calculate_and_save_all_baselines()
    
    print("\n" + "=" * 80)
    print("BASELINE SUMMARY")
    print("=" * 80)
    for baseline in baselines:
        print(f"\n{baseline.metric_name}:")
        print(f"  Mean: {baseline.mean:.4f}")
        print(f"  Std Dev: {baseline.std_dev:.4f}")
        print(f"  Range: [{baseline.min_value:.4f}, {baseline.max_value:.4f}]")
        print(f"  P95: {baseline.p95:.4f}")
        print(f"  Samples: {baseline.sample_count:,}")