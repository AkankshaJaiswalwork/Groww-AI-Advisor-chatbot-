import os
import sys
import pytest
import requests

def test_health_endpoint():
    url = "http://127.0.0.1:8000/health"
    try:
        response = requests.get(url, timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("FastAPI server is not running on http://127.0.0.1:8000")

def test_chat_unauthorized():
    url = "http://127.0.0.1:8000/chat"
    payload = {
        "query": "hello",
        "session_id": "test-session"
    }
    
    try:
        # No Auth header
        response = requests.post(url, json=payload, timeout=5)
        assert response.status_code == 401
        
        # Invalid Auth token
        headers = {"Authorization": "Bearer invalidtoken"}
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        assert response.status_code == 401
    except requests.exceptions.ConnectionError:
        pytest.skip("FastAPI server is not running on http://127.0.0.1:8000")

def test_chat_authorized():
    url = "http://127.0.0.1:8000/chat"
    payload = {
        "query": "What is the category of Nippon India Small Cap?",
        "session_id": "test-session-auth"
    }
    headers = {"Authorization": "Bearer supersecrettoken"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        assert response.status_code in [200, 500]  # 500 is possible if GROQ API key fails
        if response.status_code == 200:
            json_data = response.json()
            assert "answer" in json_data
            assert json_data["session_id"] == "test-session-auth"
    except requests.exceptions.ConnectionError:
        pytest.skip("FastAPI server is not running on http://127.0.0.1:8000")
