import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from micro.bucket_enrich import BucketEnrichMicroFunction


class TestAsyncLatency:
    """Test suite for verifying async parallel execution performance."""
    
    def test_parallel_vs_serial_latency(self):
        """Test that parallel execution is faster than serial execution."""
        
        # Mock the individual enrichment functions to simulate network delays
        with patch.object(BucketEnrichMicroFunction, 'stack_enrich') as mock_stack, \
             patch.object(BucketEnrichMicroFunction, 'biz_enrich') as mock_biz, \
             patch.object(BucketEnrichMicroFunction, 'comp_enrich') as mock_comp, \
             patch.object(BucketEnrichMicroFunction, 'culture_enrich') as mock_culture, \
             patch.object(BucketEnrichMicroFunction, 'manager_enrich') as mock_manager:
            
            # Mock each function to sleep for 0.5 seconds (simulating network delay)
            def mock_sleep_and_return(sleep_time: float, return_value: dict):
                def side_effect(*args, **kwargs):
                    time.sleep(sleep_time)
                    return return_value
                return side_effect
            
            mock_stack.side_effect = mock_sleep_and_return(0.5, {"stack": "Python"})
            mock_biz.side_effect = mock_sleep_and_return(0.5, {"news": "Growing"})
            mock_comp.side_effect = mock_sleep_and_return(0.5, {"salary": "$120k"})
            mock_culture.side_effect = mock_sleep_and_return(0.5, {"culture": "Remote"})
            mock_manager.side_effect = mock_sleep_and_return(0.5, {"manager": "John"})
            
            # Test data
            test_data = {
                "enriched": {
                    "company": "TestCorp",
                    "location": "San Francisco, CA"
                },
                "raw_input": "https://linkedin.com/jobs/test-job"
            }
            
            enrich_func = BucketEnrichMicroFunction()
            
            # Measure parallel execution time
            start_time = time.time()
            result = enrich_func.run(test_data)
            parallel_time = time.time() - start_time
            
            # Verify result structure
            assert "bucket_facts" in result
            assert len(result["bucket_facts"]) > 0
            
            # Expected serial time would be ~2.5 seconds (5 * 0.5)
            # Parallel time should be ~0.5 seconds (max of parallel tasks)
            expected_serial_time = 2.5
            max_acceptable_parallel_time = 1.0  # Give some buffer for overhead
            
            assert parallel_time < max_acceptable_parallel_time, \
                f"Parallel execution took {parallel_time:.2f}s, expected < {max_acceptable_parallel_time}s"
            
            # Verify it's significantly faster than serial would be
            speedup = expected_serial_time / parallel_time
            assert speedup > 2.0, \
                f"Speedup of {speedup:.2f}x is less than expected minimum of 2.0x"
    
    def test_async_gather_functionality(self):
        """Test that asyncio.gather works correctly with our async wrapper functions."""
        
        enrich_func = BucketEnrichMicroFunction()
        
        # Mock the sync functions to return known values
        with patch.object(enrich_func, 'stack_enrich', return_value={"stack": "Python"}), \
             patch.object(enrich_func, 'biz_enrich', return_value={"news": "Growing"}), \
             patch.object(enrich_func, 'comp_enrich', return_value={"salary": "$120k"}), \
             patch.object(enrich_func, 'culture_enrich', return_value={"culture": "Remote"}):
            
            # Test the async wrapper directly
            result = asyncio.run(enrich_func._async_enrich_all(
                company="TestCorp",
                location="San Francisco, CA",
                raw_input="normal job posting"
            ))
            
            # Verify all results are merged correctly
            expected_facts = {
                "stack": "Python",
                "news": "Growing", 
                "salary": "$120k",
                "culture": "Remote"
            }
            
            for key, value in expected_facts.items():
                assert key in result
                assert result[key] == value
    
    def test_async_exception_handling(self):
        """Test that exceptions in async tasks are handled gracefully."""
        
        enrich_func = BucketEnrichMicroFunction()
        
        # Mock some functions to raise exceptions
        with patch.object(enrich_func, 'stack_enrich', side_effect=Exception("Network error")), \
             patch.object(enrich_func, 'biz_enrich', return_value={"news": "Growing"}), \
             patch.object(enrich_func, 'comp_enrich', return_value={"salary": "$120k"}), \
             patch.object(enrich_func, 'culture_enrich', return_value={"culture": "Remote"}):
            
            # Should not raise exception, but should handle it gracefully
            result = asyncio.run(enrich_func._async_enrich_all(
                company="TestCorp",
                location="San Francisco, CA", 
                raw_input="normal job posting"
            ))
            
            # Should still get results from non-failing functions
            assert "news" in result
            assert "salary" in result
            assert "culture" in result
            
            # The failing function should not contribute to results
            assert "stack" not in result
    
    def test_parallel_execution_with_timeouts(self):
        """Test that parallel execution respects timeout constraints."""
        
        # Mock functions with different execution times
        def create_timeout_mock(delay: float, return_value: dict):
            def side_effect(*args, **kwargs):
                time.sleep(delay)
                return return_value
            return side_effect
        
        with patch.object(BucketEnrichMicroFunction, 'stack_enrich') as mock_stack, \
             patch.object(BucketEnrichMicroFunction, 'biz_enrich') as mock_biz, \
             patch.object(BucketEnrichMicroFunction, 'comp_enrich') as mock_comp, \
             patch.object(BucketEnrichMicroFunction, 'culture_enrich') as mock_culture:
            
            # Set up different delays
            mock_stack.side_effect = create_timeout_mock(0.2, {"stack": "Python"})
            mock_biz.side_effect = create_timeout_mock(0.3, {"news": "Growing"})
            mock_comp.side_effect = create_timeout_mock(0.4, {"salary": "$120k"})
            mock_culture.side_effect = create_timeout_mock(0.1, {"culture": "Remote"})
            
            test_data = {
                "enriched": {
                    "company": "TestCorp",
                    "location": "San Francisco, CA"
                },
                "raw_input": "normal job posting"
            }
            
            enrich_func = BucketEnrichMicroFunction()
            
            start_time = time.time()
            result = enrich_func.run(test_data)
            total_time = time.time() - start_time
            
            # Total time should be close to the longest task (0.4s) rather than sum (1.0s)
            assert total_time < 0.7, f"Execution took {total_time:.2f}s, expected < 0.7s"
            assert total_time > 0.3, f"Execution took {total_time:.2f}s, expected > 0.3s"
            
            # Verify all results are present
            facts = result["bucket_facts"]
            assert "stack" in facts
            assert "news" in facts
            assert "salary" in facts
            assert "culture" in facts 