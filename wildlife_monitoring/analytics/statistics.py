"""
Statistics Calculator Module

Statistical computations for wildlife monitoring data.
"""

import numpy as np
from typing import List, Dict, Any
from scipy import stats


class StatisticsCalculator:
    """
    Calculates statistical metrics for wildlife monitoring data.
    """
    
    @staticmethod
    def calculate_basic_stats(data: List[float]) -> Dict[str, float]:
        """
        Calculate basic statistical metrics.
        
        Args:
            data: List of numerical values
            
        Returns:
            Dictionary with statistical metrics
        """
        if not data:
            return {
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0
            }
        
        arr = np.array(data)
        
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "count": len(data)
        }
    
    @staticmethod
    def calculate_percentiles(
        data: List[float],
        percentiles: List[int] = [25, 50, 75, 90, 95]
    ) -> Dict[int, float]:
        """
        Calculate percentiles for data.
        
        Args:
            data: List of numerical values
            percentiles: List of percentile values to calculate
            
        Returns:
            Dictionary mapping percentile to value
        """
        if not data:
            return {p: 0.0 for p in percentiles}
        
        arr = np.array(data)
        
        return {
            p: float(np.percentile(arr, p))
            for p in percentiles
        }
    
    @staticmethod
    def calculate_moving_average(
        data: List[float],
        window_size: int = 5
    ) -> List[float]:
        """
        Calculate moving average.
        
        Args:
            data: List of numerical values
            window_size: Size of moving window
            
        Returns:
            List of moving average values
        """
        if len(data) < window_size:
            return data
        
        arr = np.array(data)
        weights = np.ones(window_size) / window_size
        
        return np.convolve(arr, weights, mode='valid').tolist()
    
    @staticmethod
    def detect_outliers(
        data: List[float],
        threshold: float = 3.0
    ) -> List[int]:
        """
        Detect outliers using z-score method.
        
        Args:
            data: List of numerical values
            threshold: Z-score threshold for outliers
            
        Returns:
            List of indices of outliers
        """
        if len(data) < 3:
            return []
        
        arr = np.array(data)
        z_scores = np.abs(stats.zscore(arr))
        
        outlier_indices = np.where(z_scores > threshold)[0].tolist()
        
        return outlier_indices
    
    @staticmethod
    def calculate_correlation(
        data1: List[float],
        data2: List[float]
    ) -> float:
        """
        Calculate Pearson correlation coefficient.
        
        Args:
            data1: First data series
            data2: Second data series
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        if len(data1) != len(data2) or len(data1) < 2:
            return 0.0
        
        correlation, _ = stats.pearsonr(data1, data2)
        
        return float(correlation)
    
    @staticmethod
    def calculate_rate_of_change(
        data: List[float],
        time_intervals: List[float] = None
    ) -> List[float]:
        """
        Calculate rate of change between consecutive data points.
        
        Args:
            data: List of numerical values
            time_intervals: Optional time intervals between points
            
        Returns:
            List of rate of change values
        """
        if len(data) < 2:
            return []
        
        arr = np.array(data)
        
        if time_intervals is None:
            # Assume uniform intervals
            rates = np.diff(arr).tolist()
        else:
            # Use provided time intervals
            time_arr = np.array(time_intervals)
            rates = (np.diff(arr) / np.diff(time_arr)).tolist()
        
        return rates
    
    @staticmethod
    def calculate_distribution_fit(
        data: List[float]
    ) -> Dict[str, Any]:
        """
        Fit data to normal distribution and return parameters.
        
        Args:
            data: List of numerical values
            
        Returns:
            Dictionary with distribution parameters
        """
        if len(data) < 3:
            return {
                "distribution": "normal",
                "mean": 0.0,
                "std": 0.0,
                "fit_quality": 0.0
            }
        
        arr = np.array(data)
        
        # Fit to normal distribution
        mean, std = stats.norm.fit(arr)
        
        # Kolmogorov-Smirnov test for goodness of fit
        ks_statistic, p_value = stats.kstest(arr, 'norm', args=(mean, std))
        
        return {
            "distribution": "normal",
            "mean": float(mean),
            "std": float(std),
            "ks_statistic": float(ks_statistic),
            "p_value": float(p_value),
            "fit_quality": float(1 - ks_statistic)  # Higher is better
        }
