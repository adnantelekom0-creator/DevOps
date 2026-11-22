from app import add, get_status


def test_add():
    assert add(10, 20) == 30
    assert add(-5, 5) == 0


def test_get_status():
    status = get_status()
    assert status["status"] == "HEALTHY"
    assert "version" in status
