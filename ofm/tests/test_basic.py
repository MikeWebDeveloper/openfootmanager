"""Basic tests to validate the testing infrastructure works."""

import pytest


class TestBasicInfrastructure:
    """Test that basic testing infrastructure is working."""
    
    @pytest.mark.fast
    def test_imports_work(self):
        """Test that we can import core modules."""
        from ofm.core.db.models import League
        from ofm.core.football.club import Club
        from ofm.core.football.player import Player
        assert League is not None
        assert Club is not None
        assert Player is not None
    
    @pytest.mark.fast
    def test_pytest_works(self):
        """Test that pytest is working correctly."""
        assert True
        assert 1 + 1 == 2
    
    @pytest.mark.fast
    def test_markers_work(self):
        """Test that pytest markers are recognized."""
        # This test should run when using -m fast
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow tests are excluded with -m 'not slow'."""
        # This test should NOT run when using -m fast
        import time
        time.sleep(0.1)
        assert True